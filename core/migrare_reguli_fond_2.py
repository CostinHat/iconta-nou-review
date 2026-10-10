# -*- coding: utf-8 -*-
"""core/migrare_reguli_fond_2.py — regulile de fond a, c, d, e, f puse în BAZA DE DATE (comanda Costin 09.10.2026, „Retestul plasei”
pct.6, verbatim în DECIZII: „Regulile noi a–f: aprobate toate. La a) și f) citează temeiul din sursă în DECIZII.”). Continuarea lui
`core/migrare_reguli_fond.py` (R1–R5), cu aceeași etichetă `REGULA_CONTABILA:` (409 pe ecran) și aceeași formă (CREATE OR REPLACE +
DROP/CREATE TRIGGER, idempotentă; oglinda în `tenant_template.sql`, păzită de `core/test_reguli_fond_2.py`).

  R6 (a)  factura EMISĂ nu se șterge — se corectează prin factură de stornare. Temei: CF art.330 alin.(1) lit.a)–b) („Corectarea
          informațiilor înscrise în facturi … a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și
          se emite o nouă factură; b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie
          să cuprindă … valorile cu semnul minus …”) — în niciun caz factura nu dispare din evidență. Se poate șterge numai ciorna
          (`nomenclator_status_factura.STERGIBILE`); proforma și avizul nu sunt facturi. [Corectat în același lot: prima formă excepta și
          `de_preluat`, crezând-o factura adusă prin import — e starea în care `emite_factura` produce factura EMISĂ din aplicație.]
  (b)     numărul facturii emise e unic pe serie — EXISTĂ (indexul `facturi_numar_emisa_uniq`, `core/migrare_unic_numar_factura.py`, CF
          art.319 alin.(20) lit.a); verificat pe toate schemele producției la 09.10.2026; aici nu se mai adaugă nimic.
  R7 (c)  declarația DEPUSĂ prin iConta.eu (`public.declaratii_depuse`, sursa „iconta”) nu se modifică (perioada, tipul, XML-ul,
          rândurile, data depunerii, numărul depunerii) și nu se șterge; o corectură e o depunere nouă (rectificativa, `nr_depunere`
          următor). Marcările „extern” / „contabil_anterior” rămân modificabile și anulabile (decizia Costin 08.10, U2). Pe baza de TEST,
          ștergerea e liberă pentru curățenia probelor (perioade sintetice) — activă numai pe producție (`iconta_v2`) sau când sesiunea
          o cere (`iconta.regula_declaratii = 'activa'`, cum o cere proba regulii).
  R8 (d)  stocul unui articol nu devine negativ: o mișcare care scade stocul (ieșire, stornarea unei intrări, ștergerea unei intrări)
          se refuză dacă după ea cantitatea netă a articolului (intrări − ieșiri, pe toate locațiile — `stocuri_cv_api._stoc_locatie`)
          e sub zero. Până azi verificarea stătea numai în Python, pe drumurile care o chemau.
  R9 (e)  luna blocată (`perioade_blocate`) nu primește nici facturi (data emiterii), nici mișcări de stoc, nici operațiuni de casă,
          nici chitanțe — aceeași funcție ca pentru note (`verifica_perioada_blocata`, R2), pe coloana de dată a fiecărui tabel.
  R10 (f) chitanța emisă nu se șterge — se anulează și se păstrează. Temei: OMFP 2634/2015, Anexa 1 pct.15 („În cazul documentelor
          financiar-contabile la care nu se admit corecturi, cum sunt cele pe baza cărora se primeşte, se eliberează sau se justifică
          numerarul […], documentul întocmit greşit se anulează şi se păstrează sau rămâne în carnetul respectiv.”).

ORDINEA pe producție: după `migrare_reguli_fond` (R1–R5). Rulare:
`python -m core.migrari_registru ruleaza --productie core/migrare_reguli_fond_2.py`.
"""
from core.db import SchemaInvalida as _SchemaInvalida
from core import db, nomenclator_status_factura as _nsf

MARCAJ_INCEPUT = ("-- [reguli_fond_v2, 09.10.2026] regulile de fond a, c, d, e, f (comanda Costin „Retestul plasei” pct.6) — "
                  "SURSA: core/migrare_reguli_fond_2.py")
MARCAJ_SFARSIT = "-- [reguli_fond_v2] sfârșit"
#: tabelele pe care luna blocată se extinde (R9) și coloana lor de dată
PERIOADA_PE = (("facturi", "data_emitere"), ("miscari_stoc", "data"), ("casa_operatiuni", "data"), ("chitante", "data"))


def sql(s):
    """DDL-ul regulilor R6, R8, R9, R10 pentru schema `s` (numele exact, sau `TENANT_PLACEHOLDER` pentru șablon)."""
    perioada = "".join("""
CREATE OR REPLACE FUNCTION @S@.verifica_perioada_blocata_%(t)s() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.%(c)s END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.%(c)s END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM @S@.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %%/%% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_perioada_blocata_%(t)s ON @S@.%(t)s;
CREATE TRIGGER trg_perioada_blocata_%(t)s BEFORE INSERT OR UPDATE OR DELETE ON @S@.%(t)s
  FOR EACH ROW EXECUTE FUNCTION @S@.verifica_perioada_blocata_%(t)s();
""" % {"t": t, "c": c} for t, c in PERIOADA_PE)
    return ("""@INC@
CREATE OR REPLACE FUNCTION @S@.regula_factura_emisa() RETURNS trigger AS $$
BEGIN
  IF OLD.directie = 'emisa' AND COALESCE(OLD.tip, 'factura') = 'factura' AND @NESTERGIBILA@ THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Factura % e emisă, deci nu se șterge: se corectează prin factură de stornare (CF art.330 alin.(1)).',
      COALESCE(OLD.serie, '') || OLD.numar;
  END IF;
  RETURN OLD;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_factura_emisa ON @S@.facturi;
CREATE TRIGGER trg_regula_factura_emisa BEFORE DELETE ON @S@.facturi
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_factura_emisa();

CREATE OR REPLACE FUNCTION @S@.efect_stoc(tip text, cantitate numeric) RETURNS numeric AS $$
  SELECT CASE WHEN tip = 'intrare' THEN cantitate WHEN tip = 'iesire' THEN -cantitate ELSE 0 END
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION @S@.regula_stoc_nenegativ() RETURNS trigger AS $$
DECLARE
  delta numeric := 0; art integer; q numeric;
BEGIN
  IF TG_OP <> 'INSERT' THEN delta := delta - @S@.efect_stoc(OLD.tip, OLD.cantitate); art := OLD.articol_id; END IF;
  IF TG_OP <> 'DELETE' THEN delta := delta + @S@.efect_stoc(NEW.tip, NEW.cantitate); art := NEW.articol_id; END IF;
  IF TG_OP = 'UPDATE' AND OLD.articol_id IS DISTINCT FROM NEW.articol_id THEN
    delta := -@S@.efect_stoc(OLD.tip, OLD.cantitate); art := OLD.articol_id;   -- articolul vechi pierde mișcarea întreagă
  END IF;
  IF delta < 0 THEN
    SELECT COALESCE(SUM(@S@.efect_stoc(m.tip, m.cantitate)), 0) INTO q FROM @S@.miscari_stoc m WHERE m.articol_id = art;
    IF q + delta < 0 THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Stocul articolului #% ar deveni negativ (% după mișcarea „%”): o ieșire nu poate scoate mai mult decât e în stoc.',
        art, q + delta, COALESCE(CASE WHEN TG_OP = 'DELETE' THEN OLD.document ELSE NEW.document END, 'fără document');
    END IF;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_stoc_nenegativ ON @S@.miscari_stoc;
CREATE TRIGGER trg_regula_stoc_nenegativ BEFORE INSERT OR UPDATE OR DELETE ON @S@.miscari_stoc
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_stoc_nenegativ();

CREATE OR REPLACE FUNCTION @S@.regula_chitanta() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'REGULA_CONTABILA: Chitanța % nr. % e emisă, deci nu se șterge: se anulează și se păstrează (OMFP 2634/2015, Anexa 1 pct.15).',
    OLD.serie, OLD.numar;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_chitanta ON @S@.chitante;
CREATE TRIGGER trg_regula_chitanta BEFORE DELETE ON @S@.chitante
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_chitanta();
""" + perioada + "@SF@").replace("@INC@", MARCAJ_INCEPUT).replace("@SF@", MARCAJ_SFARSIT).replace(
        "@NESTERGIBILA@", _nsf.clauza_sql_nestergibila()).replace("@S@", s)


#: R7 pe tabelul comun (o singură dată, nu pe schemă)
SQL_DECLARATII = """
CREATE OR REPLACE FUNCTION public.regula_declaratie_depusa() RETURNS trigger AS $$
BEGIN
  IF OLD.sursa = 'iconta' THEN
    IF TG_OP = 'DELETE' THEN
      IF current_database() = 'iconta_v2' OR current_setting('iconta.regula_declaratii', true) = 'activa' THEN
        RAISE EXCEPTION 'REGULA_CONTABILA: Declarația % pe %/% e depusă prin iConta.eu, deci nu se șterge: o corectură e o depunere nouă (rectificativa).',
          upper(OLD.tip), LPAD(OLD.luna::text, 2, '0'), OLD.an;
      END IF;
      RETURN OLD;
    END IF;
    IF (NEW.tenant_id, NEW.an, NEW.luna, NEW.tip, NEW.xml, NEW.randuri::text, NEW.data_depunere, NEW.nr_depunere, NEW.sursa)
       IS DISTINCT FROM (OLD.tenant_id, OLD.an, OLD.luna, OLD.tip, OLD.xml, OLD.randuri::text, OLD.data_depunere, OLD.nr_depunere, OLD.sursa) THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Declarația % pe %/% e depusă prin iConta.eu, deci nu se modifică: o corectură e o depunere nouă (rectificativa).',
        upper(OLD.tip), LPAD(OLD.luna::text, 2, '0'), OLD.an;
    END IF;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_declaratie_depusa ON public.declaratii_depuse;
CREATE TRIGGER trg_regula_declaratie_depusa BEFORE UPDATE OR DELETE ON public.declaratii_depuse
  FOR EACH ROW EXECUTE FUNCTION public.regula_declaratie_depusa();
"""


def aplica(conn, schema):
    """True dacă a aplicat; None dacă schema n-are tabelele (nu e o firmă)."""
    if not db.schema_valida(schema):
        raise _SchemaInvalida(schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name IN "
                    "('facturi', 'miscari_stoc', 'casa_operatiuni', 'chitante', 'perioade_blocate')", (schema,))
        if cur.fetchone()[0] < 5:
            return None
        cur.execute(sql('"%s"' % schema))
    return True


def aplica_declaratii(conn):
    with conn.cursor() as cur:
        cur.execute(SQL_DECLARATII)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica_declaratii(conn)
        conn.commit()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    n = 0
    for s in scheme:
        with db.get_conn() as conn:
            if aplica(conn, s):
                n += 1
            conn.commit()
    print("regulile de fond 2 (a, c, d, e, f): declarațiile + %d / %d scheme" % (n, len(scheme)))


if __name__ == "__main__":
    _main()
