# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/registru_evidenta_fiscala.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/registru_evidenta_fiscala.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_s(cur, schema, an, date):
    cur.execute("SELECT COALESCE(MAX(nr_crt), 0) + 1 FROM {s}.registru_fiscal_pf "
                "WHERE an = %s AND categorie_venit = %s AND sursa_venit = %s".format(s=schema), (an, str(date["categorie"]), date["sursa_venit"]))
    return cur.fetchone()


def insert_s(cur, schema, an, nr, date):
    cur.execute("INSERT INTO {s}.registru_fiscal_pf (an, categorie_venit, sursa_venit, nr_crt, "
                "venit_brut, cheltuieli_deductibile, rectificare, motiv_rectificare) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id".format(s=schema), (an, str(date["categorie"]), date["sursa_venit"], nr,
             date["venit_brut"], date.get("cheltuieli_deductibile") or 0,
             bool(date.get("rectificare")), date.get("motiv_rectificare")))
    return cur.fetchone()


def select_s_2(cur, schema, an):
    cur.execute("SELECT * FROM {s}.registru_fiscal_pf WHERE an = %s "
                "ORDER BY categorie_venit, sursa_venit, nr_crt".format(s=schema), (an,))
    return cur.fetchall()
