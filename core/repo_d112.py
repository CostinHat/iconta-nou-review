# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d112.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d112.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur, schema):
    cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
    return cur.fetchone()


def select_salariati(cur, schema, _dsal, an, luna):
    cur.execute(f"SELECT * FROM {schema}.salariati WHERE (data_incetare IS NULL OR data_incetare >= %s) "
                f"AND (data_angajare IS NULL OR data_angajare < (%s::date + INTERVAL '1 month')) ORDER BY id", (_dsal(an, luna, 1), _dsal(an, luna, 1)))
    return cur.fetchall()


def select_concedii_medicale(cur, schema, an, luna):
    cur.execute(f"""SELECT * FROM {schema}.concedii_medicale
                WHERE an=%s AND luna=%s""", (an, luna))
    return cur.fetchall()
