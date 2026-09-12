# -*- coding: utf-8 -*-
"""REPOSITORY — e-Factura primită și trimiterile către SPV.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def primite_in_asteptare(cur, schema):
    cur.execute(f"""SELECT id, cif_emitent, cif_beneficiar, status, xml_brut, factura_id
                              FROM {schema}.efactura_primite WHERE status IN ('descarcata','ciorna')
                              ORDER BY importat_la DESC LIMIT 100""")
    return cur.fetchall()


def contul_invatat_al_emitentului(cur, schema, cif_emitent):
    cur.execute(f"""SELECT cont_cheltuiala FROM {schema}.efactura_primite
                                WHERE cif_emitent=%s AND cont_cheltuiala IS NOT NULL
                                ORDER BY validat_la DESC NULLS LAST LIMIT 1""",
                (cif_emitent,))
    return cur.fetchone()


def xml_brut(cur, schema, primita_id):
    cur.execute(f"SELECT xml_brut FROM {schema}.efactura_primite WHERE id=%s",
                (primita_id,))
    return cur.fetchone()


def primita_pentru_validare(cur, schema, primita_id):
    cur.execute(f"""SELECT status, xml_brut, cif_beneficiar, factura_id
                              FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE""",
                (primita_id,))
    return cur.fetchone()


def starea_primitei_blocata(cur, schema, primita_id):
    cur.execute(f"SELECT status FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE",
                (primita_id,))
    return cur.fetchone()


def ultima_trimitere_per_factura(cur, schema):
    cur.execute(f"""SELECT DISTINCT ON (factura_id) factura_id, stare, index_incarcare, error_message
                              FROM {schema}.efactura_trimiteri ORDER BY factura_id, id DESC""")
    return cur.fetchall()
