# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d301_operatiuni_api.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d301_operatiuni_api.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_d301_operatiuni(cur, schema, an, luna):
    cur.execute(f"SELECT id, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva, "
                f"partener_tara, partener_cod, partener_den, temei_307 "
                f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))


def select_firma_profil(cur, schema):
    cur.execute(f"SELECT platitor_tva FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def insert_d301_operatiuni(cur, schema, an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva, partener_tara, partener_cod, partener_den, temei_307):
    cur.execute(f"""INSERT INTO {schema}.d301_operatiuni
                (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva,
                 partener_tara, partener_cod, partener_den, temei_307)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""", (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva,
                     partener_tara, partener_cod, partener_den, temei_307))
    return cur.fetchone()


def delete_d301_operatiuni(cur, schema, op_id, an, luna):
    cur.execute(f"DELETE FROM {schema}.d301_operatiuni WHERE id=%s AND an=%s AND luna=%s", (op_id, an, luna))
