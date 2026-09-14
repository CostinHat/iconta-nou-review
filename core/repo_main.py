# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `main.py`.

[P7 · valul D4, 13.09.2026] Statele in `main.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def sql(cur):
    cur.execute("SHOW timezone")
    return cur.fetchone()


def select_u(cur, ctx):
    cur.execute("""SELECT af.activ, extract(epoch FROM u.sesiuni_valide_de) FROM public.users u
                LEFT JOIN public.accounting_firms af ON af.id = u.accounting_firm_id
                WHERE u.id = %s""", (ctx["uid"],))
    return cur.fetchone()


def insert_public(cur, uid, tenant_id, actiune, _json_audit, status):
    cur.execute("INSERT INTO public.audit_log (user_id, tenant_id, actiune, detalii) "
                "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), %s, %s)", (uid, tenant_id, actiune, _json_audit.dumps({"status": status})))


def select_pg_stat_activity(cur):
    cur.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
    return cur.fetchone()


def select_public(cur):
    cur.execute("""
                    SELECT count(*) FROM public.audit_log
                    WHERE created_at > now() - interval '10 minutes'
                      AND (detalii->>'status')::int >= 500
                """)
    return cur.fetchone()


def select_public_2(cur):
    cur.execute("SELECT email FROM public.users WHERE rol='superadmin' AND activ=true ORDER BY id LIMIT 1")
    return cur.fetchone()


def insert_public_2(cur, m):
    cur.execute("INSERT INTO public.metrici_sanatate "
                "(ram_procent, disc_procent, load1, conexiuni_db, erori_noi) "
                "VALUES (%s,%s,%s,%s,%s)", (m["ram_procent"], m["disc_procent"], m["load1"], m["conexiuni_db"], m["erori_noi"]))


def select_public_3(cur, tenant_id):
    cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (tenant_id,))
    return cur.fetchone()


def delete_public(cur):
    cur.execute("DELETE FROM public.tokene_activare WHERE expira < now() OR folosit = true")


def insert_public_3(cur, user_id, interval_sql, _hash_tok, tok):
    cur.execute("INSERT INTO public.tokene_activare (token_hash, user_id, expira) "
                "VALUES (%s, %s, now() + (%s)::interval)", (_hash_tok(tok), user_id, interval_sql))


def select_firma_profil(cur):
    cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, tip_firma, "
                "platitor_tva_anaf_inceput, inreg_art317 FROM firma_profil LIMIT 1")
    return cur.fetchone()


def select(cur):
    cur.execute("SELECT to_regclass('salariati')")


def select_salariati(cur):
    cur.execute("SELECT count(*) FROM salariati WHERE (data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND (data_angajare IS NULL OR data_angajare <= CURRENT_DATE)")
    return cur.fetchone()


def select_public_4(cur, tid):
    cur.execute("SELECT tip, an, luna FROM public.declaratii_depuse_curente WHERE tenant_id=%s", (tid,))
    return cur.fetchall()


def select_firma_profil_2(cur):
    cur.execute("SELECT platitor_tva FROM firma_profil LIMIT 1")
    return cur.fetchone()


def select_facturi(cur, factura_id):
    cur.execute("SELECT moneda FROM facturi WHERE id=%s", (factura_id,))
    return cur.fetchone()


def select_public_5(cur, coada_id):
    cur.execute("SELECT tip, perioada, creat_de_id, cabinet_id FROM public.declaratii_coada WHERE id=%s", (coada_id,))
    return cur.fetchone()


def select_public_6(cur, tenant_id):
    cur.execute("SELECT u.email FROM public.users u JOIN public.user_tenants ut ON ut.user_id=u.id "
                "WHERE ut.tenant_id=%s AND u.rol='client' AND u.activ=true LIMIT 1", (tenant_id,))
    return cur.fetchone()


def select_public_7(cur, tenant_id):
    cur.execute("SELECT nume FROM public.tenants WHERE id=%s", (tenant_id,))
    return cur.fetchone()


def select_public_8(cur, tenant_id):
    cur.execute("""SELECT u.id FROM public.users u
                JOIN public.user_tenants ut ON ut.user_id = u.id
                WHERE ut.tenant_id = %s AND u.rol = 'client'
                ORDER BY u.id LIMIT 1""", (tenant_id,))
    return cur.fetchone()


def select_public_9(cur, email, exclude_user_id):
    cur.execute("SELECT id FROM public.users WHERE lower(email)=%s AND id<>%s", (email, exclude_user_id))
    return cur.fetchone()


def insert_public_4(cur, tenant_id, actiune, detaliu, autor_id):
    cur.execute("INSERT INTO public.urme_portal (tenant_id, actiune, detaliu, autor_id) "
                "VALUES (%s, %s, %s, %s)", (tenant_id, actiune, detaliu, autor_id))


def select_public_10(cur, tenant_id, tip, perioada):
    cur.execute("SELECT 1 FROM public.declaratii_coada "
                "WHERE tenant_id=%s AND tip=%s AND perioada=%s LIMIT 1", (tenant_id, tip, perioada))
    return cur.fetchone()


def select_public_11(cur, tenant_id, tip, an, luna):
    cur.execute("SELECT 1 FROM public.declaratii_depuse "
                "WHERE tenant_id=%s AND tip=%s AND an=%s AND luna=%s LIMIT 1", (tenant_id, tip, an, luna))
    return cur.fetchone()


def select_inregistrari(cur, schema, nota_id):
    cur.execute(f"SELECT data FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    return cur.fetchone()


def select_facturi_2(cur, schema, sfarsit, _d, an, luna):
    cur.execute(f"""SELECT count(*) FROM {schema}.facturi
                WHERE status IN ('ciorna','de_recunoscut')
                  AND data_emitere >= %s AND data_emitere < %s""", (_d(an, luna, 1), sfarsit))
    return cur.fetchone()


def select_inregistrari_2(cur, schema, sfarsit, _d, an, luna):
    cur.execute(f"""SELECT count(*) FROM {schema}.inregistrari
                WHERE status='ciorna' AND data >= %s AND data < %s""", (_d(an, luna, 1), sfarsit))
    return cur.fetchone()


def select_2(cur, schema, numar, _SURSE_Z):
    cur.execute("SELECT id, data, sursa FROM %s.inregistrari "
                "WHERE sursa = ANY(%%s) AND numar = %%s LIMIT 1" % schema, (list(_SURSE_Z), numar))
    return cur.fetchone()


def select_bonuri(cur, schema):
    cur.execute(f"""SELECT count(*) FROM {schema}.bonuri
                WHERE status='de_verificat' AND creat_la < now() - interval '3 days'""")
    return cur.fetchone()


def select_casa_operatiuni(cur, schema):
    cur.execute(f"""SELECT count(*) FROM {schema}.casa_operatiuni co
                JOIN {schema}.inregistrari i ON i.id = co.inregistrare_id
                WHERE i.status='ciorna' AND co.creat_la < now() - interval '3 days'""")
    return cur.fetchone()


def select_inregistrari_linii(cur, schema, sfarsit):
    cur.execute(f"""
                    SELECT l.cont_debit, l.cont_credit, l.suma
                    FROM {schema}.inregistrari_linii l
                    JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                    WHERE i.data < %s
                """, (sfarsit,))
    return cur.fetchall()


def select_solduri_initiale(cur, schema):
    cur.execute(f"SELECT cont, SUM(sold_debitor) - SUM(sold_creditor) FROM {schema}.solduri_initiale GROUP BY cont")
    return cur.fetchall()


def select_public_12(cur, tenant_id, actx):
    cur.execute("""SELECT schema_name FROM public.tenants
                WHERE id=%s AND accounting_firm_id=%s""", (tenant_id, actx["firm"]))
    return cur.fetchone()


def select_public_13(cur, flag, ctx):
    cur.execute("SELECT %s FROM public.users WHERE id = %%s" % flag, (ctx["uid"],))
    return cur.fetchone()


def insert_public_5(cur, uid, tenant_id, fapt, _json_audit):
    cur.execute("INSERT INTO public.audit_log (user_id, tenant_id, actiune, detalii) "
                "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), %s, %s)", (uid, tenant_id, "DEZLEGARE nota-factura", _json_audit.dumps(fapt)))


def select_facturi_3(cur, schema, f):
    cur.execute(f"""SELECT id FROM {schema}.facturi
                WHERE numar=%s AND COALESCE(tert_cui,'')=%s AND data_emitere=%s""", (f["numar"], f["tert_cui"], f["data_emitere"]))
    return cur.fetchone()


def insert_facturi(cur, schema, _stare, f):
    cur.execute(f"""INSERT INTO {schema}.facturi
                (numar, data_emitere, data_scadenta, total, tva, moneda, directie, status,
                 xml, tert_nume, tert_cui)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""", (f["numar"], f["data_emitere"], f["data_scadenta"], f["total"], f["tva"],
                 f["moneda"], f["directie"], _stare, f["xml"], (f["tert_nume"] or "")[:255],
                 (f["tert_cui"] or "")[:30]))
    return cur.fetchone()


def insert_factura_linii(cur, schema, fid, ln):
    cur.execute(f"""INSERT INTO {schema}.factura_linii
                (factura_id, descriere, cantitate, pret_unitar, cota_tva)
                VALUES (%s,%s,%s,%s,%s)""", (fid, ln["descriere"][:255], ln["cantitate"], ln["pret_unitar"], ln["cota_tva"]))
