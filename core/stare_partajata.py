# -*- coding: utf-8 -*-
"""P6 valul 1 — starea business care nu mai are voie sa traiasca in memoria unui proces.

DECIZIA ARHITECTULUI (12.09.2026): `P6_WAVE1_AUTHORITATIVE_STORE=POSTGRESQL`, `REDIS=REJECTED`.
Motivul, citat: baza exista deja si e sursa autoritativa a aplicatiei · se evita o dependenta
operationala noua · cursa din `_login_fail` se poate elimina STRUCTURAL prin operatii atomice de
bazaa · acceptarea multi-proces devine demonstrabila pe aceeasi sursa comuna.

CE ERA INAINTE, si de ce nu se putea repara pe loc. Doua dictionare la nivel de modul in `main`:

    _login_fail = {}                # esecuri de autentificare per cont
    _alerte_ultima_trimitere = {}   # cand a plecat ultima alerta din fiecare categorie

Amandoua purtau DECIZII — blocarea unui cont, respectiv «se trimite sau nu» —, si amandoua se
pierdeau la fiecare repornire. Masurat pe 12.09, inainte de reparatie:

  · DIVERGENTA: cinci esecuri in procesul A il blocheaza; procesul B nu stie nimic (`B_blocat=False`).
  · CURSA: `_login_blocat` facea CITESTE-FILTREAZA-SCRIE peste acelasi dict —
        q = [t for t in _login_fail.get(e, []) if ...]   # citeste
        _login_fail[e] = q                                # SCRIE peste lista de atunci
    iar un `_login_esec` care adauga in fereastra dintre cele doua se PIERDEA. Sub presiune
    sustinuta, la k=10 fire x 500 runde, s-au pierdut 4326 din 5000 de esecuri (87%). Adica
    incercarile concurente pe acelasi cont ocoleau in buna masura blocarea.

CE E ACUM, si de ce forma asta si nu alta:

  · un esec de autentificare e un `INSERT` — un RAND, nu un contor actualizat. Doua inserari
    concurente nu se pot pierde una pe alta, fiindca niciuna nu citeste ce a scris cealalta.
    *Cursa nu e micsorata, e scoasa din constructie:* nu mai exista nicio citire urmata de o
    scriere peste ce s-a citit.
  · intrebarea «e blocat?» e un `COUNT` cu fereastra in clauza, nu o filtrare in Python urmata de
    o rescriere. Citirea nu mai are efect secundar.
  · rezervarea unei alerte e o SINGURA instructiune: o inserare care, la conflict pe cheia
    categoriei, actualizeaza numai daca fereastra de cooldown a trecut, si intoarce randul celui
    care a reusit. Cine primeste randul inapoi a castigat dreptul sa trimita. Doua procese care
    incearca in aceeasi clipa: exact unul primeste rand. (Forma SQL e mai jos, la `rezerva_alerta`;
    n-o repet aici, ca sa nu apara de doua ori in fisier.)

CE NU S-A SCHIMBAT, si e verificat de probe: **cinci esecuri in cincisprezece minute**, per CONT
(per-IP ramane la nginx, `iconta_auth 5r/m`, neatins) · **o ora de cooldown** per categorie de
alerta · cine cheama, cand, si ce se intampla dupa. Semantica `once`/retry a oricarei alte
operatii nu e atinsa.

EXPIRAREA E EXPLICITA SI MARGINITA, in doua feluri care se sprijina:
  (a) la CITIRE, fereastra e in `WHERE` — un rand vechi nu contribuie, chiar daca e inca in tabela;
  (b) la fiecare SCRIERE, randurile iesite din fereastra se sterg — TOATE, nu doar ale contului
      curent. Deci dupa orice esec de autentificare din aplicatie, tabela contine numai randuri
      din fereastra. Nu e o curatenie «cand ne aducem aminte», si nu are nevoie de un job.
  `alerte_cooldown` n-are nevoie de curatenie: are un rand per categorie, iar categoriile sunt o
  multime mica si fixa, scrisa in `main`. E marginita prin constructie, nu prin stergere.

PURTAREA LA ESEC DE BAZA — diferita intre cele doua, si fiecare cu motivul ei:
  · `login_blocat` RIDICA. Nu intoarce `False`. Un refuz de a raspunde nu are voie sa devina
    «nu e blocat»: ar transforma o baza cazuta intr-o poarta deschisa. Oricum, cererea de login
    ar cadea doua linii mai jos, la propria ei conexiune.
  · `login_esec` RIDICA. Un esec neinregistrat slabeste tacut blocarea; e mai bine sa se vada.
  · `poate_alerta` intoarce `False` si CONSEMNEAZA. Fara rezervare nu putem sti ca alt proces nu
    trimite chiar acum, iar a trimite «ca sa fim siguri» e exact defectul pe care valul asta il
    inchide. Consecinta declarata: cat timp baza e jos, alertele nu pleaca — semnalul pentru asta
    e deadman-ul de cron, care nu trece prin functia asta.
"""
import sys

#: Contractul de blocare, neschimbat fata de `[login_lockout_v1]`. Stau AICI, langa interogarile
#: care le folosesc, ca sa nu existe doua locuri care spun «cinci» si «cincisprezece minute».
PRAG_ESECURI = 5
FEREASTRA_ESECURI_SEC = 900

DDL = """
-- [P6 val 1, 12.09.2026] Esecurile de autentificare, per CONT. Un RAND per esec — nu un contor —
-- fiindca doua inserari concurente nu se pot suprascrie, iar un contor actualizat se poate.
CREATE TABLE IF NOT EXISTS public.login_esecuri (
    id       bigserial   PRIMARY KEY,
    email    text        NOT NULL,
    esuat_la timestamptz NOT NULL DEFAULT now()
);
-- Indexul serveste amandoua interogarile: COUNT-ul pe (email, fereastra) si stergerea pe timp.
CREATE INDEX IF NOT EXISTS idx_login_esecuri_email_timp
    ON public.login_esecuri (email, esuat_la DESC);
CREATE INDEX IF NOT EXISTS idx_login_esecuri_timp
    ON public.login_esecuri (esuat_la);

-- [P6 val 1, 12.09.2026] Cooldown-ul alertelor, GLOBAL intre procese. Cheia primara e categoria:
-- un rand per categorie, deci tabela e marginita prin constructie si n-are nevoie de curatenie.
CREATE TABLE IF NOT EXISTS public.alerte_cooldown (
    categorie        text        PRIMARY KEY,
    ultima_trimitere timestamptz NOT NULL DEFAULT now()
);
"""


def aplica_ddl(conn):
    """Tabelele. Idempotent. Se cheama la pornire, in blocul fail-closed din `lifespan`."""
    with conn.cursor() as cur:
        cur.execute(DDL)


# ============================================================
#  BLOCAREA LA AUTENTIFICARE
# ============================================================
def login_blocat(conn, email, prag=PRAG_ESECURI, fereastra_sec=FEREASTRA_ESECURI_SEC):
    """`True` daca in fereastra s-au strans cel putin `prag` esecuri pentru contul asta.

    CITIRE PURA. Forma dinainte filtra in Python si REscria lista filtrata inapoi in dictionar,
    adica o citire cu efect secundar — si chiar acolo se pierdeau esecurile concurente. Aici
    fereastra e in `WHERE`, deci expirarea se aplica fara sa scrie nimeni nimic.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM public.login_esecuri "
            " WHERE email = %s AND esuat_la > now() - make_interval(secs => %s)",
            (email, fereastra_sec))
        return cur.fetchone()[0] >= prag


def login_esec(conn, email, fereastra_sec=FEREASTRA_ESECURI_SEC):
    """Consemneaza un esec. O INSERARE, deci doua apeluri concurente dau doua randuri.

    Sterge intai ce a iesit din fereastra — TOATE randurile expirate, nu doar ale contului asta.
    Asa tabela ramane marginita la fereastra dupa orice scriere, fara job de curatenie. Cele doua
    instructiuni sunt in aceeasi tranzactie ca a apelantului: ori se vad amandoua, ori niciuna.
    """
    with conn.cursor() as cur:
        cur.execute("DELETE FROM public.login_esecuri "
                    " WHERE esuat_la <= now() - make_interval(secs => %s)", (fereastra_sec,))
        cur.execute("INSERT INTO public.login_esecuri (email) VALUES (%s)", (email,))


def login_reset(conn, email):
    """Autentificare reusita: contul o ia de la zero."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM public.login_esecuri WHERE email = %s", (email,))


def esecuri_in_fereastra(conn, email, fereastra_sec=FEREASTRA_ESECURI_SEC):
    """Cate esecuri vede baza. Exista pentru PROBE — `login_blocat` intoarce un prag, iar un prag
    nu poate arata daca s-a pierdut o inserare pe drum."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM public.login_esecuri "
            " WHERE email = %s AND esuat_la > now() - make_interval(secs => %s)",
            (email, fereastra_sec))
        return cur.fetchone()[0]


# ============================================================
#  COOLDOWN-UL ALERTELOR
# ============================================================
def rezerva_alerta(conn, categorie, cooldown_sec):
    """REZERVA dreptul de a trimite alerta din categoria asta. `True` = trimite TU.

    E o rezervare, nu o intrebare — la fel ca forma dinainte, care scria `ultima_trimitere` in
    chiar apelul care raspundea `True`. Diferenta e ca acum intrebarea si scrierea sunt UNA
    SINGURA, atomica in baza: din doua procese care incearca simultan, exact unul primeste rand
    inapoi. Inainte, amandoua citeau «a trecut ora» si amandoua trimiteau.
    """
    with conn.cursor() as cur:
        # upsert-ok: rezervare cu castigator unic. Suprascrierea E scopul — `DO UPDATE ... WHERE`
        # reuseste numai daca fereastra de cooldown a trecut, iar `RETURNING` spune cine a castigat.
        cur.execute(
            "INSERT INTO public.alerte_cooldown (categorie, ultima_trimitere) "
            "VALUES (%s, now()) "
            "ON CONFLICT (categorie) DO UPDATE SET ultima_trimitere = now() "
            " WHERE public.alerte_cooldown.ultima_trimitere <= now() - make_interval(secs => %s) "
            "RETURNING categorie",
            (categorie, cooldown_sec))
        return cur.fetchone() is not None


def main():
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        aplica_ddl(conn)
    print("stare_partajata: gata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
