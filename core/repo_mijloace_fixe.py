# -*- coding: utf-8 -*-
"""REPOSITORY — mijloacele fixe din schema unui tenant.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def de_amortizat(cur, schema):
    cur.execute(f"""
                SELECT id, denumire, cont_amortizare, valoare, COALESCE(rezidual,0), dnf_luni,
                       data_pif, cont_imobilizare, metoda
                FROM {schema}.mijloace_fixe WHERE activ = true
            """)
    return cur.fetchall()


def active_pentru_d406(cur, schema, an):
    cur.execute(f"""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                   valoare, rezidual, dnf_luni, data_pif, metoda, activ
                            FROM {schema}.mijloace_fixe
                            WHERE data_pif IS NOT NULL
                              AND EXTRACT(YEAR FROM data_pif) <= %s
                            ORDER BY id""",
                (an,))
    return cur.fetchall()


def pentru_reevaluare(cur, schema, mijloc_id):
    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                           valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda
                                    FROM {schema}.mijloace_fixe WHERE id=%s AND activ=true""",
                (mijloc_id,))
    return cur.fetchone()


def toate(cur):
    cur.execute("""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                  valoare, rezidual, dnf_luni, data_pif, metoda, activ
                           FROM mijloace_fixe ORDER BY activ DESC, id""")
    return cur.fetchall()


def pentru_inventariere(cur, schema, mijloc_id):
    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                               valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda
                                        FROM {schema}.mijloace_fixe
                                        WHERE id=%s AND activ=true""",
                (mijloc_id,))
    return cur.fetchone()
