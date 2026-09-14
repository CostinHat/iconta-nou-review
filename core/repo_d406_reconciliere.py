# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d406_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d406_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT platitor_tva, tip_decont FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def sql(cur, q, di, ds):
    cur.execute(q, (di, ds))
    return cur.fetchall()
