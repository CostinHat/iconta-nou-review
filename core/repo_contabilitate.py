# -*- coding: utf-8 -*-
"""REPOSITORY — notele contabile, planul de conturi și perioadele blocate.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def id_nota_dupa_numar(cur, numar):
    cur.execute("SELECT id FROM inregistrari WHERE numar = %s",
                (numar,))
    return cur.fetchone()


def liniile_si_data(cur, nota_id):
    """[retest 08.10 pct.1] (data, [(debit, credit, sumă)] sortate) ale unei note — aceeași formă ca amprenta din coadă."""
    cur.execute("SELECT data::text FROM inregistrari WHERE id = %s", (nota_id,))
    d = cur.fetchone()
    cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s", (nota_id,))
    return ((d[0] if not isinstance(d, dict) else d["data"]) if d else None,
            sorted(tuple(x) if not isinstance(x, dict) else (x["cont_debit"], x["cont_credit"], x["suma"]) for x in cur.fetchall()))


def id_nota_dupa_numar_2(cur, numar):
    cur.execute("SELECT id FROM inregistrari WHERE numar = %s",
                (numar,))
    return cur.fetchone()


def nota_de_amortizare(cur, schema, numar):
    """(id,) al notei de amortizare a lunii (`AMORT-AAAA-LL`), sau None."""
    cur.execute(f"""
                SELECT id FROM {schema}.inregistrari
                WHERE sursa = 'amortizare' AND numar = %s ORDER BY id
            """,
                (numar,))
    return cur.fetchone()


def ciorne_altui(cur, schema, nota_ids, uid):
    """[deficiența 246] [(nota_id, autorul)] — ciornele dintre `nota_ids` care, pentru utilizatorul `uid`, sunt ale ALTUI utilizator
    (regula unică `ciorna_altui` din bază, core/migrare_ciorne_proprii.py)."""
    if not nota_ids:
        return []
    cur.execute(f"""SELECT id, {schema}.ciorna_altui(creat_de_id, %s) FROM {schema}.inregistrari
                    WHERE id = ANY(%s) AND status <> 'validata' AND {schema}.ciorna_altui(creat_de_id, %s) IS NOT NULL""",
                (uid, list(nota_ids), uid))
    return [(r[0], r[1]) if not isinstance(r, dict) else (r["id"], r["ciorna_altui"]) for r in cur.fetchall()]


def jurnal_pe_an(cur, schema, an, limita):
    cur.execute(f"""
                WITH pe_an AS (
                    -- [deficiența 302] `nr_curent` e cel PĂSTRAT, dat la validare (core/migrare_nr_curent_note.py); ciorna n-are număr
                    SELECT i.id, i.data, i.numar, i.descriere, i.sursa, i.status, i.factura_id, i.document_ref, r.nr_curent
                    FROM {schema}.inregistrari i
                    LEFT JOIN {schema}.registru_jurnal_numere r ON r.inregistrare_id = i.id
                    WHERE date_trunc('year', i.data) = %s
                )
                SELECT n.id, n.data, n.numar, n.descriere, n.sursa, n.status, n.factura_id,
                       n.document_ref, n.nr_curent,
                       f.tip, f.serie, f.numar, f.data_emitere,
                       l.cont_debit, l.cont_credit, l.suma, l.centru_cost_id, cc.nume AS centru_nume,
                       l.partener_cui, l.partener_nume   -- [381] partenerul pe linia de terți
                FROM pe_an n
                JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = n.id
                LEFT JOIN {schema}.facturi f ON f.id = n.factura_id
                LEFT JOIN {schema}.centre_cost cc ON cc.id = l.centru_cost_id
                WHERE date_trunc('month', n.data) = %s
                ORDER BY n.data, n.id, l.id
            """,
                (an, limita))
    return cur.fetchall()


def linii_pentru_jurnal_marja(cur, schema, an, luna):
    cur.execute(f"""SELECT i.id, i.data, i.descriere, i.status,
                                   l.cont_credit, l.suma, l.id
                            FROM {schema}.inregistrari i
                            JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                            WHERE i.descriere LIKE %s
                              AND to_char(i.data, 'YYYY-MM') = %s
                            ORDER BY i.data, i.id, l.id""",
                (an, luna))
    return cur.fetchall()


def denumirea_contului(cur, simbol):
    cur.execute("SELECT denumire FROM plan_conturi WHERE simbol = %s",
                (simbol,))
    return cur.fetchone()


def rulaj_pe_cont_stoc(cur, schema, cont_debit, cont_credit):
    cur.execute(f"""SELECT COALESCE(SUM(CASE WHEN l.cont_debit=%s THEN l.suma ELSE 0 END),0) AS d,
                                       COALESCE(SUM(CASE WHEN l.cont_credit=%s THEN l.suma ELSE 0 END),0) AS c
                                FROM {schema}.inregistrari_linii l
                                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                                WHERE i.status = 'validata'""",
                (cont_debit, cont_credit))
    return cur.fetchone()


def sold_initial_pe_cont(cur, schema, cont):
    cur.execute(f"""SELECT COALESCE(SUM(sold_debitor - sold_creditor),0) AS si
                                FROM {schema}.solduri_initiale WHERE cont = %s""",
                (cont,))
    return cur.fetchone()


def perioade_blocate(cur, schema):
    cur.execute(f"SELECT an, luna FROM {schema}.perioade_blocate ORDER BY an, luna")
    return cur.fetchall()


def conturi_dupa_inceputul_simbolului(cur, prefix):
    """[deficiența 219] Conturile al căror simbol ÎNCEPE cu prefixul („73” -> 7xx din clasa 73…, nu 473)."""
    cur.execute("SELECT simbol, denumire, tip FROM plan_conturi WHERE simbol LIKE %s ORDER BY simbol LIMIT 100",
                (prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%",))
    return cur.fetchall()


def conturi_dupa_text(cur, tipar_simbol, tipar_denumire):
    cur.execute(
        "SELECT simbol, denumire, tip FROM plan_conturi "
        "WHERE simbol ILIKE %s OR denumire ILIKE %s ORDER BY simbol LIMIT 100",
        (tipar_simbol, tipar_denumire))
    return cur.fetchall()


def toate_conturile(cur):
    """[Retest 2 pct.13] TOT planul (≈700 de conturi): ecranul planului de conturi îl arată întreg, cu analiticele sub sintetic.
    Căutarea (`conturi_dupa_text`) rămâne plafonată."""
    cur.execute("SELECT simbol, denumire, tip FROM plan_conturi ORDER BY simbol")
    return cur.fetchall()


def conturi_cu_sold_initial(cur, simboluri):
    """[deficiența 218] Simbolurile cu sold inițial (de preluare) nenul — un cont cu sold nu se șterge din plan."""
    cur.execute("SELECT DISTINCT cont FROM solduri_initiale WHERE cont = ANY(%s) AND (sold_debitor <> 0 OR sold_creditor <> 0)",
                (list(simboluri),))
    return {r[0] for r in cur.fetchall()}


def conturi_folosite(cur, simboluri=None):
    """Simbolurile care apar pe o linie de notă (orice stare: o ciornă e tot evidență în lucru). [Retest 2 pct.13] „un cont folosit
    în note nu se poate șterge” (decizia Costin O12)."""
    if simboluri is None:
        cur.execute("SELECT cont_debit FROM inregistrari_linii UNION SELECT cont_credit FROM inregistrari_linii")
    else:
        cur.execute("SELECT cont_debit FROM inregistrari_linii WHERE cont_debit = ANY(%s) "
                    "UNION SELECT cont_credit FROM inregistrari_linii WHERE cont_credit = ANY(%s)", (list(simboluri), list(simboluri)))
    return {r[0] for r in cur.fetchall()}


def sterge_cont_din_plan(cur, simbol):
    cur.execute("DELETE FROM plan_conturi WHERE simbol = %s", (simbol,))
    return cur.rowcount


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def adauga_cont_in_plan(cur, simbol, denumire, tip):
    cur.execute("INSERT INTO plan_conturi (simbol, denumire, tip) VALUES (%s, %s, %s)",
                (simbol, denumire, tip))


def nota_bon_ciorna(cur, schema, data_, numar, descriere, document_ref=None):
    """[08.10.2026, decizia Costin §6 pct.7 — R36] „evidența = ce a validat un om”: nota bonului aprobat intră CIORNĂ; validarea e actul
    separat (coada / jurnalul), ca la orice notă scrisă dintr-un document."""
    cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status, document_ref)
                VALUES (%s, %s, %s, 'bon', 'ciorna', %s) RETURNING id
            """,
                (data_, numar, descriere, document_ref))
    return cur.fetchone()


def adauga_linie_credit_casa(cur, schema, inregistrare_id, cont_debit, cont_credit):
    cur.execute(f"INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, '5311', %s)",
                (inregistrare_id, cont_debit, cont_credit))


def adauga_linie_tva_din_casa(cur, schema, inregistrare_id, cont_debit):
    cur.execute(f"INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4426', '5311', %s)",
                (inregistrare_id, cont_debit))


def nota_cu_sursa_si_status(cur, data_, numar, descriere, sursa, status, document_ref=None):
    cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status, document_ref) "
                        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (data_, numar, descriere, sursa, status, document_ref))
    return cur.fetchone()


def adauga_linie_fara_schema(cur, inregistrare_id, cont_debit, cont_credit, suma):
    cur.execute("INSERT INTO inregistrari_linii "
                            "(inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                (inregistrare_id, cont_debit, cont_credit, suma))


def _cu_document_intern(cur, schema, tip, data_, rand):
    """[06.10.2026, comanda Costin §6.2] Nota scrisă de aplicație fără document extern primește documentul intern al operației
    (Legea 82/1991 art.6 alin.(1)), numerotat în aceeași tranzacție. Întoarce rândul `RETURNING id` neschimbat."""
    from core import documente_interne as _di
    _di.genereaza(cur, schema, tip, data_, [rand[0] if not isinstance(rand, dict) else rand["id"]])
    return rand


def nota_amortizare_ciorna(cur, schema, data_, numar, descriere, document_ref=None):
    """[08.10.2026, deciziile Costin §6 pct.6 + pct.7 — R36] nota de amortizare intră CIORNĂ („evidența = ce a validat un om”); o ciornă
    nevalidată se înlocuiește la regenerare (clasa T1, retest 08.10 pct.1), cea validată nu se atinge (`uc_tenants.tenant_amortizare`). `document_ref` =
    tabloul ciornei înlocuite: nota nouă îl preia, fără un număr nou (numerotarea documentelor interne rămâne fără goluri)."""
    cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status, document_ref)
                VALUES (%s, %s, %s, 'amortizare', 'ciorna', %s) RETURNING id
            """,
                (data_, numar, descriere, document_ref))
    r = cur.fetchone()
    return r if document_ref else _cu_document_intern(cur, schema, "tablou_amortizare", data_, r)


def documentul_notei(cur, schema, nota_id):
    """`document_ref` al notei, sau None."""
    cur.execute(f"SELECT document_ref FROM {schema}.inregistrari WHERE id = %s", (nota_id,))
    r = cur.fetchone()
    return (r["document_ref"] if isinstance(r, dict) else r[0]) if r else None


def adauga_linie_cheltuiala_amortizare(cur, schema, inregistrare_id, cont_debit, cont_credit):
    cur.execute(f"""
                    INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                    VALUES (%s, '6811', %s, %s)
                """,
                (inregistrare_id, cont_debit, cont_credit))


def blocheaza_perioada(cur, schema, an, luna, blocat_de):
    cur.execute(f"""INSERT INTO {schema}.perioade_blocate (an, luna, blocat_de)
                            VALUES (%s,%s,%s) ON CONFLICT DO NOTHING""",
                (an, luna, blocat_de))


def deblocheaza_perioada(cur, schema, an, luna):
    cur.execute(f"DELETE FROM {schema}.perioade_blocate WHERE an=%s AND luna=%s",
                (an, luna))


def nota_amef_ciorna(cur, schema, data_, numar, descriere, document_ref=None):
    cur.execute(f"""INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status, document_ref)
                                VALUES (%s,%s,%s,'amef','ciorna',%s) RETURNING id""",
                (data_, numar, descriere, document_ref))
    return cur.fetchone()


def adauga_linie_4(cur, schema, inregistrare_id, cont_debit, cont_credit, suma):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                (inregistrare_id, cont_debit, cont_credit, suma))


def nota_horeca_z_ciorna(cur, schema, data_, numar, descriere, document_ref=None):
    """Raportul Z scris de mână intră CIORNĂ, la ambele metode de stoc: [08.10.2026, decizia Costin §6 pct.7 — R36] „evidența = ce a
    validat un om”. La cantitativ-valoric validarea cere și descărcarea pe articol (decizii 07.10 pct.3; `z_descarcare`, poarta din
    `jurnal_api.valideaza`)."""
    cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status, document_ref)
                VALUES (%s, %s, %s, 'horeca_z', 'ciorna', %s) RETURNING id
            """,
                (data_, numar, descriere, document_ref))
    return cur.fetchone()


def adauga_z_cota(cur, schema, inregistrare_id, cota, baza, tva):
    """[lot 19 pct.4b] Defalcarea raportului Z pe o cotă (baza + TVA), în aceeași tranzacție cu nota."""
    cur.execute(f"""INSERT INTO {schema}.rapoarte_z_cote (inregistrare_id, cota, baza, tva)
                    VALUES (%s, %s, %s, %s)""", (inregistrare_id, cota, baza, tva))


def adauga_z_amef(cur, schema, inregistrare_id, nui, nr_bonuri):
    """[D394 op2 Î1, decizia B] Casa (NUI) și numărul de bonuri ale raportului Z — același rând pe ambele rute."""
    cur.execute(f"""INSERT INTO {schema}.rapoarte_z_amef (inregistrare_id, nui, nr_bonuri)
                    VALUES (%s, %s, %s)""", (inregistrare_id, nui, nr_bonuri))


def adauga_linie_3(cur, schema, inregistrare_id, cont_debit, cont_credit, suma):
    cur.execute(f"""
                    INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                    VALUES (%s, %s, %s, %s)
                """,
                (inregistrare_id, cont_debit, cont_credit, suma))


def nota_operatiune_ciorna(cur, schema, data_, descriere, tip_document="nota_calcul", document_ref=None):
    """[lotul 10, deficiența 430d, clasa] Ciorna unei operațiuni speciale, cu sursa ei: `operatiuni` („sursa: operațiunile
    speciale”, `jurnal_api.ETICHETE_SURSA`) — nu „facturile” / „banca (extrasul de cont)” / „registrul de casă” / „statul de
    plată”, documente pe care nota nu le are în spate. Documentul: `document_ref` dat
    (documentul extern al operației — hotărârea adunării asociaților la dividende, 430c) sau, fără el, documentul intern numerotat
    (`_cu_document_intern`, Legea 82/1991 art.6 alin.(1)). Întoarce rândul `RETURNING id`."""
    cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                            VALUES (%s,%s,'operatiuni','ciorna',%s) RETURNING id""",
                (data_, descriere, document_ref))
    r = cur.fetchone()
    return r if document_ref else _cu_document_intern(cur, schema, tip_document, data_, r)


def adauga_linie_partener(cur, schema, inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume):
    """[lotul 10, deficiența 430b] Rândul notei cu partenerul lui (asociatul, la dividende) — coloanele deficienței 381."""
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume)
                            VALUES (%s,%s,%s,%s,%s,%s)""",
                (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume))


def dividende_nevalidate_din(cur, schema, cont_sursa):
    """[lotul 10, deficiența 430a] Dividendele propuse din `cont_sursa` în note NEVALIDATE (<sursa> = 457): profitul pe care
    l-ar consuma, încă neintrat în sold. [(nota_id, data, suma)]."""
    cur.execute(f"""SELECT i.id, i.data, SUM(l.suma) AS suma FROM {schema}.inregistrari i
                            JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                            WHERE i.status <> 'validata' AND l.cont_debit = %s AND l.cont_credit LIKE '457%%'
                            GROUP BY i.id, i.data ORDER BY i.data, i.id""", (cont_sursa,))
    return cur.fetchall()



def adauga_linie_2(cur, schema, inregistrare_id, cont_debit, cont_credit, suma):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                    (inregistrare_id, cont_debit, cont_credit, suma)
                                    VALUES (%s,%s,%s,%s)""",
                (inregistrare_id, cont_debit, cont_credit, suma))


def adauga_linie(cur, schema, inregistrare_id, cont_debit, cont_credit, suma):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""",
                (inregistrare_id, cont_debit, cont_credit, suma))


def adauga_linie_venit_servicii(cur, schema, inregistrare_id, cont_debit):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,'4111','704',%s)""",
                (inregistrare_id, cont_debit))


def nota_facturi_cu_factura(cur, schema, data_, factura_id, descriere):
    cur.execute(f"""INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status)
                            VALUES (%s,%s,%s,'facturi','ciorna') RETURNING id""",
                (data_, factura_id, descriere))
    return cur.fetchone()


def adauga_linie_furnizor(cur, schema, inregistrare_id, cont_debit, cont_credit):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,%s,'401',%s)""",
                (inregistrare_id, cont_debit, cont_credit))


def adauga_linie_client(cur, schema, inregistrare_id, cont_debit, cont_credit):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,'4111',%s,%s)""",
                (inregistrare_id, cont_debit, cont_credit))


def adauga_linie_5(cur, schema, inregistrare_id, cont_debit, cont_credit, suma):
    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                (inregistrare_id, cont_debit, cont_credit, suma))



def search_path_firma(cur, schema):
    """[08.10, W2] Numele necalificate ale cititorilor (registrul MF) pe schema firmei, numai în tranzacția curentă."""
    cur.execute('SET LOCAL search_path TO "%s", public' % str(schema).strip('"'))


def punct_de_revenire(cur, nume):
    """[retest 08.10 pct.1] SAVEPOINT — înlocuirea ciornei statului se poate retrage dacă noua notă are aceeași amprentă."""
    cur.execute("SAVEPOINT %s" % nume)


def revino_la(cur, nume):
    cur.execute("ROLLBACK TO SAVEPOINT %s" % nume)


def profil_tva(cur):
    """[08.10, V1] (platitor_tva, tip_decont) — fereastra D406 (`common.fereastra_d406`)."""
    cur.execute("SELECT platitor_tva, tip_decont FROM firma_profil LIMIT 1")
    return cur.fetchone()


def cate_nevalidate_dintre(cur, nota_ids):
    """[deficiența 284] Câte din notele date sunt încă nevalidate (cele șterse nu se mai numără)."""
    cur.execute("SELECT count(*) FROM inregistrari WHERE id = ANY(%s) AND status <> 'validata'", (list(nota_ids),))
    return cur.fetchone()[0]


def note_nevalidate_in_interval(cur, de_la, pana_la):
    """[08.10, V1] Câte note NEvalidate sunt în [de_la, pana_la) — balanța le arată, D406 nu."""
    cur.execute("SELECT count(*) FROM inregistrari WHERE status <> 'validata' AND data >= %s AND data < %s", (de_la, pana_la))
    return cur.fetchone()[0]
