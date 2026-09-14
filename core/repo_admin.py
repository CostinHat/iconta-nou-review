# -*- coding: utf-8 -*-
"""REPOSITORY — panoul de administrare: sănătate, activitate, anunțuri, evenimente publice.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:829`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def activitate_pe_cabinete(cur):
    cur.execute("""
                SELECT f.id, f.nume, f.activ,
                       (SELECT COUNT(*) FROM public.tenants t WHERE t.accounting_firm_id = f.id) AS nr_firme,
                       (SELECT COUNT(*) FROM public.users u2 WHERE u2.accounting_firm_id = f.id
                          AND u2.activ = true AND u2.rol IN ('admin_firma','angajat')) AS nr_angajati,
                       (SELECT COUNT(*) FROM public.audit_log a2 JOIN public.users u3 ON u3.id = a2.user_id
                          WHERE u3.accounting_firm_id = f.id AND a2.actiune LIKE 'POST /recomanda%%') AS nr_recomandari,
                       (SELECT COUNT(*) FROM public.audit_log a5 JOIN public.users u6 ON u6.id = a5.user_id
                          WHERE u6.accounting_firm_id = f.id AND a5.actiune LIKE '%%/facturi/emite%%') AS nr_facturi,
                       (SELECT COUNT(*) FROM public.audit_log a6 JOIN public.users u7 ON u7.id = a6.user_id
                          WHERE u7.accounting_firm_id = f.id AND a6.actiune LIKE '%%/depune%%') AS nr_declaratii,  -- ICRD_CABINETE_CATEGORII_V1
                       MAX(a.created_at) AS ultima_activitate,
                       MAX(a.created_at) FILTER (WHERE a.actiune = 'login') AS ultim_login,
                       COUNT(a.id) AS nr_actiuni,
                       COUNT(a.id) FILTER (WHERE a.actiune = 'login') AS nr_logari
                FROM public.accounting_firms f
                LEFT JOIN public.users u ON u.accounting_firm_id = f.id
                LEFT JOIN public.audit_log a ON a.user_id = u.id
                GROUP BY f.id, f.nume, f.activ
                ORDER BY f.nume
            """)
    return cur.fetchall()


def ultimele_actiuni(cur):
    cur.execute("""
                    SELECT id, actiune, tenant_id, user_id, created_at, detalii
                    FROM public.audit_log
                    WHERE created_at > now() - interval '24 hours'
                      AND (detalii->>'status')::int >= 500
                    ORDER BY created_at DESC
                """)
    return cur.fetchall()


def actiunile_cabinetului(cur, firm_id, limita):
    cur.execute("""
                SELECT a.id, a.actiune, a.tenant_id, a.created_at, u.nume, u.prenume
                FROM public.audit_log a
                JOIN public.users u ON u.id = a.user_id
                WHERE u.accounting_firm_id = %s
                ORDER BY a.created_at DESC
                LIMIT %s
            """,
                (firm_id, limita))
    return cur.fetchall()


def marimea_bazei(cur):
    cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
    return cur.fetchone()


def conexiuni_active(cur):
    cur.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
    return cur.fetchone()


def alerte_fiscale(cur):
    cur.execute("""SELECT id, sursa, titlu, rezumat, url, relevanta, creat_la
                       FROM public.alerte_fiscale WHERE NOT vazut AND sursa != 'anaf_buletin' ORDER BY id DESC LIMIT 30""")
    return cur.fetchall()


def anunturi_pentru_cabinet(cur, firm_id):
    cur.execute("""SELECT id, mesaj, creat_la FROM public.anunturi_cabinet
                       WHERE cabinet_id=%s AND confirmat_la IS NULL AND (data_afisare IS NULL OR data_afisare <= CURRENT_DATE) ORDER BY id""",
                (firm_id,))
    return cur.fetchall()


def istoric_sanatate(cur, ore):
    cur.execute("""
                SELECT ram_procent, disc_procent, load1, conexiuni_db, erori_noi, creat_la
                FROM public.metrici_sanatate
                WHERE creat_la > now() - (%s || ' hours')::interval
                ORDER BY creat_la ASC
            """,
                (ore,))
    return cur.fetchall()


def evenimente_pe_tip(cur, zile):
    cur.execute("SELECT tip, COUNT(*) AS n FROM public.eveniment_public "
                    "WHERE creat_la >= now() - (%s || ' days')::interval GROUP BY tip ORDER BY n DESC",
                (zile,))
    return cur.fetchall()


def evenimente_pe_zi(cur, zile):
    cur.execute("SELECT to_char(date_trunc('day', creat_la), 'YYYY-MM-DD') AS zi, COUNT(*) AS n "
                    "FROM public.eveniment_public WHERE creat_la >= now() - (%s || ' days')::interval "
                    "GROUP BY 1 ORDER BY 1 DESC",
                (zile,))
    return cur.fetchall()


def evenimente_pe_pagina(cur, zile):
    cur.execute("SELECT COALESCE(NULLIF(pagina,''),'landing') AS pagina, COUNT(*) AS n "
                    "FROM public.eveniment_public WHERE creat_la >= now() - (%s || ' days')::interval "
                    "GROUP BY 1 ORDER BY n DESC LIMIT 100",
                (zile,))
    return cur.fetchall()


def cate_evenimente(cur, zile):
    cur.execute("SELECT COUNT(*) AS n FROM public.eveniment_public "
                    "WHERE creat_la >= now() - (%s || ' days')::interval",
                (zile,))
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def adauga_anunt(cur, cabinet_id, mesaj, data_afisare):
    cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj, data_afisare) VALUES (%s,%s,%s)",
                (cabinet_id, mesaj, data_afisare))


def marcheaza_alerta_vazuta(cur, id_):
    cur.execute("UPDATE public.alerte_fiscale SET vazut=true WHERE id=%s RETURNING id",
                (id_,))
    return cur.fetchone()


def confirma_anunt(cur, id_, cabinet_id):
    cur.execute("""UPDATE public.anunturi_cabinet SET confirmat_la=now()
                       WHERE id=%s AND cabinet_id=%s AND confirmat_la IS NULL RETURNING id""",
                (id_, cabinet_id))
    return cur.fetchone()


def scrie_audit_cu_detalii(cur, user_id, actiune, entitate, entitate_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune, entitate, entitate_id, detalii) "
                    "VALUES (%s,'gdpr_export',%s,%s,%s)",
                (user_id, actiune, entitate, entitate_id))


def scrie_audit_login(cur, user_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'login')",
                (user_id,))


def scrie_audit_reset_cerut(cur, user_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'reset_parola_cerut')",
                (user_id,))


def scrie_audit_reset_schimbat(cur, user_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'reset_parola_schimbat')",
                (user_id,))


def scrie_eveniment_public(cur, tip, pagina):
    cur.execute("INSERT INTO public.eveniment_public (tip, pagina) VALUES (%s, %s)",
                (tip, pagina))
