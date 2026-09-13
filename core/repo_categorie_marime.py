# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/categorie_marime.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/categorie_marime.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_salariati(cur, schema, an):
    cur.execute(f"""
                    SELECT AVG(n)::numeric FROM (
                        SELECT generate_series(1, 12) AS luna
                    ) l, LATERAL (
                        SELECT COUNT(*) AS n FROM {schema}.salariati s
                         WHERE (s.data_angajare IS NULL
                                OR s.data_angajare < make_date(%s, l.luna, 1) + INTERVAL '1 month')
                           AND (s.data_incetare IS NULL
                                OR s.data_incetare >= make_date(%s, l.luna, 1))
                    ) x
                """, (an, an))
    return cur.fetchone()
