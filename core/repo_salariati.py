# -*- coding: utf-8 -*-
"""REPOSITORY — salariații și cheile REGES ale firmei.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:829`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def salariatul_exista(cur, salariat_id):
    cur.execute("SELECT 1 FROM salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def salariatul_exista_2(cur, salariat_id):
    cur.execute("SELECT 1 FROM salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def salariatul_exista_3(cur, salariat_id):
    cur.execute("SELECT 1 FROM salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def identitate_pentru_reges(cur, schema, salariat_id):
    cur.execute(f"SELECT cnp, nume, prenume FROM {schema}.salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def firma_are_chei_reges(cur, tenant_id):
    cur.execute("SELECT 1 FROM public.reges_chei WHERE tenant_id=%s",
                (tenant_id,))
    return cur.fetchone()


def chei_reges(cur, tenant_id):
    cur.execute("SELECT username, parola, mediu, author_id FROM public.reges_chei WHERE tenant_id=%s",
                (tenant_id,))
    return cur.fetchone()


def chei_reges_fara_autor(cur, tenant_id):
    cur.execute("SELECT username, parola, mediu FROM public.reges_chei WHERE tenant_id=%s",
                (tenant_id,))
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def salveaza_cheile_reges(cur, tenant_id, username, parola, mediu):
    # upsert-ok: salvare credentiale REGES per tenant - update intentionat al aceleiasi chei (tenant_id)
    cur.execute("""INSERT INTO public.reges_chei (tenant_id, username, parola, mediu)
                           VALUES (%s,%s,%s,%s)
                           ON CONFLICT (tenant_id) DO UPDATE
                           SET username=EXCLUDED.username, parola=EXCLUDED.parola,
                               mediu=EXCLUDED.mediu""",
                (tenant_id, username, parola, mediu))


def scrie_mesaj_reges(cur, tenant_id, salariat_id, operatie, message_id, response_id):
    cur.execute("""INSERT INTO public.reges_mesaje
                           (tenant_id, salariat_id, operatie, message_id, response_id, raspuns)
                           VALUES (%s,%s,'InregistrareSalariat',%s,%s,%s) RETURNING id""",
                (tenant_id, salariat_id, operatie, message_id, response_id))
    return cur.fetchone()


def scrie_raspunsul_reges(cur, raspuns, referinta_salariat, referinta_contract, message_id, tenant_id):
    cur.execute("""UPDATE public.reges_mesaje
                               SET status='raspuns', raspuns=%s,
                                   referinta_salariat=COALESCE(%s::uuid, referinta_salariat),
                                   referinta_contract=COALESCE(%s::uuid, referinta_contract)
                               WHERE message_id=%s::uuid AND tenant_id=%s""",
                (raspuns, referinta_salariat, referinta_contract, message_id, tenant_id))
