# -*- coding: utf-8 -*-
"""C194 (lotul 12, găsită de Code la C133) — o D112 aflată deja în coadă nu devenea „depășită” când se corecta fișa salariatului:
`coada_api.amprenta_surse` amprentează numai notele și facturile perioadei, iar D112 nu se face din ele, ci din datele salariaților
(`d112.pull`). Acum declarațiile din `coada_api.DECLARATII_DIN_SALARII` poartă și `amprenta_salarii` (rândurile întregi ale
`SURSE_SALARII`, pe luna declarației), iar `depasire` le confruntă pe amândouă; o D112 intrată în coadă fără ea e depășită (fail-closed,
ca la 17.10.2026 pentru amprenta documentelor).

Pe o schemă efemeră din `tenant_template.sql` (anul 2099, sintetic), în tranzacție anulată. CNP 1900101410011 — cifra de control
verificată cu algoritmul din CLAUDE.md. Temei: N/A — regula de proces (decizia Costin 17.10.2026 7.2 pct.3: declarația din coadă se
marchează depășită când i se schimbă datele-sursă); cifrele D112 nu se schimbă aici.
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_c194"
_DE_LA, _PANA_LA = "2099-10-01", "2099-11-01"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


@pytest.fixture()
def lume():
    if not _DB:
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    yield _SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _salariat(cur, tichet=0, angajat="2099-01-01", cnp="1900101410011"):
    cur.execute("WITH s AS (INSERT INTO salariati (cnp, nume, prenume, data_angajare, ore_zi, judet_casa, tichet_masa_valoare) VALUES "
                "(%s,'IONESCU','VASILE',%s,8,'B',%s) RETURNING id, data_angajare), "
                "i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) SELECT id, data_angajare, 4050 FROM s) "
                "SELECT id FROM s", (cnp, angajat, tichet))
    return cur.fetchone()[0]


def _payload(cur, ca, lume, tip):
    return {"_surse": {"de_la": _DE_LA, "pana_la": _PANA_LA, **ca.amprente(cur, lume, tip, _DE_LA, _PANA_LA), "note": []}}


def test_c194_d112_din_coada_devine_depasita_la_corectarea_fisei_salariatului(lume):
    """Corectura scutirii (C133: „Scutit” + „Motiv”) pe fișa unui salariat al lunii -> D112 din coadă e depășită, cu motivul ei; D300
    (din facturi) nu. MUTAȚIE: în `depasire`, `amprenta_salarii(...) == s["amprenta_salarii"]` -> `True` -> pică."""
    from core import coada_api as ca
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            sid = _salariat(cur)
            p112, p300 = _payload(cur, ca, lume, "d112"), _payload(cur, ca, lume, "d300")
            assert set(p112["_surse"]) == {"de_la", "pana_la", "amprenta", "amprenta_salarii", "note"}, p112
            assert set(p300["_surse"]) == {"de_la", "pana_la", "amprenta", "note"}, p300
            assert ca.depasire(cur, lume, p112, "d112") is None, "aceleași date -> nedepășită"
            cur.execute("UPDATE salariati SET scutit_contrib_minim = true, motiv_exceptare = 2 WHERE id = %s", (sid,))
            dep = ca.depasire(cur, lume, p112, "d112")
            assert dep and dep["mesaj"] == (
                "Declarația e depășită: după generare s-au schimbat datele salariaților lunii (fișa unui salariat, salariul, un concediu "
                "medical, o suspendare, pontajul, elementele variabile sau tichetele). Cifrele ei nu mai sunt cele din evidență; "
                "generează-o din nou."), dep
            assert dep["fel"] == "contradictie" and len(dep["sursele"]) == 2, dep
            assert ca.depasire(cur, lume, p300, "d300") is None, "D300 nu se face din fișa salariatului"
        c.rollback()


def test_c194_concediul_medical_al_lunii_schimba_amprenta_cel_din_alta_luna_nu(lume):
    """Un concediu medical al lunii declarației schimbă amprenta; unul din luna următoare și un salariat încetat înainte de lună nu.
    MUTAȚIE: fereastra `concedii_medicale` -> `TRUE` -> pică."""
    from core import coada_api as ca
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            sid = _salariat(cur)
            vechi = _salariat(cur, angajat="2098-01-01", cnp="1990101412340")
            cur.execute("UPDATE salariati SET data_incetare = '2099-08-31' WHERE id = %s", (vechi,))
            a0 = ca.amprenta_salarii(cur, lume, _DE_LA, _PANA_LA)
            cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile) VALUES (%s, 2099, 11, '01', 3)", (sid,))
            cur.execute("UPDATE salariati SET persoane_intretinere = 2 WHERE id = %s", (vechi,))
            assert ca.amprenta_salarii(cur, lume, _DE_LA, _PANA_LA) == a0, "luna următoare / salariatul încetat nu intră în D112 a lunii"
            cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile) VALUES (%s, 2099, 10, '01', 3)", (sid,))
            assert ca.amprenta_salarii(cur, lume, _DE_LA, _PANA_LA) != a0, "concediul medical al lunii intră în D112"
        c.rollback()


def test_c194_d112_intrata_fara_amprenta_salariatilor_e_depasita_fail_closed(lume):
    """O D112 intrată în coadă înainte de C194 (fără `amprenta_salarii`) nu se poate confrunta cu datele salariaților -> depășită.
    MUTAȚIE: condiția `tip in DECLARATII_DIN_SALARII and not s.get("amprenta_salarii")` scoasă -> pică."""
    from core import coada_api as ca
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            vechi = {"_surse": {"de_la": _DE_LA, "pana_la": _PANA_LA, "amprenta": ca.amprenta_surse(cur, lume, _DE_LA, _PANA_LA), "note": []}}
            dep = ca.depasire(cur, lume, vechi, "d112")
            assert ca.depasire(cur, lume, vechi, "d300") is None
        c.rollback()
    assert dep and dep["fel"] == "verificare_rupta" and dep["mesaj"].startswith("Declarația a intrat în coadă înainte ca aplicația"), dep


def test_c194_intrarea_in_coada_pastreaza_amprenta_salariatilor_la_d112(lume, monkeypatch):
    """`uc_coada.surse_declaratiei` (drumul „Pune în coadă”) dă `amprenta_salarii` la D112 și numai acolo. MUTAȚIE: în
    `coada_api.amprente`, `if tip in DECLARATII_DIN_SALARII` -> `if False` -> pică."""
    from core import uc_coada as uq
    monkeypatch.setattr(uq, "fereastra_declaratie", lambda schema, tip, an, luna, trim: (_DE_LA, _PANA_LA))
    s112 = uq.surse_declaratiei(lume, "d112", 2099, 10, None)
    s300 = uq.surse_declaratiei(lume, "d300", 2099, 10, None)
    assert s112.get("amprenta_salarii") and s300.get("amprenta_salarii", "lipsă") == "lipsă", (s112, s300)


def test_c194_garda_toate_tabelele_citite_de_d112_pull_sunt_in_amprenta(lume):
    """GARDA clasei: tabelele firmei pe care `d112.pull` le citește efectiv (statisticile tranzacției, `pg_stat_xact_user_tables`) sunt toate
    în `SURSE_SALARII` (afară de `firma_profil`, scos cu motiv în `coada_api`). Dacă D112 începe să citească un tabel nou, testul pică
    până când tabelul intră în amprentă. MUTAȚIE: `("pontaj", …)` scos din `SURSE_SALARII` -> pică."""
    from core import coada_api as ca
    from core import d112
    from core.common import Perioada
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            sid = _salariat(cur, tichet=30)
            cur.execute("INSERT INTO perioada_confirmata (an, luna, domeniu) VALUES (2099, 10, 'pontaj')")
            cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile) VALUES (%s, 2099, 10, '01', 3)", (sid,))
            cur.execute("SELECT relname, seq_scan + COALESCE(idx_scan, 0) FROM pg_stat_xact_user_tables WHERE schemaname = %s", (lume,))
            inainte = dict(cur.fetchall())
        d112.pull(c, lume, Perioada(an=2099, luna=10))
        with c.cursor() as cur:
            cur.execute("SELECT relname, seq_scan + COALESCE(idx_scan, 0) FROM pg_stat_xact_user_tables WHERE schemaname = %s", (lume,))
            citite = {t for t, n in cur.fetchall() if n > inainte.get(t, 0)}
        c.rollback()
    assert {"salariati", "concedii_medicale", "pontaj", "salariu_istoric"} <= citite, citite   # garda vede citirile
    lipsa = citite - {t for t, _ in ca.SURSE_SALARII} - {"firma_profil"}
    assert not lipsa, "D112 citește %s, dar amprenta salariaților nu le cuprinde (coada_api.SURSE_SALARII)" % sorted(lipsa)


def test_c194_amprenta_e_aceeasi_pe_cursorul_dictionar_al_listei_cozii(lume):
    """Lista cozii (`lista_coada` -> `depasire`) citește amprenta printr-un cursor-dicționar, intrarea în coadă prin unul obișnuit: aceeași
    lună dă aceeași amprentă pe amândouă. Înainte, cele opt coloane „există tabelul?” fără nume se strângeau pe dicționar într-o singură
    cheie („?column?”), amprenta cuprindea numai `salariati`, iar orice D112 ieșea „depășită” imediat după intrarea în coadă (prins de
    e2e-ul C194 și de pasul D112 al scenariului lunii pilot, 25.10.2026). MUTAȚIE: alias-urile `AS e<n>` scoase -> pică."""
    import psycopg2.extras as _E
    from core import coada_api as ca
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            sid = _salariat(cur)
            cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile) VALUES (%s, 2099, 10, '01', 3)", (sid,))
            simplu = ca.amprenta_salarii(cur, lume, _DE_LA, _PANA_LA)
        with c.cursor(cursor_factory=_E.RealDictCursor) as cur:
            assert ca.amprenta_salarii(cur, lume, _DE_LA, _PANA_LA) == simplu
            assert ca.depasire(cur, lume, {"_surse": {"de_la": _DE_LA, "pana_la": _PANA_LA, "amprenta_salarii": simplu,
                                                      "amprenta": ca.amprenta_surse(cur, lume, _DE_LA, _PANA_LA), "note": []}},
                               "d112") is None
        c.rollback()
