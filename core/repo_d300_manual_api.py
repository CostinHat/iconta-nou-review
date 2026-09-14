# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d300_manual_api.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d300_manual_api.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_d300_manual(cur, schema, an, luna):
    cur.execute(f"SELECT id, rand, baza, tva, descriere FROM {schema}.d300_manual "
                f"WHERE an=%s AND luna=%s ORDER BY id", (an, luna))


def select_firma_profil(cur, schema):
    cur.execute(f"SELECT platitor_tva FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def insert_d300_manual(cur, schema, an, luna, rand, baza, tva, descriere):
    # upsert-ok: editare rand D300 manual pe (an,luna,rand) - re-scrierea aceluiasi rand
    # [P7 · D4] motivul a venit aici odata cu instructiunea, din `core/d300_manual_api.py`.
    cur.execute(f"""INSERT INTO {schema}.d300_manual (an, luna, rand, baza, tva, descriere)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (an, luna, rand)
                DO UPDATE SET baza=EXCLUDED.baza, tva=EXCLUDED.tva,
                              descriere=EXCLUDED.descriere
                RETURNING id""", (an, luna, rand, baza, tva, descriere))
    return cur.fetchone()


def delete_d300_manual(cur, schema, rid):
    cur.execute(f"DELETE FROM {schema}.d300_manual WHERE id=%s", (rid,))


def select_d300_manual_2(cur, schema, an, luna):
    cur.execute(f"SELECT rand, baza, tva FROM {schema}.d300_manual WHERE an=%s AND luna=%s", (an, luna))
    return cur.fetchall()
