# -*- coding: utf-8 -*-
"""REPOSITORY — casa: bonuri și chitanțe.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:794`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
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


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def aproba_bonul(cur, schema, comerciant, data_, total, inregistrare_id, id_):
    cur.execute(f"""
                UPDATE {schema}.bonuri SET status='aprobat',
                       comerciant=%s, data=%s, total=%s, inregistrare_id=%s
                WHERE id=%s
            """,
                (comerciant, data_, total, inregistrare_id, id_))


def sterge_bonurile_extrase_vechi(cur, schema):
    cur.execute(f"""DELETE FROM {schema}.bonuri
                            WHERE status='extras' AND creat_la < now() - interval '24 hours'
                            RETURNING id""")
    return cur.fetchall()


def adauga_bon(cur, schema, comerciant, cui, data_, total, tva_11, tva_21, articole, tva, nr_imagini, bon_complet, status, tip, numar_document, mentiuni):
    cur.execute(f"""
                INSERT INTO {schema}.bonuri (comerciant, cui, data, total, tva_11, tva_21, articole, tva, nr_imagini, bon_complet, status, tip, numar_document, mentiuni, orientare)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'extras', %s, %s, %s, %s) RETURNING id
            """,
                (comerciant, cui, data_, total, tva_11, tva_21, articole, tva, nr_imagini, bon_complet, status, tip, numar_document, mentiuni))
    return cur.fetchone()


def trece_bonul_la_de_verificat(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.bonuri SET status='de_verificat' WHERE id=%s AND status='extras' RETURNING id",
                (id_,))
    return cur.fetchone()


def sterge_bonul_extras(cur, schema, id_):
    cur.execute(f"DELETE FROM {schema}.bonuri WHERE id=%s AND status='extras' RETURNING id",
                (id_,))
    return cur.fetchone()


def aproba_bonul_cu_documente(cur, schema, factura_id, casa_operatiune_id, inregistrare_id, comerciant, data_, total, id_):
    cur.execute(f"""UPDATE {schema}.bonuri SET status='aprobat', factura_id=%s,
                            casa_operatiune_id=%s, inregistrare_id=%s,
                            comerciant=%s, data=%s, total=%s WHERE id=%s""",
                (factura_id, casa_operatiune_id, inregistrare_id, comerciant, data_, total, id_))


def adauga_chitanta(cur, schema, serie, numar, data_, factura_id, client_nume, client_cui, suma, reprezentand, casa_operatiune_id, inregistrare_id):
    cur.execute(f"""INSERT INTO {schema}.chitante
                            (serie, numar, data, factura_id, client_nume, client_cui, suma, reprezentand,
                             casa_operatiune_id, inregistrare_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (serie, numar, data_, factura_id, client_nume, client_cui, suma, reprezentand, casa_operatiune_id, inregistrare_id))
    return cur.fetchone()
