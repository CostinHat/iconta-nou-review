# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/registru_inventar.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/registru_inventar.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_s(cur, schema, exercitiu, date):
    cur.execute("SELECT COALESCE(MAX(nr_curent), 0) + 1 FROM {s}.registru_inventar "
                "WHERE exercitiu = %s AND momentul = %s".format(s=schema), (exercitiu, date["momentul"]))
    return cur.fetchone()


def insert_s(cur, schema, campuri, exercitiu, nr, date):
    cur.execute("INSERT INTO {s}.registru_inventar (exercitiu, momentul, nr_curent, {c}) "
                "VALUES (%s, %s, %s, {p}) RETURNING id".format(
                    s=schema, c=", ".join(campuri), p=", ".join(["%s"] * len(campuri))), [exercitiu, date["momentul"], nr] + [date.get(c) for c in campuri])
    return cur.fetchone()


def select_s_2(cur, schema, exercitiu, momentul):
    cur.execute("SELECT * FROM {s}.registru_inventar WHERE exercitiu = %s AND momentul = %s "
                "ORDER BY nr_curent".format(s=schema), (exercitiu, momentul))
    return cur.fetchall()
