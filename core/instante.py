# -*- coding: utf-8 -*-
"""P6 valul 3 — mai multe procese care servesc, fara ca vreunul sa creada ca e singur.

CE CERE TEXTUL CANONIC (`PLAN_HARDENING.md:709-721`): trecerea de la **un singur proces**
(`ExecStart` fara `--workers`, un singur PID) la **mai multe instante**, cu patru criterii de
acceptare — doua instante care se comporta identic · reconstructia fiecarui cache ramas (facuta la
valul 2) · **fault-check**, o instanta oprita in timpul unei cereri · si four-way-ul redefinit din
«procesul viu poarta HEAD» in «**TOATE** procesele poarta HEAD».

Modulul asta raspunde la trei intrebari pe care un proces nu si le punea cat era singur:

  1. CINE INSTALEAZA INFRASTRUCTURA LA PORNIRE?  Toti — dar pe rand.
     `migreaza_triggerele` face `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER` pentru FIECARE tenant.
     Patru workeri care pornesc in aceeasi secunda ar face-o simultan, pe aceleasi obiecte: fie
     coliziuni de blocaje, fie erori — iar blocul de pornire e FAIL-CLOSED, deci serviciul n-ar mai
     porni deloc. `blocaj_pornire` ii serializeaza cu un `pg_advisory_xact_lock`, legat de
     tranzactie: se elibereaza singur la commit sau la rollback, deci un worker care moare la
     mijloc nu lasa poarta incuiata. Fiecare worker TOT ruleaza instalarea si verificarea — nu se
     sare peste ele —, doar ca unul dupa altul; a doua rulare e idempotenta si ieftina.

  2. CINE RULEAZA MUNCA DE FUNDAL?  Unul singur, prin LEASE.
     Bucla de sanatate scrie in `metrici_sanatate` si interogheaza catalogul la 5 minute. Cu N
     workeri ar face-o de N ori. Alegerea liderului foloseste EXACT forma de la valul 1 — o
     rezervare atomica intr-o singura instructiune — nu un `pg_try_advisory_lock` la nivel de
     sesiune: acela s-ar lega de o CONEXIUNE, iar conexiunile vin dintr-un pool si se rotesc.
     Un lease expira singur, deci daca liderul moare, urmatorul il preia fara ca nimeni sa curete.

  3. TOATE PROCESELE POARTA HEAD?  Se poate raspunde numai daca ele o spun.
     `ActiveEnterTimestamp > data commitului` era un PROXY bun cat timp exista un singur proces.
     Cu mai multe, proxy-ul afirma despre unitate ce ar trebui afirmat despre fiecare proces. Deci
     fiecare worker se INREGISTREAZA la pornire cu commitul pe care il poarta, iar bratul
     four-way devine o intrebare pe date: *exista vreun proces viu al carui commit nu e HEAD?*

CE NU FACE modulul asta: nu porneste procese, nu stie cate ar trebui sa fie, nu opreste pe nimeni.
Numarul de instante e o decizie de infrastructura (`--workers` in unitate), iar modulul doar face
ca ea sa fie sigura si masurabila.
"""
import os
import socket
import sys

#: Cheia blocajului de pornire. Un intreg fix, ales o data, DIFERIT de `firma_rezumat.CHEIE_BLOCAJ`
#: (0x1C0A7A) — doua blocaje consultative cu aceeasi cheie ar parea ca se apara unul pe altul si
#: s-ar bloca reciproc fara ca nimeni sa inteleaga de ce.
CHEIE_PORNIRE = 0x1C0A7B

#: Cat tine dreptul de a fi lider, si cat de des se reinnoieste. Termenul e mai lung decat perioada
#: buclei (300 s), ca o intarziere obisnuita sa nu produca o schimbare de lider; dar destul de
#: scurt cat un lider mort sa fie inlocuit intr-un ciclu.
LEASE_SEC = 900

#: Cand se considera moarta o instanta care nu mai bate. Trei batai ratate.
INSTANTA_MOARTA_SEC = 900

DDL = """
-- [P6 val 3, 12.09.2026] Procesele care servesc ACUM, fiecare cu commitul pe care il poarta.
-- Exista ca sa se poata raspunde la intrebarea canonica «TOATE procesele poarta HEAD?», care pana
-- azi se aproxima cu ora de pornire a unitatii systemd.
CREATE TABLE IF NOT EXISTS public.instante (
    gazda      text        NOT NULL,
    pid        integer     NOT NULL,
    commit_sha text,                      -- NULL cand git n-a raspuns; se vede, nu se ghiceste
    pornit_la  timestamptz NOT NULL DEFAULT now(),
    batut_la   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (gazda, pid)
);
CREATE INDEX IF NOT EXISTS idx_instante_batut ON public.instante (batut_la);

-- [P6 val 3, 12.09.2026] Dreptul de a rula munca de fundal, cu TERMEN. Un rand per rol.
CREATE TABLE IF NOT EXISTS public.instante_lider (
    rol       text        PRIMARY KEY,
    gazda     text        NOT NULL,
    pid       integer     NOT NULL,
    expira_la timestamptz NOT NULL
);
"""


def aplica_ddl(conn):
    """Tabelele. Idempotent. Se cheama la pornire, in blocul fail-closed."""
    with conn.cursor() as cur:
        cur.execute(DDL)


def eu():
    """(gazda, pid) — identitatea procesului asta. Doua workere au PID-uri diferite."""
    return socket.gethostname(), os.getpid()


# ============================================================
#  1. PORNIREA, SERIALIZATA
# ============================================================
def blocaj_pornire(conn):
    """Ia blocajul de pornire. Se elibereaza SINGUR la sfarsitul tranzactiei.

    `pg_advisory_xact_lock` blocheaza pana il primeste — si asta e purtarea dorita: un worker care
    asteapta e corect, unul care sare peste instalare ar servi cereri peste o infrastructura
    neverificata, adica exact ce interzice blocul fail-closed din `lifespan`.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(%s)", (CHEIE_PORNIRE,))


# ============================================================
#  2. LIDERUL, PRIN LEASE
# ============================================================
def blocaj_tinut(conn):
    """Tine procesul asta, CHIAR ACUM, blocajul de pornire? Intrebat la sursa, nu dedus.

    `pg_locks` sparge cheia de 64 de biti in doua coloane de 32; `objsubid = 1` inseamna forma cu
    un singur intreg, care e chiar forma lui `pg_advisory_xact_lock(bigint)`.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM pg_locks "
            " WHERE locktype = 'advisory' AND classid = %s AND objid = %s AND objsubid = 1 "
            "   AND pid = pg_backend_pid() AND granted",
            (CHEIE_PORNIRE >> 32, CHEIE_PORNIRE & 0xFFFFFFFF))
        return cur.fetchone()[0] > 0


class BlocajPierdut(RuntimeError):
    """Blocajul de pornire s-a pierdut inainte de capatul sectiunii critice.

    Tip propriu, nu `RuntimeError` gol, ca proba sa poata intreba CE s-a intamplat fara sa citeasca
    proza mesajului: o conditie numita primeste o eroare numita (METODA §23).
    """


def confirma_blocaj(conn):
    """Ridica daca blocajul NU mai e tinut la capatul sectiunii critice.

    DE CE EXISTA (12.09.2026, dupa un defect masurat pe productie). Blocajul se lua corect, dar
    apelul URMATOR — `migrare_api.asigura_tabel` — se termina cu `conn.commit()`, iar un blocaj
    legat de tranzactie moare odata cu ea. Instalarea infrastructurii rula NESERIALIZATA, si la
    fiecare repornire cu doi workeri unul murea cu `tuple concurrently updated`. Patru din patru.

    *Nimic nu se plangea.* Proba care exista verifica `blocaj_pornire` IZOLAT — acolo functia chiar
    serializeaza —, iar o poarta care intreaba daca functia merge nu poate afla ca cineva i-a luat
    blocajul din mana trei linii mai jos. Deci intrebarea se pune acum acolo unde conteaza: la
    CAPAT, despre blocajul REAL. Un apel viitor care comite in mijlocul sectiunii nu mai poate
    desface serializarea in tacere — opreste pornirea, ca orice alta verificare din blocul asta.
    """
    if not blocaj_tinut(conn):
        raise BlocajPierdut(
            "[P6] blocajul de pornire NU mai e tinut la capatul sectiunii critice — ceva a incheiat "
            "tranzactia intre timp (un `commit` intr-un apel chemat de aici). Instalarea "
            "infrastructurii a rulat NESERIALIZAT, deci pornirea asta nu poate fi declarata sigura.")


def retrage_liderul_mort(conn, rol):
    """Scoate lease-ul unui lider care nu mai exista PE GAZDA ASTA. Intoarce PID-ul scos, sau `None`.

    DE CE (12.09.2026, masurat de doua ori pe productie). `instante` isi retrage mortii de pe gazda
    proprie; `instante_lider` nu avea perechea. Consecinta: dupa fiecare repornire, lease-ul ramanea
    pe procesul mort pana la EXPIRARE — 900 s in care munca de fundal nu se facea deloc (masurat:
    nicio scriere in `metrici_sanatate` intre 14:36 si 14:49). Textul de langa `LEASE_SEC` spunea
    «destul de scurt cat un lider mort sa fie inlocuit intr-un ciclu», iar ciclul e 300 s — deci
    proza si purtarea nu se potriveau.

    NU se scurteaza niciun termen ca sa iasa cifra: pe gazda proprie moartea nu se ghiceste, o stie
    sistemul de operare — exact mecanismul lui `retrage_mortii_de_pe_gazda`, chemat pentru acelasi
    fel de rand. Termenul de 900 s ramane neschimbat, si ramane singurul raspuns pentru un lider de
    pe ALTA gazda: acolo bataia e tot ce se stie. Se declara, nu se ascunde.

    Stergerea e legata de (rol, gazda, pid): daca intre citire si stergere altcineva a preluat deja,
    randul lui NU se atinge.
    """
    gazda, _pid = eu()
    with conn.cursor() as cur:
        cur.execute("SELECT gazda, pid FROM public.instante_lider WHERE rol = %s", (rol,))
        r = cur.fetchone()
        if not r or r[0] != gazda or traieste(r[1]):
            return None
        cur.execute("DELETE FROM public.instante_lider "
                    " WHERE rol = %s AND gazda = %s AND pid = %s", (rol, r[0], r[1]))
        return r[1]


def cere_lider(conn, rol, lease_sec=LEASE_SEC):
    """`True` daca procesul asta are dreptul sa faca munca de fundal pentru `rol`.

    O SINGURA instructiune atomica, aceeasi forma ca rezervarea alertelor de la valul 1: din N
    workeri care incearca in aceeasi clipa, exact unul primeste rand inapoi. Liderul de azi isi
    REINNOIESTE dreptul (a doua ramura a lui `WHERE`), deci nu se schimba conducerea la fiecare
    ciclu — o schimbare inutila ar rupe continuitatea masuratorilor.
    """
    gazda, pid = eu()
    with conn.cursor() as cur:
        # upsert-ok: lease cu castigator unic. Suprascrierea E scopul — `DO UPDATE ... WHERE`
        # reuseste doar daca termenul a expirat SAU daca cel care cere e chiar detinatorul.
        cur.execute(
            "INSERT INTO public.instante_lider (rol, gazda, pid, expira_la) "
            "VALUES (%s, %s, %s, now() + make_interval(secs => %s)) "
            "ON CONFLICT (rol) DO UPDATE "
            "   SET gazda = EXCLUDED.gazda, pid = EXCLUDED.pid, expira_la = EXCLUDED.expira_la "
            " WHERE public.instante_lider.expira_la <= now() "
            "    OR (public.instante_lider.gazda = EXCLUDED.gazda "
            "        AND public.instante_lider.pid = EXCLUDED.pid) "
            "RETURNING pid",
            (rol, gazda, pid, lease_sec))
        return cur.fetchone() is not None


def cine_e_lider(conn, rol):
    """(gazda, pid) al liderului in viata, sau `None`. Exista pentru probe si pentru ecran."""
    with conn.cursor() as cur:
        cur.execute("SELECT gazda, pid FROM public.instante_lider "
                    " WHERE rol = %s AND expira_la > now()", (rol,))
        r = cur.fetchone()
        return (r[0], r[1]) if r else None


# ============================================================
#  3. REGISTRUL INSTANTELOR — bratul four-way redefinit
# ============================================================
def traieste(pid):
    """Exista procesul asta pe gazda ASTA? Intrebarea se pune sistemului de operare, nu unui
    cronometru. `PermissionError` inseamna «exista, dar nu e al meu» — deci traieste."""
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def retrage_mortii_de_pe_gazda(conn):
    """Scoate rindurile gazdei ASTEIA ale caror PID-uri nu mai exista.

    [12.09.2026] Adaugata dupa ce bratul four-way a raportat, PE DREPT, un proces mort ca fiind
    viu: fereastra de bataie (900 s) e mai lunga decat intervalul dintre doua reporniri, iar cu
    `Restart=always` asta se intampla de la sine. Pe gazda proprie moartea nu trebuie ghicita.

    CE NU ACOPERA, declarat: (a) rindurile ALTOR gazde — acolo bataia ramane singurul semn;
    (b) reciclarea unui PID, caz in care rindul vechi supravietuieste pana ii expira bataia.
    """
    gazda, _pid = eu()
    scoase = []
    with conn.cursor() as cur:
        cur.execute("SELECT pid FROM public.instante WHERE gazda = %s", (gazda,))
        for (p,) in cur.fetchall():
            if not traieste(p):
                scoase.append(p)
        for p in scoase:
            cur.execute("DELETE FROM public.instante WHERE gazda = %s AND pid = %s", (gazda, p))
    return scoase


def inregistreaza(conn, commit_sha):
    """Procesul asta intra in registru cu commitul pe care il poarta. La pornire.

    Retrage intai mortii de pe gazda lui: un registru care pastreaza fantome raspunde gresit exact
    la intrebarea pentru care exista — «toate procesele poarta HEAD?».
    """
    retrage_mortii_de_pe_gazda(conn)
    gazda, pid = eu()
    with conn.cursor() as cur:
        # upsert-ok: un PID se poate refolosi dupa o repornire; randul vechi descrie un proces
        # mort, iar a-l pastra ar face registrul sa minta. Suprascrierea E scopul.
        cur.execute(
            "INSERT INTO public.instante (gazda, pid, commit_sha, pornit_la, batut_la) "
            "VALUES (%s, %s, %s, now(), now()) "
            "ON CONFLICT (gazda, pid) DO UPDATE "
            "   SET commit_sha = EXCLUDED.commit_sha, pornit_la = now(), batut_la = now()",
            (gazda, pid, commit_sha))


def bate(conn):
    """Semnul ca procesul asta mai traieste. Din bucla de fundal, din FIECARE worker — nu doar
    din lider: un registru care ar bate numai pentru lider ar declara moarte toate celelalte."""
    gazda, pid = eu()
    with conn.cursor() as cur:
        cur.execute("UPDATE public.instante SET batut_la = now() "
                    " WHERE gazda = %s AND pid = %s", (gazda, pid))


def curata(conn, moarta_sec=INSTANTA_MOARTA_SEC):
    """Scoate procesele care nu mai bat. Marginire EXPLICITA: fara ea, registrul ar creste cu
    fiecare repornire si ar raporta drept vii niste PID-uri disparute — adica ar face bratul
    four-way sa pice pe fantome."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM public.instante "
                    " WHERE batut_la <= now() - make_interval(secs => %s)", (moarta_sec,))
        return cur.rowcount


def vii(conn, moarta_sec=INSTANTA_MOARTA_SEC):
    """[(gazda, pid, commit_sha, pornit_la)] pentru procesele care mai bat."""
    with conn.cursor() as cur:
        cur.execute("SELECT gazda, pid, commit_sha, pornit_la FROM public.instante "
                    " WHERE batut_la > now() - make_interval(secs => %s) "
                    " ORDER BY gazda, pid", (moarta_sec,))
        return [tuple(r) for r in cur.fetchall()]


def toate_poarta(conn, head_sha, moarta_sec=INSTANTA_MOARTA_SEC):
    """Bratul four-way REDEFINIT: `(da, total, rataciti)`.

    `da` e `True` numai daca exista cel putin un proces viu SI niciunul nu poarta alt commit. Un
    registru gol NU inseamna «toate poarta HEAD»: inseamna ca nu se poate sti, iar raspunsul
    trebuie sa fie `False`. *Un brat care se inchide pe o multime vida afirma mai putin decat pare.*
    """
    lista = vii(conn, moarta_sec)
    rataciti = [x for x in lista if x[2] != head_sha]
    return (bool(lista) and not rataciti), len(lista), rataciti


def main():
    """`python3 -m core.instante` — ce se vede acum. Pentru om si pentru hook."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        aplica_ddl(conn)
        for g, p, c, t in vii(conn):
            print("%s pid=%-7d commit=%s  pornit %s" % (g, p, (c or "?")[:8], t))
        print("lider sanatate: %s" % (cine_e_lider(conn, "sanatate"),))
    return 0


if __name__ == "__main__":
    sys.exit(main())
