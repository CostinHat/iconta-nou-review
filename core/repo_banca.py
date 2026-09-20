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


def inregistreaza_import(cur, schema, fisier_hash, fisier_nume, nr_linii):
    """[C5] Inregistreaza un import de extras si intoarce id-ul NUMAI daca e nou.

    Cheia UNIQUE pe `fisier_hash` e gardul de idempotenta: `ON CONFLICT DO NOTHING RETURNING id`
    intoarce un rand DOAR la primul import al fisierului. La reimport (dublu-click / raspuns pierdut)
    conflictul face INSERT-ul un no-op si RETURNING nu da nimic -> apelantul stie sa NU insereze
    liniile. E race-safe: constrangerea UNIQUE arbitreaza chiar cursa a doua cereri concurente, nu un
    SELECT-apoi-INSERT verificat separat. `DO NOTHING` (nu suprascriere): randul existent nu se atinge.
    """
    cur.execute(f"""INSERT INTO {schema}.extras_import (fisier_hash, fisier_nume, nr_linii)
                    VALUES (%s,%s,%s) ON CONFLICT (fisier_hash) DO NOTHING RETURNING id""",
                (fisier_hash, (fisier_nume or "")[:255], nr_linii))
    r = cur.fetchone()
    return r[0] if r else None


def import_existent_nr_linii(cur, schema, fisier_hash):
    """[C5] Cate linii avea importul deja existent cu acest hash (pentru mesajul de reimport)."""
    cur.execute(f"SELECT nr_linii FROM {schema}.extras_import WHERE fisier_hash=%s", (fisier_hash,))
    r = cur.fetchone()
    return r[0] if r else None
