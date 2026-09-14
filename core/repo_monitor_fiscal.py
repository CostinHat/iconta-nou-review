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


def select_public_3(cur, aid, prag):
    cur.execute("SELECT 1 FROM public.alerte_emise WHERE alerta_id=%s AND prag=%s", (aid, prag))
    return cur.fetchone()


def select_public_4(cur):
    cur.execute("SELECT id FROM public.accounting_firms WHERE activ")


def insert_public_2(cur, cid, mesaj):
    cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj) VALUES (%s, %s)", (cid, mesaj))


def insert_public_3(cur, aid, prag):
    cur.execute("INSERT INTO public.alerte_emise (alerta_id, prag) VALUES (%s, %s)", (aid, prag))
