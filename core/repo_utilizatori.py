# -*- coding: utf-8 -*-
"""REPOSITORY — conturile, accesul clienților și urmele lor (`public.users` și tabelele legate).

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:746`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def firme_scoase_din_portofoliu(cur, firm_id):
    cur.execute("SELECT id, tenant_id, nume, cui, schema_name, motiv, randuri_sterse, "
            "       urme_pastrate, scos_de_user_id, scos_la, "
            "       (SELECT u.email FROM public.users u WHERE u.id = fs.scos_de_user_id) AS scos_de "
            "FROM public.firme_scoase fs WHERE cabinet_id = %s "
            "ORDER BY scos_la DESC LIMIT 200",
                (firm_id,))
    return cur.fetchall()


def conturi_client_ale_firmei(cur, tenant_id):
    cur.execute("""SELECT u.id, u.email, u.nume, u.activ FROM public.users u
                           JOIN public.user_tenants ut ON ut.user_id = u.id
                           WHERE ut.tenant_id = %s AND u.rol = 'client' ORDER BY u.id""",
                (tenant_id,))
    return cur.fetchall()


def contul_dupa_email(cur, email):
    cur.execute("SELECT id, rol, activ, accounting_firm_id FROM public.users "
                        "WHERE lower(email)=%s",
                (email,))
    return cur.fetchone()


def id_cont_activ_dupa_email(cur, email):
    cur.execute("SELECT id FROM public.users WHERE email=%s AND activ",
                (email,))
    return cur.fetchone()


def primul_client_al_firmei(cur, tenant_id):
    cur.execute("""SELECT u.id FROM public.users u
                           JOIN public.user_tenants ut ON ut.user_id = u.id
                           WHERE ut.tenant_id=%s AND u.rol='client' AND u.activ=true
                           ORDER BY u.id LIMIT 1""",
                (tenant_id,))
    return cur.fetchone()


def clientii_firmei(cur, tenant_id):
    cur.execute("""SELECT u.id, u.email, u.nume FROM public.users u
                           JOIN public.user_tenants ut ON ut.user_id=u.id
                           WHERE ut.tenant_id=%s AND u.rol='client' ORDER BY u.id""",
                (tenant_id,))
    return cur.fetchall()


def emailul_contului(cur, user_id):
    cur.execute("SELECT email FROM public.users WHERE id=%s",
                (user_id,))
    return cur.fetchone()


def contul_dupa_email_2(cur, email):
    cur.execute("SELECT id, rol, activ, accounting_firm_id FROM public.users "
                        "WHERE lower(email)=%s",
                (email,))
    return cur.fetchone()


def conturi_active_ale_cabinetului(cur, firm_id):
    cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND activ=true "
                    "AND rol IN ('admin_firma', 'angajat')",
                (firm_id,))
    return cur.fetchall()


def id_si_activ_dupa_email(cur, email):
    cur.execute("SELECT id, activ FROM public.users WHERE email=%s",
                (email,))
    return cur.fetchone()


def hash_parola(cur, user_id):
    cur.execute("SELECT password_hash FROM public.users WHERE id = %s",
                (user_id,))
    return cur.fetchone()


def permisiuni(cur, user_id):
    cur.execute("SELECT poate_pregati, poate_valida, poate_depune, rol "
                "FROM public.users WHERE id = %s",
                (user_id,))
    return cur.fetchone()


def cont_din_token_activare(cur, token_hash):
    cur.execute("""SELECT user_id FROM public.tokene_activare
                       WHERE token_hash=%s AND NOT folosit AND expira > now()""",
                (token_hash,))
    return cur.fetchone()


def cont_din_token_activare_2(cur, token_hash):
    cur.execute("""SELECT user_id FROM public.tokene_activare
                           WHERE token_hash=%s AND NOT folosit AND expira > now()""",
                (token_hash,))
    return cur.fetchone()


def schimbare_email_in_asteptare(cur, token_hash):
    cur.execute("SELECT id, user_id, tenant_id, email_vechi, email_nou "
                        "FROM public.schimbari_email "
                        "WHERE token_hash=%s AND confirmat_la IS NULL AND expira > now()",
                (token_hash,))
    return cur.fetchone()


def urme_portal_ale_firmei(cur, tenant_id):
    cur.execute("SELECT actiune, detaliu, autor_id, creat_la FROM public.urme_portal "
                        "WHERE tenant_id=%s ORDER BY creat_la DESC LIMIT 200",
                (tenant_id,))
    return cur.fetchall()


def cate_firme_mai_are_contul(cur, user_id):
    cur.execute("SELECT count(*) AS n FROM public.user_tenants WHERE user_id=%s",
                (user_id,))
    return cur.fetchone()
