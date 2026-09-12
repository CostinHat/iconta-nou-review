# -*- coding: utf-8 -*-
"""REPOSITORY — notele contabile, planul de conturi și perioadele blocate.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def id_nota_dupa_numar(cur, numar):
    cur.execute("SELECT id FROM inregistrari WHERE numar = %s",
                (numar,))
    return cur.fetchone()


def id_nota_dupa_numar_2(cur, numar):
    cur.execute("SELECT id FROM inregistrari WHERE numar = %s",
                (numar,))
    return cur.fetchone()


def nota_de_amortizare(cur, schema, numar):
    cur.execute(f"""
                SELECT numar FROM {schema}.inregistrari
                WHERE sursa = 'amortizare' AND numar = %s
            """,
                (numar,))
    return cur.fetchone()


def jurnal_pe_an(cur, schema, an, limita):
    cur.execute(f"""
                WITH pe_an AS (
                    SELECT id, data, numar, descriere, sursa, status, factura_id, document_ref,
                           ROW_NUMBER() OVER (ORDER BY data, id) AS nr_curent
                    FROM {schema}.inregistrari
                    WHERE date_trunc('year', data) = %s
                )
                SELECT n.id, n.data, n.numar, n.descriere, n.sursa, n.status, n.factura_id,
                       n.document_ref, n.nr_curent,
                       f.tip, f.serie, f.numar, f.data_emitere,
                       l.cont_debit, l.cont_credit, l.suma, l.centru_cost_id, cc.nume AS centru_nume
                FROM pe_an n
                JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = n.id
                LEFT JOIN {schema}.facturi f ON f.id = n.factura_id
                LEFT JOIN {schema}.centre_cost cc ON cc.id = l.centru_cost_id
                WHERE date_trunc('month', n.data) = %s
                ORDER BY n.data, n.id, l.id
            """,
                (an, limita))
    return cur.fetchall()


def linii_pentru_jurnal_marja(cur, schema, an, luna):
    cur.execute(f"""SELECT i.id, i.data, i.descriere, i.status,
                                   l.cont_credit, l.suma, l.id
                            FROM {schema}.inregistrari i
                            JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                            WHERE i.descriere LIKE %s
                              AND to_char(i.data, 'YYYY-MM') = %s
                            ORDER BY i.data, i.id, l.id""",
                (an, luna))
    return cur.fetchall()


def denumirea_contului(cur, simbol):
    cur.execute("SELECT denumire FROM plan_conturi WHERE simbol = %s",
                (simbol,))
    return cur.fetchone()


def rulaj_pe_cont_stoc(cur, schema, cont_debit, cont_credit):
    cur.execute(f"""SELECT COALESCE(SUM(CASE WHEN l.cont_debit=%s THEN l.suma ELSE 0 END),0) AS d,
                                       COALESCE(SUM(CASE WHEN l.cont_credit=%s THEN l.suma ELSE 0 END),0) AS c
                                FROM {schema}.inregistrari_linii l
                                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                                WHERE i.status = 'validata'""",
                (cont_debit, cont_credit))
    return cur.fetchone()


def sold_initial_pe_cont(cur, schema, cont):
    cur.execute(f"""SELECT COALESCE(SUM(sold_debitor - sold_creditor),0) AS si
                                FROM {schema}.solduri_initiale WHERE cont = %s""",
                (cont,))
    return cur.fetchone()


def perioade_blocate(cur, schema):
    cur.execute(f"SELECT an, luna FROM {schema}.perioade_blocate ORDER BY an, luna")
    return cur.fetchall()


def conturi_dupa_text(cur, tipar_simbol, tipar_denumire):
    cur.execute(
        "SELECT simbol, denumire, tip FROM plan_conturi "
        "WHERE simbol ILIKE %s OR denumire ILIKE %s ORDER BY simbol LIMIT 100",
        (tipar_simbol, tipar_denumire))
    return cur.fetchall()


def toate_conturile(cur):
    cur.execute("SELECT simbol, denumire, tip FROM plan_conturi ORDER BY simbol LIMIT 100")
    return cur.fetchall()
