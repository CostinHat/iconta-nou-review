# -*- coding: utf-8 -*-
"""REPOSITORY — articolele și mișcările de stoc.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def articolul_exista(cur, articol_id):
    cur.execute("SELECT 1 FROM articole WHERE id=%s",
                (articol_id,))
    return cur.fetchone()


def articole_cu_cont(cur, schema):
    cur.execute(f"SELECT id, denumire, cont_stoc FROM {schema}.articole ORDER BY id")
    return cur.fetchall()


def miscari_pentru_d406(cur, schema, an):
    cur.execute(f"""SELECT a.id, a.denumire, a.um, a.cont_stoc,
                                   m.data, m.tip, m.cantitate, m.valoare
                            FROM {schema}.articole a
                            JOIN {schema}.miscari_stoc m ON m.articol_id = a.id
                            WHERE m.data <= %s
                            ORDER BY a.id, m.data, m.id""",
                (an,))
    return cur.fetchall()


def miscari_ale_articolului(cur, schema, articol_id):
    """Fișa de magazie a articolului, în ordinea în care o citește motorul CMP (`stocuri_cv.fisa_magazie`). SURSA UNICĂ a acestei
    citiri [retest 07.10 R1]: stornarea în roșu cere `valoare` și `anuleaza_id` — trei citiri separate (fișa, rețetele, inventarul)
    ar fi trebuit să le afle toate trei."""
    cur.execute(f"""SELECT id, data, tip, cantitate, pret_unitar, valoare, document, anuleaza_id FROM {schema}.miscari_stoc
                    WHERE articol_id=%s ORDER BY data, id""", (articol_id,))
    return [dict(r) for r in cur.fetchall()]


# ── [lotul 11, subagentul x — regula straturilor] SQL-ul NIR-ului cu număr repetat (decizia 10.3, `uc_tenants.stocuri_adauga` /
# `_nir_cu_numarul`) și al articolului ales din nomenclator (450, `uc_tenants.achizitie_neinregistrat` / `borderou_storneaza`), mutat din
# use-case fără schimbare de comportament.
def miscari_pentru_diferenta(cur, schema, cont):
    """[696.1, comanda 14.3] Mișcările de intrare / ieșire ale articolelor cu contul de stoc `cont`, cu valoarea notei lor pe cont: [{id, data, tip,
    document, valoare, inregistrare_id, status_nota, valoare_nota}] — pentru a numi cauza unei diferențe între fișe și balanță (fără notă, sau
    nota are altă valoare). `valoare_nota` = suma liniilor notei pe contul de stoc (debit la intrare, credit la ieșire)."""
    cur.execute(f"""SELECT m.id, m.data, m.tip, m.document, m.valoare, m.inregistrare_id, i.status AS status_nota,
                           (SELECT coalesce(sum(l.suma), 0) FROM {schema}.inregistrari_linii l
                             WHERE l.inregistrare_id = m.inregistrare_id
                               AND ((m.tip = 'intrare' AND l.cont_debit LIKE %s) OR (m.tip = 'iesire' AND l.cont_credit LIKE %s))) AS valoare_nota
                      FROM {schema}.miscari_stoc m
                      JOIN {schema}.articole a ON a.id = m.articol_id
                      LEFT JOIN {schema}.inregistrari i ON i.id = m.inregistrare_id
                     WHERE a.cont_stoc = %s AND m.tip IN ('intrare', 'iesire')
                       AND m.data > coalesce((SELECT max(data_referinta) FROM {schema}.solduri_initiale), date '0001-01-01')   -- ce e după preluare: soldul preluat nu e o cauză
                     ORDER BY m.data, m.id""", (cont + "%", cont + "%", cont))
    return [dict(r) for r in cur.fetchall()]


def blocheaza_nir_urile(cur, schema):
    """NIR-urile firmei se scriu unul după altul: lacăt pe tranzacție."""
    cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (schema + ":nir",))


def nir_cu_numarul(cur, schema, numar_normalizat, an, refacut_din_id):
    """NIR-ul care poartă `numar_normalizat` (majuscule, spațiile strânse) în `an`, altul decât `refacut_din_id` și neînlocuit de o refacere:
    (numar, data, furnizor) — rândul cursorului — sau None."""
    cur.execute(f"""SELECT n.numar, n.data, n.furnizor FROM {schema}.nir n
                    WHERE upper(regexp_replace(btrim(n.numar), '\\s+', ' ', 'g')) = %s AND EXTRACT(YEAR FROM n.data) = %s
                      AND n.id IS DISTINCT FROM %s
                      AND NOT EXISTS (SELECT 1 FROM {schema}.nir r WHERE r.refacut_din_id = n.id)
                    ORDER BY n.data, n.id LIMIT 1""", (numar_normalizat, int(an), refacut_din_id))
    return cur.fetchone()


def savepoint_nir_numar_repetat(cur):
    """NIR-ul cu numărul repetat se verifică (toate refuzurile lui, 440) fără să se scrie nimic."""
    cur.execute("SAVEPOINT nir_numar_repetat")


def inapoi_la_nir_numar_repetat(cur):
    cur.execute("ROLLBACK TO SAVEPOINT nir_numar_repetat")


def articolul_ales(cur, schema, articol_id):
    """Articolul din nomenclator: id, denumire, um (sau None)."""
    cur.execute("SELECT id, denumire, um FROM %s.articole WHERE id = %%s" % schema, (int(articol_id),))
    return cur.fetchone()


def denumirea_articolului(cur, schema, articol_id):
    """Rândul cu `denumire` al articolului (sau None)."""
    cur.execute(f"SELECT denumire FROM {schema}.articole WHERE id = %s", (articol_id,))
    return cur.fetchone()


def clasa_miscarilor(cur, schema):
    """[lotul 14, deficiența 696] {id mișcare: 'validata' | 'ciorna' | 'fara_nota'}. `validata` = mișcarea e în evidență (nota ei sau o notă a
    documentului ei e validată — `stocuri_anulare.IN_EVIDENTA`, aceeași definiție ca la respingere); `ciorna` = are notă (sau document cu
    notă), dar niciuna validată; `fara_nota` = n-are nicio notă (soldul preluat la migrare, mișcarea unui document încă necontat)."""
    from core.stocuri_anulare import IN_EVIDENTA
    nevalidata = (IN_EVIDENTA.replace("i.status = 'validata'", "i.status <> 'validata'"))
    cur.execute(("SELECT m.id, CASE WHEN " + IN_EVIDENTA + " THEN 'validata' WHEN " + nevalidata + " THEN 'ciorna' ELSE 'fara_nota' END AS clasa "
                 "FROM {s}.miscari_stoc m").format(s=schema))
    return {(r["id"] if isinstance(r, dict) else r[0]): (r["clasa"] if isinstance(r, dict) else r[1]) for r in cur.fetchall()}


def locatii_cu_stoc(cur, schema):
    """[lotul 14, deficiența 696] {articol_id: [locație, …]} — locațiile (gestiunile) în care articolul are mișcări, ca „Gestiune” în
    situația stocului: două rânduri cu aceeași denumire se deosebesc prin ea. Mișcările fără locație nu apar."""
    cur.execute(f"""SELECT articol_id, locatie FROM {schema}.miscari_stoc WHERE locatie IS NOT NULL AND btrim(locatie) <> ''
                    GROUP BY articol_id, locatie ORDER BY articol_id, locatie""")
    out = {}
    for r in cur.fetchall():
        a, l = (r["articol_id"], r["locatie"]) if isinstance(r, dict) else (r[0], r[1])
        out.setdefault(a, []).append(l)
    return out
