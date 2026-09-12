# -*- coding: utf-8 -*-
"""REPOSITORY — firmele din portofoliu și cabinetele lor (`public.tenants`, `public.accounting_firms`).

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def nume_si_cabinet(cur, tenant_id):
    cur.execute("SELECT nume, accounting_firm_id FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def cui_uri_din_portofoliu(cur, firm_id):
    cur.execute("SELECT cui FROM public.tenants WHERE accounting_firm_id = %s",
                (firm_id,))
    return cur.fetchall()


def creat_la(cur, tenant_id):
    cur.execute("SELECT creat_la FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def cui_dupa_id(cur, tenant_id):
    cur.execute("SELECT cui FROM public.tenants WHERE id = %s",
                (tenant_id,))
    return cur.fetchone()


def nume_si_cui_spatiat(cur, tenant_id):
    cur.execute("SELECT nume, cui FROM public.tenants WHERE id = %s",
                (tenant_id,))
    return cur.fetchone()


def cabinetul_firmei(cur, tenant_id):
    cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def nume_dupa_id(cur, tenant_id):
    cur.execute("SELECT nume FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def nume_dupa_id_2(cur, tenant_id):
    cur.execute("SELECT nume FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def nume_dupa_id_3(cur, tenant_id):
    cur.execute("SELECT nume FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def nume_si_cui(cur, tenant_id):
    cur.execute("SELECT nume, cui FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def firme_pentru_api(cur, firm_id):
    cur.execute("""SELECT id, nume, cui FROM public.tenants
                       WHERE accounting_firm_id=%s ORDER BY nume""",
                (firm_id,))
    return cur.fetchall()


def firme_cu_schema(cur, firm_id):
    cur.execute("""SELECT id, nume, schema_name FROM public.tenants
                       WHERE accounting_firm_id = %s ORDER BY nume""",
                (firm_id,))
    return cur.fetchall()


def cabinetul_si_numele(cur, tenant_id):
    cur.execute("SELECT accounting_firm_id, nume FROM public.tenants WHERE id=%s",
                (tenant_id,))
    return cur.fetchone()


def cabinete_active(cur):
    cur.execute("SELECT id FROM public.accounting_firms WHERE activ")
    return cur.fetchall()


def cabinetul_exista(cur, firm_id):
    cur.execute("SELECT 1 FROM public.accounting_firms WHERE id = %s",
                (firm_id,))
    return cur.fetchone()
