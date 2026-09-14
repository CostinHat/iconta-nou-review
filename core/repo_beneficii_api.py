# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/beneficii_api.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/beneficii_api.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_salariati(cur, schema, salariat_id):
    cur.execute(f"SELECT 1 FROM {schema}.salariati WHERE id = %s", (salariat_id,))
    return cur.fetchone()


def delete_beneficii_lunare(cur, schema, salariat_id, an, luna, tip, eveniment):
    cur.execute(f"DELETE FROM {schema}.beneficii_lunare "
                f"WHERE salariat_id=%s AND an=%s AND luna=%s AND tip=%s AND eveniment=%s", (salariat_id, an, luna, tip, eveniment))


def insert_beneficii_lunare(cur, schema, salariat_id, an, luna, tip, v, eveniment):
    # upsert-ok: set beneficiu pe (salariat,an,luna,tip,eveniment) - re-setare intentionata
    # [P7 · D4] motivul a venit aici odata cu instructiunea, din `core/beneficii_api.py`.
    cur.execute(f"""INSERT INTO {schema}.beneficii_lunare (salariat_id, an, luna, tip, valoare, eveniment)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (salariat_id, an, luna, tip, eveniment)
                DO UPDATE SET valoare = EXCLUDED.valoare""", (salariat_id, an, luna, tip, v, eveniment))


def select_beneficii_lunare(cur, schema, an, luna, tip):
    cur.execute(f"""SELECT salariat_id, COALESCE(SUM(valoare),0) FROM {schema}.beneficii_lunare
                WHERE an=%s AND luna=%s AND tip=%s GROUP BY salariat_id""", (an, luna, tip))
    return cur.fetchall()


def select_beneficii_lunare_2(cur, schema, an, luna):
    cur.execute(f"""SELECT salariat_id, eveniment, valoare FROM {schema}.beneficii_lunare
                WHERE an=%s AND luna=%s AND tip='cadou' ORDER BY salariat_id, eveniment""", (an, luna))


def select_beneficii_lunare_3(cur, schema, salariat_id, an, tip, pana_luna):
    cur.execute(f"""SELECT COALESCE(SUM(valoare),0) FROM {schema}.beneficii_lunare
                WHERE salariat_id=%s AND an=%s AND tip=%s AND luna<=%s""", (salariat_id, an, tip, pana_luna))
    return cur.fetchone()
