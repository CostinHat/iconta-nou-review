# -*- coding: utf-8 -*-
"""REPOSITORY — extrasul de cont și liniile lui.

[P7 · V2, 13.09.2026] Scrierile de aici stăteau în corpul rutelor din `main.py`. SQL-ul s-a mutat,
nu s-a rescris: aceleași instrucțiuni, aceiași parametri, aceeași ordine, același `RETURNING`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI și nu face nici `commit`, nici `rollback`: hotarele
tranzacției rămân exact unde erau — la cel care le deținea deja (contractul P4).
"""


def ignora_linia_de_extras(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.extras_linii SET status='ignorat' WHERE id=%s AND status != 'contat' RETURNING id",
                (id_,))
    return cur.fetchone()


def readuce_linia_de_extras(cur, schema, id_):
    cur.execute(f"""UPDATE {schema}.extras_linii SET status='nou'
                            WHERE id=%s AND status='ignorat' RETURNING id""",
                (id_,))
    return cur.fetchone()
