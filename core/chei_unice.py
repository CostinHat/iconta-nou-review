# -*- coding: utf-8 -*-
"""CHEIA NATURALĂ DUBLATĂ — refuzul bazei devine refuzul numit al aplicației, nu un `500`.

[lotul 10, deficiența C73] `POST /tenants/{id}/clienti` cu un CUI deja existent cădea cu **500**:
*„psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "clienti_cui_uniq"
DETAIL: Key (cui)=(RO24736200) already exists.”* Constrângerea apăra datele corect (GARZI cat.1,
`core/migrare_intrare_date_garduri.py`), dar refuzul ei nu ajungea la contabil: excepția bazei ieșea
neprinsă din use-case. Aceeași clasă cu R164 (`salariati_api.creeaza_salariat`, CNP dublat), care
o rezolvase local, cu un `except` propriu — de-aia aici e UN singur mecanism, nu câte o copie pe tabel.

CUM SE FOLOSEȘTE:

    with chei_unice.refuza_dublura(cur, ("clienti_cui_uniq",), _refuz_cui):
        cur.execute("INSERT INTO clienti ... RETURNING id", ...)
        client_id = cur.fetchone()[0]       # citit ÎNĂUNTRU: `RELEASE SAVEPOINT` golește cursorul

`refuz(cur, e)` e chemat DUPĂ `ROLLBACK TO SAVEPOINT`, deci tranzacția e din nou utilizabilă și poate
citi ce există deja (clientul cu acel CUI, mijlocul fix cu acel cod) — refuzul numește lucrul existent,
nu doar valoarea. Întoarce excepția de ridicat (de obicei `CheieDublata`; `salariati_api` întoarce
eroarea lui pe câmp). O violare a ALTEI constrângeri decât cele numite nu se traduce: se re-ridică
neatinsă — nu inventăm un refuz pentru o cheie pe care apelantul n-a declarat-o.

Numele savepoint-ului e literal (ca în `core/tranzactie.py`: niciun nume interpolat într-un SQL).
`refuz` poate întoarce `None` (n-a găsit lucrul existent): atunci excepția bazei se re-ridică neatinsă.

Când numărul îl dă APLICAȚIA (`MAX + 1`: registratura, registrele art.321, inventarul, exemplarul artefactului), cursa nu se
refuză — se reia cu numărul următor: `reincearca_la_dublura` (același savepoint, aceeași listă de constrângeri).

Gard: `core/test_lot10_c73_chei_unice.py` — catalogul TUTUROR cheilor unice din `tenant_template.sql` (CONSTRAINT … UNIQUE și
CREATE UNIQUE INDEX); fiecare scriere din cod pe una din ele tratează dublura (aici / ON CONFLICT / la apelant) ori e excepție cu motiv.
"""
import contextlib
import re

import psycopg2


class CheieDublata(ValueError):
    """Refuzul numit al unei chei naturale dublate. E `ValueError`, deci orice use-case care traducea deja
    `ValueError` în `DateInvalide` (importurile) îl întoarce la fel, ca text; cine vrea să dea și drumul
    spre lucrul existent (clientul) folosește `detaliu()`."""

    def __init__(self, mesaj, valoare=None, existent=None, camp=None):
        super().__init__(mesaj)
        self.valoare = valoare
        self.existent = existent      # ce există deja cu acea cheie (ex. {"client_id": 7, "nume": "ALFA SRL"})
        self.camp = camp              # câmpul formularului pe care stă cheia, dacă ecranul îl are

    def detaliu(self):
        """Corpul refuzului pentru stratul HTTP: `mesaj` (ce citește ecranul), valoarea dublată, lucrul existent și, cu câmp,
        `erori_campuri` (forma G10 pe care `api.js` o pune lângă câmp)."""
        # `ok: False` — rezultatul unei scrieri refuzate (vocabularul `{ok, cod}` al operațiilor; `scan_afirmatii.OPERATIE_CHEI`)
        d = {"ok": False, "mesaj": str(self), "cod": "CHEIE_DUBLATA", "valoare": self.valoare}
        if self.existent is not None:
            d["existent"] = self.existent
        if self.camp:
            d["erori_campuri"] = [{"camp": self.camp, "mesaj": str(self)}]
        return d


def constrangerea(e):
    """Numele constrângerii încălcate (`diag.constraint_name`), sau „”."""
    return getattr(getattr(e, "diag", None), "constraint_name", None) or ""


def valoarea(e):
    """Valoarea dublată, din detaliul bazei („Key (cont, cui)=(4111, 14399840) already exists.” -> „4111, 14399840”), sau None."""
    m = re.search(r"\)=\((.*)\) already exists", getattr(getattr(e, "diag", None), "message_detail", None) or "")
    return m.group(1) if m else None


@contextlib.contextmanager
def refuza_dublura(cur, constrangeri, refuz):
    """Scrierea din blocul `with` rulează sub un savepoint; o violare a uneia din `constrangeri` întoarce tranzacția la savepoint
    și ridică `refuz(cur, e)`. Orice altă excepție (inclusiv altă constrângere) trece neatinsă."""
    cur.execute("SAVEPOINT cheie_unica")
    try:
        yield
    except psycopg2.errors.UniqueViolation as e:
        if constrangerea(e) not in constrangeri:
            raise
        cur.execute("ROLLBACK TO SAVEPOINT cheie_unica")
        exc = refuz(cur, e)
        if exc is None:   # [lotul 10, C73 / U2] refuzul n-a găsit lucrul existent: excepția bazei trece neatinsă, nu se înghite
            raise
        raise exc from e
    cur.execute("RELEASE SAVEPOINT cheie_unica")


#: câte curse pierdute la rând se reiau (operațional, nu fiscal): a șasea cerere simultană pe același număr ar fi deja un tipar,
#: nu o coincidență — atunci refuzul numit, nu o buclă fără capăt
INCERCARI_LA_CURSA = 5


def reincearca_la_dublura(cur, constrangeri, scrie, refuz, incercari=None):
    """[lotul 10, C73 / U2] NUMĂRUL DAT DE APLICAȚIE (`MAX + 1`): o cursă pierdută se reia cu numărul următor, nu se refuză.

    `scrie()` alocă singur numărul (citește `MAX + 1` ÎNĂUNTRU) și scrie, sub un savepoint. Dacă o cerere simultană a luat același
    număr, baza refuză a doua scriere pe una din `constrangeri`; atunci tranzacția se întoarce la savepoint și `scrie()` se cheamă din
    nou — în READ COMMITTED citirea nouă vede rândul celeilalte cereri (comis, altfel violarea n-ar fi apărut), deci primește numărul
    următor. Un refuz pentru o valoare pe care omul n-a scris-o ar fi fals: numărul e al aplicației, iar cursa e a ei.
    Abia după `incercari` curse pierdute la rând (n-are drum în practică) se ridică `refuz(cur, e)`, ca la `refuza_dublura`.
    Întoarce ce întoarce `scrie()`; ce citește din cursor citește ÎNĂUNTRU (`RELEASE SAVEPOINT` golește cursorul)."""
    incercari = incercari or INCERCARI_LA_CURSA
    for incercare in range(incercari):
        cur.execute("SAVEPOINT cheie_unica")
        try:
            rez = scrie()
        except psycopg2.errors.UniqueViolation as e:
            if constrangerea(e) not in constrangeri:
                raise
            cur.execute("ROLLBACK TO SAVEPOINT cheie_unica")
            if incercare == incercari - 1:
                exc = refuz(cur, e)
                if exc is None:
                    raise
                raise exc from e
            continue
        cur.execute("RELEASE SAVEPOINT cheie_unica")
        return rez
