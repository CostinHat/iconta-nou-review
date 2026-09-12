# -*- coding: utf-8 -*-
"""REPOSITORY — casa: bonuri și chitanțe.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def urmatorul_numar_chitanta(cur, schema, serie):
    cur.execute(f"SELECT COALESCE(max(numar), 0) + 1 FROM {schema}.chitante WHERE serie=%s",
                (serie,))
    return cur.fetchone()


def chitanta_pentru_pdf(cur, schema, chitanta_id):
    cur.execute(f"SELECT serie, numar, data, client_nume, client_cui, suma, reprezentand FROM {schema}.chitante WHERE id=%s",
                (chitanta_id,))
    return cur.fetchone()


def tipul_bonului(cur, schema, bon_id):
    cur.execute(f"SELECT tip FROM {schema}.bonuri WHERE id=%s",
                (bon_id,))
    return cur.fetchone()


def cui_si_total_bon(cur, schema, bon_id):
    cur.execute(f"SELECT cui, total FROM {schema}.bonuri WHERE id=%s",
                (bon_id,))
    return cur.fetchone()


def tip_si_status_bon(cur, schema, bon_id):
    cur.execute(f"SELECT tip, status FROM {schema}.bonuri WHERE id=%s",
                (bon_id,))
    return cur.fetchone()


def chitante_ale_facturii(cur, schema, factura_id):
    cur.execute(f"SELECT id, serie, numar, data, suma, client_nume FROM {schema}.chitante WHERE factura_id=%s AND NOT anulata ORDER BY id DESC",
                (factura_id,))
    return cur.fetchall()


def chitante_toate(cur, schema):
    cur.execute(f"SELECT id, serie, numar, data, suma, client_nume FROM {schema}.chitante WHERE NOT anulata ORDER BY id DESC LIMIT 100")
    return cur.fetchall()


def bonuri_de_verificat(cur, schema):
    cur.execute(f"""
                SELECT id, comerciant, cui, data, total, tva_11, tva_21, articole, status, nr_imagini, tip, numar_document, mentiuni, tva, creat_la, orientare
                FROM {schema}.bonuri WHERE status = 'de_verificat' ORDER BY creat_la DESC
            """)
    return cur.fetchall()
