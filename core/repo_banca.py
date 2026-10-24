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
    # [lotul 12, 479] o notă propusă pe același cont la debit și la credit (5121=5121, de dinainte de reparație) nu se readuce cu linia
    cur.execute(f"""UPDATE {schema}.extras_linii SET status='nou',
                            nota_propusa = CASE WHEN split_part(nota_propusa->>'debit', '.', 1) = split_part(nota_propusa->>'credit', '.', 1)
                                                THEN NULL ELSE nota_propusa END
                            WHERE id=%s AND status='ignorat' RETURNING id""",
                (id_,))
    return cur.fetchone()


def inregistreaza_import(cur, schema, fisier_hash, fisier_nume, nr_linii):
    """[C5] Registrul fișierelor de extras importate: un rând per conținut (UNIQUE pe `fisier_hash`; același fișier a doua oară nu
    adaugă rând). Întoarce id-ul rândului nou sau None. [16.10.2026, lotul 6 pct.1, 277] NU mai decide duplicatul — îl decide
    mișcarea (`reconciliere_api.cheie_miscare`); un fișier cu aceiași octeți ca unul vechi nu mai respinge liniile.
    """
    cur.execute(f"""INSERT INTO {schema}.extras_import (fisier_hash, fisier_nume, nr_linii)
                    VALUES (%s,%s,%s) ON CONFLICT (fisier_hash) DO NOTHING RETURNING id""",
                (fisier_hash, (fisier_nume or "")[:255], nr_linii))
    r = cur.fetchone()
    return r[0] if r else None
