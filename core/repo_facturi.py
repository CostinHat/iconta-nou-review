# -*- coding: utf-8 -*-
"""REPOSITORY — facturile din schema unui tenant.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def tip_si_transformare(cur, factura_id):
    cur.execute("SELECT tip, transformat_in_id FROM facturi WHERE id=%s",
                (factura_id,))
    return cur.fetchone()


def candidate_pentru_bon(cur, schema, cui, total):
    cur.execute(f"""
                SELECT id, numar, serie, data_emitere, total, tert_nume, tert_cui
                FROM {schema}.facturi
                WHERE directie='primita' AND COALESCE(status,'') <> 'anulata' AND platita_la IS NULL
                ORDER BY (upper(replace(COALESCE(tert_cui,''),'RO','')) = %s) DESC,
                         abs(total - %s) ASC, data_emitere DESC
                LIMIT 10
            """,
                (cui, total))
    return cur.fetchall()


def factura_pentru_chitanta(cur, schema, factura_id):
    cur.execute(f"SELECT serie, numar, tert_nume, tert_cui, total, directie, data_emitere FROM {schema}.facturi WHERE id=%s",
                (factura_id,))
    return cur.fetchone()


def pentru_cashflow(cur):
    cur.execute("""SELECT directie, data_emitere, data_scadenta, total
                           FROM facturi WHERE tip='factura' AND storno_din_id IS NULL""")
    return cur.fetchall()


def stare_pentru_recunoastere(cur, schema, factura_id):
    cur.execute(f"SELECT status, directie, (xml IS NOT NULL) FROM {schema}.facturi "
                        f"WHERE id=%s FOR UPDATE",
                (factura_id,))
    return cur.fetchone()


def emise_pe_luni_pentru_intrastat(cur, schema, an):
    cur.execute(f"""SELECT directie, tert_cui,
                                   EXTRACT(MONTH FROM data_emitere)::int AS luna,
                                   COALESCE(total,0) - COALESCE(tva,0) AS baza
                            FROM {schema}.facturi
                            WHERE EXTRACT(YEAR FROM data_emitere) = %s""",
                (an,))
    return cur.fetchall()
