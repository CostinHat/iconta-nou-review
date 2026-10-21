# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/monitor_fiscal.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/monitor_fiscal.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def insert_public(cur, sursa, url, rel, dv, directie, decl, a):
    cur.execute("""INSERT INTO public.alerte_fiscale (sursa, titlu, rezumat, url, relevanta,
                                                   data_vigoare, directie, declaratii_atinse)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (sursa, titlu) DO NOTHING RETURNING id""", (sursa, a.get("titlu", "")[:500], a.get("rezumat"), url,
                         rel, dv, directie, decl))
    return cur.fetchone()


def select_marcaj(cur, sursa, titlu):
    """[17.10.2026, lotul 7] Marcajul unei surse deja procesate (buletinul ANAF, actul din portal)."""
    cur.execute("SELECT 1 FROM public.alerte_fiscale WHERE sursa=%s AND titlu=%s", (sursa, titlu[:500]))
    return cur.fetchone()


def select_public(cur, titlu):
    cur.execute("SELECT 1 FROM public.alerte_fiscale WHERE sursa='anaf_buletin' AND titlu=%s", (titlu[:500],))
    return cur.fetchone()


def select_public_2(cur):
    cur.execute("""SELECT id, titlu, rezumat, data_vigoare FROM public.alerte_fiscale
                WHERE data_vigoare IS NOT NULL AND data_vigoare >= CURRENT_DATE""")
    return cur.fetchall()


def select(cur, dv, prag):
    cur.execute("SELECT (%s - CURRENT_DATE) = %s", (dv, prag))
    return cur.fetchone()


def select_public_4(cur):
    cur.execute("SELECT id FROM public.accounting_firms WHERE activ")


def insert_public_2(cur, cid, mesaj):
    cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj) VALUES (%s, %s)", (cid, mesaj))


def revendica_pragul(cur, aid, prag):
    """[lotul 10, C73 / U3] Pragul (alertă, 7/3/0 zile) se REVENDICĂ înainte de anunțuri: True numai pentru cine l-a scris. Înainte, pragul
    se verifica (SELECT), anunțurile plecau, iar rândul se scria la urmă — două rulări suprapuse ale cronului (emiterea zilnică și cea de
    după detecție) trimiteau amândouă anunțurile, iar a doua cădea pe `alerte_emise_pkey`. `ON CONFLICT DO NOTHING` e intenționat: cheia
    E jurnalul de idempotență; a doua rulare așteaptă rândul primei și, după commit-ul ei, nu mai emite nimic."""
    cur.execute("INSERT INTO public.alerte_emise (alerta_id, prag) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING 1", (aid, prag))
    return cur.fetchone() is not None
