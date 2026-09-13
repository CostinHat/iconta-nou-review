# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d390_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d390_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def sql(cur, q, inceput, sfarsit):
    cur.execute(q, (inceput, sfarsit))
    return cur.fetchall()


def select_s(cur, schema, an, luna):
    cur.execute("SELECT directie, tara, cod, tip FROM {s}.d390_reclasificare "
                "WHERE an=%s AND luna=%s".format(s=schema), (an, luna))
    return cur.fetchall()


def select_s_2(cur, schema, an, luna):
    cur.execute("SELECT tip, tara, cod, den, baza FROM {s}.d390_manual "
                "WHERE an=%s AND luna=%s".format(s=schema), (an, luna))
    return cur.fetchall()


def select(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
    return cur.fetchone()


def select_s_3(cur, schema, an, luna):
    cur.execute("SELECT tip, val_valuta, curs, partener_tara, partener_cod, partener_den "
                "FROM {s}.d301_operatiuni WHERE an=%s AND luna=%s".format(s=schema), (an, luna))
