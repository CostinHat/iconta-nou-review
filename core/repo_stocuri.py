# -*- coding: utf-8 -*-
"""REPOSITORY — articolele și mișcările de stoc.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def articolul_exista(cur, articol_id):
    cur.execute("SELECT 1 FROM articole WHERE id=%s",
                (articol_id,))
    return cur.fetchone()


def articole_cu_cont(cur, schema):
    cur.execute(f"SELECT id, denumire, cont_stoc FROM {schema}.articole ORDER BY id")
    return cur.fetchall()


def miscari_pentru_d406(cur, schema, an):
    cur.execute(f"""SELECT a.id, a.denumire, a.um, a.cont_stoc,
                                   m.data, m.tip, m.cantitate, m.valoare
                            FROM {schema}.articole a
                            JOIN {schema}.miscari_stoc m ON m.articol_id = a.id
                            WHERE m.data <= %s
                            ORDER BY a.id, m.data, m.id""",
                (an,))
    return cur.fetchall()


def miscari_ale_articolului(cur, schema, articol_id):
    cur.execute(f"""SELECT data, tip, cantitate, pret_unitar FROM {schema}.miscari_stoc
                                WHERE articol_id=%s ORDER BY data, id""",
                (articol_id,))
    return cur.fetchall()
