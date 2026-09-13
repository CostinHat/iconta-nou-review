# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/control_fiscal_api.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/control_fiscal_api.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".efactura_primite",))


def select_schema(cur, schema):
    cur.execute("SELECT count(*) FROM " + schema + ".efactura_primite "
                "WHERE status = 'descarcata'")
    return cur.fetchone()


def select_firma_profil(cur):
    cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, "
                "platitor_tva_anaf, platitor_tva_anaf_data, tip_firma, platitor_tva_anaf_inceput, "
                "inreg_art317 "
                "FROM firma_profil LIMIT 1")
    return cur.fetchone()


def select_2(cur):
    cur.execute("SELECT to_regclass('salariati')")


def select_salariati(cur):
    cur.execute("SELECT count(*) FROM salariati WHERE (data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND (data_angajare IS NULL OR data_angajare <= CURRENT_DATE)")
    return cur.fetchone()


def select_public(cur, tenant_id):
    cur.execute("SELECT (creat_la AT TIME ZONE 'Europe/Bucharest')::date FROM public.tenants WHERE id=%s", (tenant_id,))
    return cur.fetchone()


def select_facturi(cur, inc, sf):
    cur.execute("SELECT count(*) FROM facturi WHERE directie='emisa' "
                "AND data_emitere >= %s AND data_emitere < %s", (inc.isoformat(), sf.isoformat()))
    return cur.fetchone()


def select_public_2(cur, tenant_id):
    cur.execute("SELECT tip, an, luna, (data_depunere AT TIME ZONE 'Europe/Bucharest')::date AS data_depunere "
                "FROM public.declaratii_depuse_curente WHERE tenant_id=%s", (tenant_id,))
