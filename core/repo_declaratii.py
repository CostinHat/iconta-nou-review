# -*- coding: utf-8 -*-
"""REPOSITORY — coada declarațiilor și artefactele lor.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def continutul_din_coada(cur, coada_id, tenant_id):
    cur.execute("SELECT tip, payload, (payload->>'_an')::int, (payload->>'_luna')::int "
                        "FROM public.declaratii_coada WHERE id=%s AND cabinet_id=%s",
                (coada_id, tenant_id))
    return cur.fetchone()


def perioada_d300_manual(cur, schema, manual_id):
    cur.execute(f"SELECT an, luna FROM {schema}.d300_manual WHERE id=%s",
                (manual_id,))
    return cur.fetchone()


def trimiteri_etransport(cur, schema):
    cur.execute(f"""SELECT id, stare, uit, data_transport, uit_valabil_pana, intracom, error_message
                              FROM {schema}.etransport_trimiteri WHERE mediu='prod'
                              ORDER BY id DESC LIMIT 50""")
    return cur.fetchall()
