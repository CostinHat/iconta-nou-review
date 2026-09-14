# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d390_clasificare_api.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d390_clasificare_api.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def delete_d390_reclasificare(cur, schema, an, luna, directie, tara, cod):
    cur.execute(f"DELETE FROM {schema}.d390_reclasificare "
                f"WHERE an=%s AND luna=%s AND directie=%s AND tara=%s AND cod=%s", (an, luna, directie, tara, cod))


def insert_d390_reclasificare(cur, schema, an, luna, directie, tara, cod, tip):
    # upsert-ok: override reclasificare D390 pe (an,luna,directie,tara,cod) - set intentionat
    # [P7 · D4] motivul a venit aici odata cu instructiunea, din `core/d390_clasificare_api.py`.
    cur.execute(f"""INSERT INTO {schema}.d390_reclasificare (an,luna,directie,tara,cod,tip)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (an,luna,directie,tara,cod) DO UPDATE SET tip=EXCLUDED.tip""", (an, luna, directie, tara, cod, tip))


def select_firma_profil(cur, schema):
    cur.execute(f"SELECT operatiuni_ic FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def insert_d390_manual(cur, schema, an, luna, tip, tara, cod, den, b):
    cur.execute(f"""INSERT INTO {schema}.d390_manual (an,luna,tip,tara,cod,den,baza)
                VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""", (an, luna, tip, tara, cod, den, b))
    return cur.fetchone()


def delete_d390_manual(cur, schema, id, an, luna):
    cur.execute(f"DELETE FROM {schema}.d390_manual WHERE id=%s AND an=%s AND luna=%s", (id, an, luna))
