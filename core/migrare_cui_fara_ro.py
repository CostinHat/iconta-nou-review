"""
core/migrare_cui_fara_ro.py — CUI-ul se păstrează fără „RO” și fără spații (lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII
„Comanda 10.3”: „CUI-ul se păstrează fără «RO» și fără spații; «RO» apare doar la afișare, după starea de plătitor de TVA.”).

Temeiul formei afișate: CF art.318 alin.(1) — „Codul de înregistrare în scopuri de TVA, atribuit conform art. 316 și 317 , are prefixul
RO, conform Standardului internațional ISO 3166 - alpha 2.” — prefixul e al codului de TVA, deci se pune la afișare / pe documentul
ANAF după starea de plătitor (D406 `registration_number`, e-Factura `_vatid` din cifre + stare, factura PDF `cod_fiscal_pe_factura`).

CE FACE:
1. NORMALIZAREA ÎN BAZĂ, PE ORICE DRUM (gardul): un trigger `BEFORE INSERT OR UPDATE OF <coloana>` pe fiecare coloană de cod fiscal —
   aceeași formă ca `core/cui_forma.stocare` (spațiile scoase, „RO” scos din fața unui cod numai din cifre; codul de TVA al unui partener
   din alt stat rămâne cu prefixul statului; o valoare goală rămâne cum e — coloanele NOT NULL au '' implicit). Orice scriere viitoare
   (ecran, import, ANAF, e-Factura, o rută nouă) iese normalizată; niciun drum nu o poate ocoli. Pe facturi, un „RO” scris pe o factură
   fără starea partenerului înghețată (`tert_platitor_tva` NULL — ANAF n-a răspuns la emitere) devine starea înghețată (`true`): prefixul
   scris era singura informație despre starea lui (CF art.318 alin.(1)), iar factura PDF / D394 o citeau din el; acum o citesc din coloană.
2. DATELE EXISTENTE, numai DATELE DE BAZĂ: fișele de clienți / furnizori, profilul firmei, soldurile de preluare ale partenerilor, firma
   și cabinetul din `public`. Documentele emise / înregistrate (facturi, note, casă, bonuri, chitanțe, NIR, e-Factura primite, extrase)
   NU se rescriu: sunt documente, iar lunile închise și notele validate sunt păzite de regulile de fond (`migrare_reguli_fond`,
   `trg_perioada_blocata_*`). Consumatorii lor compară deja fără prefix (`cui_forma.SQL`, D394 `cui_ro`, D406
   `_partener_registration_number`). Dacă și ele trebuie rescrise e decizia lui Costin (raportul lotului 11, §6).
   Dubluri: două fișe care după normalizare au același CUI (ex. „RO123” și „123”) încalcă cheia unică — migrarea se OPREȘTE pe firma
   aceea și le numește (nu unește fișe: alegerea e a contabilului); după unire, se rulează din nou.
`--uscat` (fără `--productie` / registru: `python -m core.migrare_cui_fara_ro --uscat [--dsn-productie] [--scheme s1,s2]`): numai
citire, în ROLLBACK — câte valori s-ar schimba pe fiecare coloană, documentele numărate separat (nu se rescriu).
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `sql('TENANT_PLACEHOLDER')` (păzit de core/test_lot11_p_cui.py); partea
publică: `SQL_PUBLIC` (oglinda în infra/bootstrap_public.sql). Rulare: `python -m core.migrari_registru ruleaza [--productie]
core/migrare_cui_fara_ro.py`.
"""
import sys

from core import db

MARCAJ_INCEPUT = "-- [cui_fara_ro_v1, lotul 11, decizia Costin 10.3] CUI-ul fără „RO” și fără spații — SURSA: core/migrare_cui_fara_ro.py"
MARCAJ_SFARSIT = "-- [cui_fara_ro_v1] sfârșit"

#: spațiile scoase — aceleași ca `\s` din Python (`cui_forma.SPATII_SQL`): `\s` din PostgreSQL nu vede U+00A0 / U+202F / U+2007 / U+0085 /
#: U+001C–U+001F [lotul 11, subagentul CF; paritatea pe fiecare spațiu Unicode: core/test_lot11_cf_cui_forma_unica.py]
SPATII = "[\\s\\u0085\\u00a0\\u2007\\u202f\\u001c-\\u001f]"
#: expresia SQL a normalizării — aceeași ca `cui_forma.stocare` (paritatea: core/test_lot11_p_cui.py)
EXPR = "regexp_replace(regexp_replace(upper(v), '" + SPATII + "', '', 'g'), '^RO([0-9]+)$', '\\1')"

#: (tabela, coloanele de cod fiscal) din schema unei firme — TOATE (garda numără coloanele `cui` / `cif` din șablon)
COLOANE_FIRMA = (
    ("clienti", ("cui",)), ("furnizori", ("cui",)), ("firma_profil", ("cui",)), ("solduri_parteneri", ("cui",)),
    ("facturi", ("tert_cui",)), ("facturi_recurente", ("tert_cui",)), ("casa_operatiuni", ("cui",)), ("bonuri", ("cui",)),
    ("chitante", ("client_cui",)), ("nir", ("cui",)), ("inregistrari_linii", ("partener_cui",)),
    ("efactura_primite", ("cif_emitent", "cif_beneficiar")), ("extras_linii", ("cui_detectat",)),
    # [lotul 11, subagentul CF] `asociati.cnp` ține și CUI-ul asociatului persoană juridică (UNIQUE(cnp)); un CNP n-are „RO” și rămâne
    ("asociati", ("cnp",)),
)
#: datele de bază: se normalizează și pe datele existente (restul sunt documente — vezi docstringul)
DATE_DE_BAZA = ("clienti", "furnizori", "firma_profil", "solduri_parteneri", "asociati")
#: (tabela, coloanele) din `public`: firma și cabinetul (+ CIF-ul întocmitorului bilanțului)
COLOANE_PUBLIC = (("tenants", ("cui",)), ("accounting_firms", ("cui", "cif_intocmit")))


def _functie(s):
    return """CREATE OR REPLACE FUNCTION %(s)s.cui_stocare(v text) RETURNS text AS $$
  SELECT CASE WHEN v IS NULL OR btrim(v) = '' THEN v ELSE %(e)s END
$$ LANGUAGE sql IMMUTABLE;
CREATE OR REPLACE FUNCTION %(s)s.cui_normalizeaza() RETURNS trigger AS $$
DECLARE c text; v text; n text; j jsonb := '{}'::jsonb;
BEGIN
  FOREACH c IN ARRAY TG_ARGV LOOP
    v := to_jsonb(NEW) ->> c;
    n := %(s)s.cui_stocare(v);
    IF n IS DISTINCT FROM v THEN j := j || jsonb_build_object(c, n); END IF;
  END LOOP;
  IF j <> '{}'::jsonb THEN NEW := jsonb_populate_record(NEW, j); END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;""" % {"s": s, "e": EXPR}


def sql(s):
    """DDL-ul pentru schema `s` (numele exact, între ghilimele, sau `TENANT_PLACEHOLDER` pentru șablon)."""
    out = [MARCAJ_INCEPUT, _functie(s),
           # facturi: „RO” scris fără starea înghețată -> starea înghețată (CF art.318 alin.(1)); apoi forma păstrată
           """CREATE OR REPLACE FUNCTION %(s)s.cui_normalizeaza_factura() RETURNS trigger AS $$
BEGIN
  IF NEW.tert_platitor_tva IS NULL AND regexp_replace(upper(COALESCE(NEW.tert_cui, '')), '%(sp)s', '', 'g') ~ '^RO[0-9]+$' THEN
    NEW.tert_platitor_tva := true;
  END IF;
  NEW.tert_cui := %(s)s.cui_stocare(NEW.tert_cui);
  RETURN NEW;
END $$ LANGUAGE plpgsql;""" % {"s": s, "sp": SPATII}]
    for t, cols in COLOANE_FIRMA:
        fn = "cui_normalizeaza_factura()" if t == "facturi" else "cui_normalizeaza(%s)" % ", ".join("'%s'" % c for c in cols)
        out.append("DROP TRIGGER IF EXISTS trg_cui_fara_ro ON %s.%s;" % (s, t))
        out.append("CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF %s ON %s.%s FOR EACH ROW EXECUTE FUNCTION %s.%s;"
                   % (", ".join(cols), s, t, s, fn))
    out.append(MARCAJ_SFARSIT)
    return "\n".join(out)


def sql_public():
    """DDL-ul pentru `public` (o dată per bază)."""
    out = [_functie("public")]
    for t, cols in COLOANE_PUBLIC:
        out.append("DROP TRIGGER IF EXISTS trg_cui_fara_ro ON public.%s;" % t)
        out.append("CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF %s ON public.%s FOR EACH ROW EXECUTE FUNCTION "
                   "public.cui_normalizeaza(%s);" % (", ".join(cols), t, ", ".join("'%s'" % c for c in cols)))
    return "\n".join(out)


SQL_PUBLIC = sql_public()

def _expr(col):
    return EXPR.replace("upper(v)", "upper(%s)" % col)


def dubluri(cur, tabela, col="cui", cu=None):
    """[(valoarea normalizată, [valorile scrise])] — rânduri distincte care după normalizare ar avea același cod (cheia unică, împreună
    cu coloana `cu` când cheia are două coloane: `solduri_parteneri (cont, cui)`)."""
    g = ("%s || ' ' || " % cu) if cu else ""
    cur.execute("SELECT %(g)s%(e)s, array_agg(%(c)s ORDER BY %(c)s) FROM %(t)s WHERE btrim(COALESCE(%(c)s, '')) <> '' "
                "GROUP BY 1 HAVING count(*) > 1 ORDER BY 1" % {"g": g, "e": _expr(col), "c": col, "t": tabela})
    return [(r[0], list(r[1])) for r in cur.fetchall()]


#: cheile unice ale datelor de bază care conțin codul: tabela -> coloana de lângă cod (None = codul singur)
CHEI_FIRMA = {"clienti": None, "furnizori": None, "solduri_parteneri": "cont"}


def de_schimbat(cur, tabela, col, unde="", param=()):
    """Câte valori nevide din `tabela.col` s-ar schimba (`unde` = condiție în plus, cu `param`)."""
    cur.execute("SELECT count(*) FROM %(t)s WHERE btrim(COALESCE(%(c)s, '')) <> '' AND %(c)s IS DISTINCT FROM %(e)s %(u)s"
                % {"t": tabela, "c": col, "e": _expr(col), "u": unde}, param)
    return cur.fetchone()[0]


def aplica_public(conn):
    with conn.cursor() as cur:
        d = dubluri(cur, "public.accounting_firms")
        if d:
            raise ValueError("cabinete care ar avea același CUI după normalizare (se corectează unul, apoi se rulează din nou): " +
                             "; ".join("%s: %s" % (n, ", ".join(v)) for n, v in d))
        cur.execute(SQL_PUBLIC)
        for t, cols in COLOANE_PUBLIC:
            for c in cols:
                cur.execute("UPDATE public.%s SET %s = %s WHERE btrim(COALESCE(%s, '')) <> '' AND %s IS DISTINCT FROM %s"
                            % (t, c, _expr(c), c, c, _expr(c)))


def aplica(conn, schema):
    """True dacă a aplicat; None dacă schema n-are tabelele (nu e o firmă). Dubluri pe fișe -> ValueError, nimic scris."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name IN %s",
                    (schema, tuple(t for t, _c in COLOANE_FIRMA)))
        if cur.fetchone()[0] < len(COLOANE_FIRMA):
            return None
        d = [(t, n, v) for t, cu in CHEI_FIRMA.items() for n, v in dubluri(cur, '"%s".%s' % (schema, t), cu=cu)]
        # [lotul 11, CF] asociații: UNIQUE(cnp) — doi asociați cu același cod după normalizare se unesc întâi, ca fișele
        d += [("asociati", n, v) for n, v in dubluri(cur, '"%s".asociati' % schema, col="cnp")]
        if d:
            raise ValueError("fișe care ar avea același CUI după normalizare (se unesc de contabil, apoi se rulează din nou): " +
                             "; ".join("%s %s: %s" % (t, n, ", ".join(v)) for t, n, v in d))
        cur.execute(sql('"%s"' % schema))
        for t, cols in COLOANE_FIRMA:
            if t in DATE_DE_BAZA:
                for c in cols:   # UPDATE OF col: triggerul de mai sus face normalizarea; expresia o face explicit (aceeași)
                    cur.execute('UPDATE "%s".%s SET %s = %s WHERE btrim(COALESCE(%s, \'\')) <> \'\' AND %s IS DISTINCT FROM %s'
                                % (schema, t, c, _expr(c), c, c, _expr(c)))
    return True


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = %s AND t.tgname = 'trg_cui_fara_ro'", (schema,))
        return cur.fetchone()[0] == len(COLOANE_FIRMA)


def raport_uscat(cur, scheme):
    """{schema: {"date_de_baza": {tabela.col: n}, "documente": {tabela.col: n}, "dubluri": [...]}} — numai citire."""
    out = {}
    for s in scheme:
        r = {"date_de_baza": {}, "documente": {}, "dubluri": []}
        for t, cols in COLOANE_FIRMA:
            cur.execute("SELECT to_regclass(%s)", ('"%s".%s' % (s, t),))
            if cur.fetchone()[0] is None:
                continue
            for c in cols:
                n = de_schimbat(cur, '"%s".%s' % (s, t), c)
                if n:
                    r["date_de_baza" if t in DATE_DE_BAZA else "documente"]["%s.%s" % (t, c)] = n
            if t in CHEI_FIRMA:
                r["dubluri"] += [(t, n, v) for n, v in dubluri(cur, '"%s".%s' % (s, t), cu=CHEI_FIRMA[t])]
        out[s] = r
    return out


def _main():
    if "--uscat" in sys.argv:
        import os
        if "--dsn-productie" in sys.argv:
            from core import mediu_test
            os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
        db.init_pool()
        scheme = sys.argv[sys.argv.index("--scheme") + 1].split(",") if "--scheme" in sys.argv else None
        with db.get_conn() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SET TRANSACTION READ ONLY")
                    if scheme is None:
                        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
                        scheme = [x[0] for x in cur.fetchall()]
                    for s, r in raport_uscat(cur, scheme).items():
                        print("%s: date de bază %s; documente (nu se rescriu) %s; dubluri %s" % (
                            s, r["date_de_baza"] or "nimic", r["documente"] or "nimic", r["dubluri"] or "niciuna"))
                    # partea publică: NUMAI firmele numite și cabinetele lor (pe producție, datele altui cabinet nu se citesc)
                    _sch = tuple(scheme)
                    _unde = {"tenants": ("AND schema_name IN %s", (_sch,)),
                             "accounting_firms": ("AND id IN (SELECT accounting_firm_id FROM public.tenants WHERE schema_name IN %s)", (_sch,))}
                    for t, cols in COLOANE_PUBLIC:
                        for c in cols:
                            cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s "
                                        "AND column_name = %s", (t, c))
                            if cur.fetchone()[0]:
                                print("public.%s.%s (firmele numite / cabinetele lor): %d de schimbat" % (
                                    t, c, de_schimbat(cur, "public.%s" % t, c, *_unde[t])))
            finally:
                conn.rollback()
        return
    db.init_pool()
    with db.get_conn() as conn:
        aplica_public(conn)
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                if aplica(conn, s):
                    ok += 1
                conn.commit()
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_cui_fara_ro: public ok; firme %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
