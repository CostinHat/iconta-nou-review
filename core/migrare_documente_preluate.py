# -*- coding: utf-8 -*-
"""
core/migrare_documente_preluate.py — facturile deschise preluate (lotul 12, deficiența 252).

DEFECTUL. Importul soldurilor pe parteneri scria numai `solduri_parteneri` (soldul fiecărui partener). Facturile deschise ale programului
vechi nu deveneau documente ale firmei: scadențarul nu le vedea, iar o încasare / plată din bancă, casă sau compensare de după preluare
n-avea ce stinge (rândul „fără potrivire”, nota fără factură). De acum importul scrie și facturile deschise
(`solduri_parteneri_api.documente_din_randuri`, `facturi.tip = 'preluata'`).

CE FACE:
1. STRUCTURA: indexul numerotării unice pe emise (`facturi_numar_emisa_uniq`, `migrare_unic_numar_factura.CONDITIE`) nu mai cuprinde
   facturile deschise preluate — numerele lor sunt ale programului vechi („Sold la <data>” e același pe toți clienții). Indexul vechi se
   reface numai dacă n-are condiția nouă. Sursa unică a definiției: `migrare_unic_numar_factura` (oglinda din tenant_template.sql).
2. DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): firmele cu solduri pe parteneri salvate
   înainte de reparație primesc facturile deschise pe care le-ar fi scris importul — soldul fiecărui partener de pe 4111 / 401 ca document
   „Sold la <data preluării>”, fără scadență (fișierul vechi n-avea facturile: nu se inventează nici numere, nici scadențe).
   NU se scriu (și se numesc) când documentul ar minți:
     * firma are deja facturi deschise preluate (idempotent);
     * firma n-are data preluării (`bilant_api.data_soldurilor`);
     * pe cont există, după data preluării, încasări / plăți NElegate de nicio factură (credit 4111 / debit 401, fără `factura_id`, fără
       chitanță sau compensare legată), cu suma netă nenulă: acelea au stins deja, de mână, o parte din soldurile preluate, iar un document
       cu soldul întreg ar apărea în scadențar ca neîncasat (exact defectul 466). Contabilul reîncarcă atunci soldurile pe parteneri din
       ecran (Import date › Solduri parteneri), după ce leagă încasările.
   [lotul 12, decizia Costin 12.3 pct.5: „dacă [coloana TVA la încasare] lipsește, se ia regimul firmei la data facturii”] Fișierul vechi
   n-avea coloana, deci documentul primește regimul firmei la data preluării (`solduri_parteneri_api.cu_regimul_tva`, ca la import):
   firma în sistemul TVA la încasare -> TVA-ul cuprins în sold e încă neexigibil / nededus și îl mută încasarea / plata. NU se pune (și se
   numește) când firma are deja un D300 depus pe o perioadă care se termină la data preluării sau după ea: secțiunea „TVA neexigibilă” a
   unui D300 regenerat pe acea perioadă n-ar mai fi cea depusă. Contabilul reîncarcă atunci soldurile din ecran, cu coloana.
Notele, balanța și declarațiile depuse NU se ating: documentele n-au notă și nu intră în nicio declarație ca documente ale perioadei.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_documente_preluate.py`.
"""
from core import db
from core.common import cate as _cate

_INDEX = "facturi_numar_emisa_uniq"


def _ddl_index(cur, schema):
    """Indexul numerotării unice, cu condiția fără facturile preluate (refăcut numai dacă e vechi). -> True dacă s-a refăcut."""
    from core import migrare_unic_numar_factura as _mu
    cur.execute("SELECT indexdef FROM pg_indexes WHERE schemaname = %s AND indexname = %s", (schema, _INDEX))
    r = cur.fetchone()
    if r and "preluata" in r[0]:
        return False
    cur.execute('DROP INDEX IF EXISTS "%s".%s' % (schema, _INDEX))
    cur.execute(_mu._DDL.format(s=schema))
    return True


def stinse_nelegate(cur, schema, cont, dupa):
    """Suma netă a încasărilor (credit 4111) / plăților (debit 401) de după `dupa`, NElegate de o factură (nici `factura_id`, nici
    chitanța, nici compensarea): ce a stins deja, de mână, din soldurile preluate."""
    latura = "l.cont_credit" if cont == "4111" else "l.cont_debit"
    cur.execute(f'''SELECT COALESCE(SUM(l.suma), 0) FROM "{schema}".inregistrari i
                      JOIN "{schema}".inregistrari_linii l ON l.inregistrare_id = i.id
                     WHERE {latura} LIKE %s AND i.data > %s AND i.factura_id IS NULL
                       AND NOT EXISTS (SELECT 1 FROM "{schema}".chitante c WHERE c.inregistrare_id = i.id AND c.factura_id IS NOT NULL)
                       AND NOT EXISTS (SELECT 1 FROM "{schema}".compensari z WHERE z.inregistrare_id = i.id)''', (cont + "%", dupa))
    return cur.fetchone()[0]


def d300_depus_dupa(cur, schema, zi):
    """[12.3 pct.5] Perioada (an, luna) celui mai recent D300 depus al firmei care se termină la `zi` sau după, ori None. `luna` =
    ultima lună a perioadei (`declaratii_depuse_curente`; prin aplicație „d300”, din istoricul importat „D300”)."""
    cur.execute("SELECT d.an, d.luna FROM public.declaratii_depuse_curente d JOIN public.tenants t ON t.id = d.tenant_id "
                "WHERE t.schema_name = %s AND lower(d.tip) = 'd300' AND d.an * 100 + d.luna >= %s ORDER BY d.an DESC, d.luna DESC LIMIT 1",
                (schema, zi.year * 100 + zi.month))
    r = cur.fetchone()
    return (r[0], r[1]) if r else None


def aplica(conn, schema):
    """-> {"index": bool, "documente": n, "sarite": [motiv]}."""
    import psycopg2
    import psycopg2.extras as _E
    from core import bilant_api as _bil, solduri_parteneri_api as _sp
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    rez = {"index": False, "documente": 0, "sarite": []}
    with conn.cursor() as cur:
        rez["index"] = _ddl_index(cur, schema)
        cur.execute("SELECT to_regclass(%s)", ('"%s".solduri_parteneri' % schema,))
        if cur.fetchone()[0] is None:
            return rez
        cur.execute('SELECT count(*) FROM "%s".facturi WHERE tip = %%s' % schema, ("preluata",))
        if cur.fetchone()[0]:
            return rez
        cur.execute('SELECT cont, cui, denumire, sold_debitor, sold_creditor FROM "%s".solduri_parteneri ORDER BY id' % schema)
        randuri = [{"cont": c, "cui": u, "denumire": d, "debit": sd, "credit": sc} for c, u, d, sd, sc in cur.fetchall()]
    if not randuri:
        return rez
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        zi = _bil.data_soldurilor(cur, schema)
    if not zi:
        rez["sarite"].append("firma n-are data preluării: soldurile pe parteneri rămân fără documente (se reîncarcă din ecran)")
        return rez
    docs, _nec = _sp.documente_din_randuri(randuri, zi.isoformat())
    with conn.cursor() as cur:
        for cont in sorted({_sp._radacina(d["cont"]) for d in docs}):
            n = stinse_nelegate(cur, schema, cont, zi)
            if n:
                rez["sarite"].append("contul %s: după %s are încasări / plăți nelegate de facturi (net %s lei) — soldurile partenerilor lui "
                                     "nu devin documente; se reîncarcă din ecran după legarea lor" % (cont, zi.isoformat(), n))
                docs = [d for d in docs if _sp._radacina(d["cont"]) != cont]
        cur.execute('SET LOCAL search_path TO "%s", public' % schema)
        _sp.cu_regimul_tva(cur, docs)   # [12.3 pct.5] regimul firmei la data preluării (fișierul vechi n-avea coloana)
        depus = d300_depus_dupa(cur, schema, zi) if any(d["tva"] for d in docs) else None
        if depus:
            for d in docs:
                d["tva"], d["furnizor_tva_incasare"] = 0, False
            rez["sarite"].append("firma aplica sistemul TVA la încasare la %s, dar are D300 depus pe %02d/%d: documentele se scriu fără TVA "
                                 "neexigibil (declarația depusă rămâne neatinsă); reîncarcă soldurile pe parteneri din ecran, cu coloana "
                                 "„TVA la încasare”, dacă TVA-ul lor trebuie să devină exigibil la încasare" % (zi.isoformat(), depus[1], depus[0]))
        cur.execute("SAVEPOINT documente_preluate")
        try:
            _sp._scrie_documente(cur, docs)
        except psycopg2.errors.RaiseException as e:   # luna preluării închisă (trg_perioada_blocata_facturi): se numește, indexul rămâne
            cur.execute("ROLLBACK TO SAVEPOINT documente_preluate")
            rez["sarite"].append("facturile deschise nu s-au scris: %s (se reîncarcă din ecran după deschiderea lunii)"
                                 % (e.diag.message_primary or e))
            return rez
    rez["documente"] = len(docs)
    return rez


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT indexdef FROM pg_indexes WHERE schemaname = %s AND indexname = %s", (schema, _INDEX))
        r = cur.fetchone()
        return bool(r and "preluata" in r[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, idx, total = 0, [], 0, 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            idx += int(r["index"])
            total += r["documente"]
            if r["documente"]:
                print("  %s: %s" % (s, _cate(r["documente"], "factură deschisă preluată scrisă", "facturi deschise preluate scrise")))
            for m in r["sarite"]:
                print("  %s: %s" % (s, m))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_documente_preluate: %d ok, %d esec, %d indecși refăcuți, %d facturi deschise preluate scrise" % (ok, len(esec), idx, total))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
