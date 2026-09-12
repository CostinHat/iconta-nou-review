# -*- coding: utf-8 -*-
"""REPOSITORY — portalul clientului: solicitări și clienți.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def cate_solicitari_necitite(cur, tenant_id):
    cur.execute("SELECT count(*) FROM public.solicitari_client "
                "WHERE tenant_id=%s AND autor_rol='cabinet' AND citit=false",
                (tenant_id,))
    return cur.fetchone()


def solicitarile_firmei(cur, tenant_id):
    cur.execute("SELECT id, mesaj, autor_rol, creat_la FROM public.solicitari_client "
                "WHERE tenant_id=%s ORDER BY id",
                (tenant_id,))
    return cur.fetchall()


def solicitarile_pentru_cabinet(cur, tenant_id):
    cur.execute("SELECT id, mesaj, autor_rol, creat_la, citit FROM public.solicitari_client "
                "WHERE tenant_id=%s ORDER BY id",
                (tenant_id,))
    return cur.fetchall()


def clientul_exista(cur, client_id):
    cur.execute("SELECT 1 FROM clienti WHERE id=%s",
                (client_id,))
    return cur.fetchone()
