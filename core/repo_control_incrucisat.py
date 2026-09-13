# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/control_incrucisat.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/control_incrucisat.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_inregistrari_linii(cur, schema, data_de, data_pana, conturi):
    cur.execute(f"""
                    SELECT l.cont_debit AS cont, SUM(l.suma) AS s, 'debit' AS sens
                    FROM {schema}.inregistrari_linii l
                    JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                    WHERE i.data >= %s AND i.data < %s AND i.status = 'validata'
                      AND l.cont_debit = ANY(%s)
                    GROUP BY l.cont_debit
                    UNION ALL
                    SELECT l.cont_credit, SUM(l.suma), 'credit'
                    FROM {schema}.inregistrari_linii l
                    JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                    WHERE i.data >= %s AND i.data < %s AND i.status = 'validata'
                      AND l.cont_credit = ANY(%s)
                    GROUP BY l.cont_credit
                """, (data_de, data_pana, list(conturi), data_de, data_pana, list(conturi)))
    return cur.fetchall()


def select_inregistrari_linii_2(cur, schema, de, pana):
    cur.execute(f"""SELECT COALESCE(SUM(l.suma), 0)
                FROM {schema}.inregistrari_linii l
                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                WHERE i.data >= %s AND i.data < %s AND i.status='validata'
                  AND l.cont_debit LIKE '457%%'""", (de, pana))
    return cur.fetchone()


def select_inregistrari(cur, schema, de, pana):
    cur.execute(f"""SELECT 1 FROM {schema}.inregistrari
                WHERE data >= %s AND data < %s AND status='validata' LIMIT 1""", (de, pana))
    return cur.fetchone()


def select(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
    return cur.fetchone()


def select_d301_operatiuni(cur, schema, an):
    cur.execute(f"SELECT DISTINCT luna FROM {schema}.d301_operatiuni WHERE an=%s", (an,))
    return cur.fetchall()


def select_2(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".salariati",))
    return cur.fetchone()


def select_salariati(cur, schema, ultima, prima):
    cur.execute(f"""SELECT 1 FROM {schema}.salariati
                WHERE (data_angajare IS NULL OR data_angajare <= %s)
                  AND (data_incetare IS NULL OR data_incetare >= %s) LIMIT 1""", (ultima, prima))
    return cur.fetchone()


def select_3(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".facturi",))


def select_facturi(cur, schema, an):
    cur.execute(f"SELECT 1 FROM {schema}.facturi WHERE EXTRACT(year FROM data_emitere)=%s LIMIT 1", (an,))
    return cur.fetchone()


def select_4(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".salariati",))


def select_salariati_2(cur, schema, an, _dt):
    cur.execute(f"""SELECT 1 FROM {schema}.salariati
                WHERE (data_angajare IS NULL OR data_angajare <= %s)
                  AND (data_incetare IS NULL OR data_incetare >= %s) LIMIT 1""", (_dt.date(an, 12, 31), _dt.date(an, 1, 1)))
    return cur.fetchone()


def select_5(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".inregistrari",))


def select_inregistrari_2(cur, schema, an):
    cur.execute(f"SELECT 1 FROM {schema}.inregistrari WHERE EXTRACT(year FROM data)=%s LIMIT 1", (an,))
    return cur.fetchone()


def select_6(cur, _tab, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + "." + _tab,))


def select_7(cur, schema, _tab, _unde, an):
    cur.execute(f"SELECT 1 FROM {schema}.{_tab} WHERE {_unde} LIMIT 1", (an,))
    return cur.fetchone()


def select_inregistrari_3(cur, schema, inceput, sfarsit):
    cur.execute(f"""
                    SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume,
                           EXISTS (SELECT 1 FROM {schema}.inregistrari ic
                                   WHERE ic.factura_id = f.id AND ic.status = 'ciorna') AS are_ciorna
                    FROM {schema}.facturi f
                    WHERE f.data_emitere >= %s AND f.data_emitere < %s
                      AND NOT EXISTS (
                            SELECT 1 FROM {schema}.inregistrari i
                            LEFT JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                            WHERE i.factura_id = f.id AND i.status = 'validata'
                              AND ( COALESCE(f.tva, 0) = 0
                                 OR COALESCE(f.taxare_inversa, false) = true
                                 OR (f.directie = 'emisa'   AND l.cont_credit = '4427')
                                 OR (f.directie = 'primita' AND l.cont_debit  = '4426') ) )
                    ORDER BY f.id
                """, (inceput, sfarsit))
    return cur.fetchall()


def select_public(cur, schema):
    cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_2(cur, r):
    cur.execute("SELECT patru_ochi_activ FROM public.accounting_firms WHERE id = %s", (r[0],))
    return cur.fetchone()


def select_inregistrari_4(cur, schema):
    cur.execute(f"""SELECT EXISTS (SELECT 1 FROM {schema}.inregistrari
                WHERE document_ref IS NOT NULL)""")
    return cur.fetchone()


def select_inregistrari_5(cur, schema, inceput, sfarsit, luna, an):
    cur.execute(f"""SELECT count(*) FROM {schema}.inregistrari
                WHERE data >= %s AND data < %s AND status = 'ciorna'
                  AND sursa = 'salarii' AND document_ref = %s""", (inceput, sfarsit, "SAL %02d/%04d" % (luna, an)))
    return cur.fetchone()


def select_public_3(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_4(cur, an, luna, row):
    cur.execute("SELECT xml FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = 'd112' AND an = %s AND luna = %s", (row[0], an, luna))
    return cur.fetchone()


def select_firma_profil(cur, schema):
    cur.execute(f"SELECT platitor_tva, tip_decont FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def select_inregistrari_6(cur, schema, data_de, data_pana):
    cur.execute(f"""
                    SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume, f.data_emitere,
                           c.cui AS c_cui, f.tert_cui,
                           EXISTS (SELECT 1 FROM {schema}.inregistrari i
                                   WHERE i.factura_id = f.id AND i.status = 'validata') AS contabilizata,
                           EXISTS (SELECT 1 FROM {schema}.inregistrari ic
                                   WHERE ic.factura_id = f.id AND ic.status = 'ciorna') AS are_ciorna
                    FROM {schema}.facturi f
                    LEFT JOIN {schema}.clienti c ON c.id = f.client_id
                    WHERE f.data_emitere >= %s AND f.data_emitere < %s
                    ORDER BY f.id
                """, (data_de, data_pana))
    return cur.fetchall()


def select_public_5(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_6(cur, an, luna, row):
    cur.execute("SELECT randuri FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = 'd300' AND an = %s AND luna = %s", (row[0], an, luna))
    return cur.fetchone()


def select_public_7(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_8(cur, row):
    cur.execute("SELECT an, luna, randuri FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = 'd300' ORDER BY an DESC, luna DESC LIMIT 1", (row[0],))
    return cur.fetchone()


def select_firma_profil_2(cur, schema):
    cur.execute(f"SELECT tip_decont FROM {schema}.firma_profil WHERE id = 1")
    return cur.fetchone()


def select_facturi_2(cur, schema, inceput, sfarsit):
    cur.execute(f"""
                    SELECT f.id, f.numar, f.data_emitere, l.cantitate, l.pret_unitar, l.cota_tva
                    FROM {schema}.facturi f
                    JOIN {schema}.factura_linii l ON l.factura_id = f.id
                    WHERE f.directie = 'emisa' AND f.data_emitere >= %s AND f.data_emitere < %s
                    ORDER BY f.id
                """, (inceput, sfarsit))
    return cur.fetchall()


def select_8(cur, schema):
    cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, tip_firma "
                "FROM %s.firma_profil LIMIT 1" % schema)
    return cur.fetchone()


def select_9(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".salariati",))


def select_10(cur, schema):
    cur.execute("SELECT count(*) FROM %s.salariati WHERE "
                "(data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND "
                "(data_angajare IS NULL OR data_angajare <= CURRENT_DATE)" % schema)
    return cur.fetchone()


def select_public_9(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_10(cur, tip, an, row):
    cur.execute("SELECT an, luna, randuri FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = %s AND an = %s ORDER BY luna", (row[0], tip, an))
    return cur.fetchall()


def select_public_11(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_12(cur, row):
    cur.execute("SELECT max(an) FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = 'd101'", (row[0],))
    return cur.fetchone()


def select_inregistrari_linii_3(cur, schema, cont, an):
    cur.execute(f"""
                    SELECT count(*) FROM {schema}.inregistrari_linii l
                    JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                    WHERE i.data >= %s AND i.data < %s AND i.status <> 'validata'
                      AND (l.cont_debit = %s OR l.cont_credit = %s)
                """, ("%d-01-01" % an, "%d-01-01" % (an + 1), cont, cont))
    return cur.fetchone()


def select_public_13(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_14(cur, row):
    cur.execute("""
                SELECT d3.an, d3.luna, d3.randuri, d9.randuri
                FROM public.declaratii_depuse_curente d3
                JOIN public.declaratii_depuse_curente d9
                  ON d9.tenant_id = d3.tenant_id AND d9.an = d3.an AND d9.luna = d3.luna
                 AND d9.tip = 'd394'
                WHERE d3.tenant_id = %s AND d3.tip = 'd300'
                  AND d3.randuri IS NOT NULL AND d9.randuri IS NOT NULL
                ORDER BY d3.an DESC, d3.luna DESC LIMIT 1""", (row[0],))
    return cur.fetchone()


def select_11(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".efactura_trimiteri",))
    return cur.fetchone()


def select_efactura_trimiteri(cur, schema, data_de, data_pana):
    cur.execute(f"""
                    SELECT DISTINCT t.factura_id
                      FROM {schema}.efactura_trimiteri t
                      JOIN {schema}.facturi f ON f.id = t.factura_id
                     WHERE t.stare = 'ok' AND t.mediu = 'prod'
                       AND f.data_emitere >= %s AND f.data_emitere < %s
                """, (data_de, data_pana))
    return cur.fetchall()


def select_public_15(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
    return cur.fetchone()


def select_public_16(cur, row):
    cur.execute("SELECT an, luna, randuri FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = 'd394' AND randuri IS NOT NULL "
                "  AND randuri ? 'facturi_incluse' "
                "ORDER BY an DESC, luna DESC LIMIT 1", (row[0],))
    return cur.fetchone()


def select_firma_profil_3(cur, schema):
    cur.execute(f"SELECT tip_decont FROM {schema}.firma_profil WHERE id = 1")
    return cur.fetchone()
