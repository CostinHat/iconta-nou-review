# -*- coding: utf-8 -*-
"""core/migrare_reguli_fond.py — regulile de fond puse în BAZA DE DATE, nu în ecrane (comanda Costin 09.10.2026, pct.11, verbatim în
DECIZII: „Reguli de fond puse în baza de date, nu în ecrane, ca să nu le poată ocoli niciun drum, nici unul viitor: o notă validată
nu se modifică și nu se șterge, iar corectura se face doar prin stornare; o lună blocată nu primește note; fiecare notă are
documentul-sursă; fiecare notă are debit egal cu credit; o mișcare de stoc a unui document contat nu se desface decât printr-un
document de corecție.”).

Regulile (triggere pe fiecare schemă de firmă; mesajul poartă eticheta `REGULA_CONTABILA:`, pe care handlerul global din `main.py` o
arată contabilului ca 409, ca pe `PERIOADA_BLOCATA:` -> 423):
  R1  nota VALIDATĂ nu se modifică (data, numărul, factura, documentul, descrierea, sursa, starea) și nu se șterge; rândurile ei nu
      se adaugă / schimbă / șterg. Temei: OMFP 1802/2014 pct.69 (corectarea prin stornare). *INTERPRETARE:* „validată” = validată
      ÎNTR-O TRANZACȚIE ÎNCHEIATĂ — construirea completă a notei în tranzacția care o creează (nota, rândurile, documentul) nu e o
      modificare a evidenței: nimeni n-a văzut-o încă (`nota_din_tranzactia_curenta`: `xmin` încă „in progress”, deci al tranzacției curente sau al unei sub-tranzacții a ei). [09.10.2026,
      prins de suita completă: forma strictă refuza construirea notei validate în aceeași tranzacție, drum folosit de fixturi și
      posibil de un import viitor.]
  R2  luna blocată (`perioade_blocate`) nu primește note — exista (`trg_verifica_perioada_blocata`, #66); închise două goluri: la
      UPDATE se verifica numai data NOUĂ (o notă se putea muta AFARĂ dintr-o lună blocată), iar rândurile notei
      (`inregistrari_linii`, fără dată proprie) nu treceau prin nicio verificare.
  R3  documentul-sursă: o notă nu devine VALIDATĂ fără documentul justificativ — ACEEAȘI definiție ca a aplicației
      (`jurnal_api.document_justificativ`: `document_ref` scris pe notă, altfel factura legată prin `factura_id`; paritatea e păzită
      de `core/test_reguli_fond.py`). [09.10.2026, prins de proba blocului E] prima formă cerea numai `document_ref` și refuza
      validarea notei de contare a unei facturi (document_ref gol, documentul e factura). *INTERPRETARE:* regula se aplică la
      validare, nu la ciornă: la ACTUL de validare (trecerea ciornă -> validată), imediat. [09.10.2026] O formă amânată la COMMIT a fost
      încercată și abandonată: evenimentele amânate opresc `DROP SCHEMA` în aceeași tranzacție. Inserarea DIRECTĂ a unei note deja
      validate nu trece prin actul de validare: azi nu există în aplicație (căutat), iar `core/test_reguli_fond.py` pică dacă apare
      în cod un `INSERT INTO inregistrari` cu starea `validata` în afara testelor și a migrărilor —
      ciorna e lucru în curs (aplicația o lasă deliberat fără document până la validare: `jurnal_api.editeaza`), iar evidența e ce a
      validat un om (decizia Costin 08.10, R36). De reconfirmat de Costin.
  R4  debit = credit: garantat de MODEL — fiecare rând e o pereche (`cont_debit`, `cont_credit`, `suma`, toate NOT NULL), deci nu
      există rând cu o singură parte; regula pusă aici e ce mai poate strica perechea: niciun cont gol.
  R5  mișcarea de stoc ÎN EVIDENȚĂ (`stocuri_anulare.IN_EVIDENTA`, aceeași definiție, generată de aici în funcția
      `miscare_in_evidenta`) nu se modifică și nu se șterge; o stornare a ei (`anuleaza_id`) se scrie numai cu documentul de corecție:
      o notă NOUĂ, în ciornă, alta decât nota mișcării stornate.
ORDINEA pe producție: reparația tenant_049 (`migrare_nota_corectie`) ÎNAINTE — rândurile ei greșite de stornare n-ar mai putea fi
scoase după R5. Idempotentă (CREATE OR REPLACE + DROP/CREATE TRIGGER). Oglinda în `tenant_template.sql` e generată de `sql(...)` și
păzită de `core/test_reguli_fond.py`. Rulare: `python -m core.migrari_registru ruleaza --productie core/migrare_reguli_fond.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [reguli_fond_v1, 09.10.2026] regulile de fond în bază (comanda Costin pct.11) — SURSA: core/migrare_reguli_fond.py"
MARCAJ_SFARSIT = "-- [reguli_fond_v1] sfârșit"


def sql(s):
    """DDL-ul regulilor pentru schema `s` (numele exact, sau `TENANT_PLACEHOLDER` pentru șablon)."""
    from core.stocuri_anulare import IN_EVIDENTA
    in_evidenta = IN_EVIDENTA.format(s=s)
    return """@INC@
CREATE OR REPLACE FUNCTION @S@.nota_din_tranzactia_curenta(nid integer) RETURNS boolean AS $$
  -- rândul vizibil al cărui `xmin` e încă „in progress” poate fi numai al tranzacției curente (și al sub-tranzacțiilor ei, care au
  -- identificatori MAI MARI decât ea); `xmin` e pe 32 de biți: se pune epoca curentă, iar numai un `xmin` cu peste 2^31 înaintea
  -- tranzacției curente e din epoca anterioară; un rezultat negativ sau NULL (prea vechi) = nu e al tranzacției
  SELECT COALESCE((
    SELECT pg_xact_status(y::text::xid8) = 'in progress'
      FROM (SELECT CASE WHEN x - c > 2147483648 THEN x - 4294967296 ELSE x END AS y
              FROM (SELECT ((k.c >> 32) << 32) | i.xmin::text::bigint AS x, k.c
                      FROM @S@.inregistrari i, (SELECT pg_current_xact_id()::text::bigint AS c) k WHERE i.id = nid) t) u
     WHERE y >= 0), false)
$$ LANGUAGE sql VOLATILE;

CREATE OR REPLACE FUNCTION @S@.regula_nota() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status = 'validata' AND NOT @S@.nota_din_tranzactia_curenta(OLD.id) THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Nota #% e validată, deci nu se mai șterge. Corectura se face prin stornare (OMFP 1802/2014 pct.69).', OLD.id;
    END IF;
    RETURN OLD;
  END IF;
  IF TG_OP = 'UPDATE' AND OLD.status = 'validata' AND NOT @S@.nota_din_tranzactia_curenta(OLD.id)
     AND (NEW.data, NEW.numar, NEW.factura_id, NEW.document_ref, NEW.descriere, NEW.sursa, NEW.status)
         IS DISTINCT FROM (OLD.data, OLD.numar, OLD.factura_id, OLD.document_ref, OLD.descriere, OLD.sursa, OLD.status) THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Nota #% e validată, deci nu se mai modifică. Corectura se face prin stornare (OMFP 1802/2014 pct.69).', OLD.id;
  END IF;
  IF NEW.status = 'validata' AND OLD.status IS DISTINCT FROM 'validata' AND COALESCE(btrim(NEW.document_ref), '') = ''
     AND NOT EXISTS (SELECT 1 FROM @S@.facturi f WHERE f.id = NEW.factura_id) THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Nota #% n-are documentul justificativ: o notă nu se validează fără documentul din care provine.', NEW.id;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_nota ON @S@.inregistrari;
CREATE TRIGGER trg_regula_nota BEFORE UPDATE OR DELETE ON @S@.inregistrari
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_nota();

CREATE OR REPLACE FUNCTION @S@.verifica_perioada_blocata() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.data END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.data END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM @S@.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_verifica_perioada_blocata ON @S@.inregistrari;
CREATE TRIGGER trg_verifica_perioada_blocata BEFORE INSERT OR UPDATE OR DELETE ON @S@.inregistrari
  FOR EACH ROW EXECUTE FUNCTION @S@.verifica_perioada_blocata();

CREATE OR REPLACE FUNCTION @S@.regula_linii_nota() RETURNS trigger AS $$
DECLARE
  nid integer; st text; d date;
BEGIN
  IF TG_OP <> 'DELETE' AND (COALESCE(btrim(NEW.cont_debit), '') = '' OR COALESCE(btrim(NEW.cont_credit), '') = '') THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Un rând de notă are nevoie de ambele conturi, debitor și creditor: debitul e egal cu creditul numai așa.';
  END IF;
  FOREACH nid IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.inregistrare_id END,
                            CASE WHEN TG_OP <> 'DELETE' THEN NEW.inregistrare_id END] LOOP
    CONTINUE WHEN nid IS NULL;
    SELECT status, data INTO st, d FROM @S@.inregistrari WHERE id = nid;
    IF st = 'validata' AND NOT @S@.nota_din_tranzactia_curenta(nid) THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Nota #% e validată, deci rândurile ei nu se mai schimbă. Corectura se face prin stornare (OMFP 1802/2014 pct.69).', nid;
    END IF;
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM @S@.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_linii_nota ON @S@.inregistrari_linii;
CREATE TRIGGER trg_regula_linii_nota BEFORE INSERT OR UPDATE OR DELETE ON @S@.inregistrari_linii
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_linii_nota();

CREATE OR REPLACE FUNCTION @S@.miscare_in_evidenta(mid integer) RETURNS boolean AS $$
  SELECT EXISTS (SELECT 1 FROM @S@.miscari_stoc m WHERE m.id = mid AND @EV@)
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION @S@.regula_stoc() RETURNS trigger AS $$
DECLARE
  nota_tinta integer; st text;
BEGIN
  IF TG_OP <> 'INSERT' AND @S@.miscare_in_evidenta(OLD.id) THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Mișcarea de stoc „%” e a unui document contat: nu se modifică și nu se șterge. Se corectează printr-un document de corecție.', OLD.document;
  END IF;
  IF TG_OP <> 'DELETE' AND NEW.anuleaza_id IS NOT NULL AND @S@.miscare_in_evidenta(NEW.anuleaza_id) THEN
    SELECT inregistrare_id INTO nota_tinta FROM @S@.miscari_stoc WHERE id = NEW.anuleaza_id;
    SELECT status INTO st FROM @S@.inregistrari WHERE id = NEW.inregistrare_id;
    IF NEW.inregistrare_id IS NULL OR NEW.inregistrare_id IS NOT DISTINCT FROM nota_tinta OR st IS DISTINCT FROM 'ciorna' THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Mișcarea de stoc #% e a unui document contat: se stornează numai cu un document de corecție (o notă nouă, în ciornă).', NEW.anuleaza_id;
    END IF;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_stoc ON @S@.miscari_stoc;
CREATE TRIGGER trg_regula_stoc BEFORE INSERT OR UPDATE OR DELETE ON @S@.miscari_stoc
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_stoc();
@SF@""".replace("@INC@", MARCAJ_INCEPUT).replace("@SF@", MARCAJ_SFARSIT).replace("@EV@", in_evidenta).replace("@S@", s)


def aplica(conn, schema):
    """True dacă a aplicat; None dacă schema n-are tabelele (nu e o firmă)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name IN "
                    "('inregistrari', 'inregistrari_linii', 'miscari_stoc', 'perioade_blocate', 'nir')", (schema,))
        if cur.fetchone()[0] < 5:
            return None
        cur.execute(sql('"%s"' % schema))
    return True


def _main():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    n = 0
    for s in scheme:
        with db.get_conn() as conn:
            if aplica(conn, s):
                n += 1
            conn.commit()
    print("regulile de fond: aplicate pe %d / %d scheme" % (n, len(scheme)))


if __name__ == "__main__":
    _main()
