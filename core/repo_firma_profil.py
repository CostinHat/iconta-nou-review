# -*- coding: utf-8 -*-
"""REPOSITORY — profilul firmei din schema ei (`firma_profil`).

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def profil_fiscal(cur):
    cur.execute("SELECT tip_firma, tip_decont, platitor_tva, operatiuni_ic, regim_fiscal FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def email_firma(cur):
    cur.execute("SELECT email FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def seria_chitantei(cur, schema):
    cur.execute(f"SELECT COALESCE(serie_chitanta, 'CH') FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def config_woocommerce(cur, schema):
    cur.execute(f"SELECT wc_url, (wc_ck IS NOT NULL AND wc_cs IS NOT NULL) AS are_chei FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def cui_firma(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id = 1")
    return cur.fetchone()


def cui_firma_2(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def cui_firma_3(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def platitor_tva(cur, schema):
    cur.execute(f"SELECT COALESCE(platitor_tva, true) FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def platitor_tva_2(cur, schema):
    cur.execute(f"SELECT COALESCE(platitor_tva, true) FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()
