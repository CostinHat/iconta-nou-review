"""
core/migrare_factura_tva_cote.py — TVA-ul de pe factură, pe cote (lotul 11, C79: contarea facturii primite recalcula TVA-ul deductibil din
baze; pe un XML e-Factura cu TVA 143,52 lei nota ieșea 143,54 lei).

TEMEI. CF art.299 alin.(1) lit.a: pentru deducere, beneficiarul trebuie „să dețină o factură emisă în conformitate cu prevederile
art. 319”; CF art.319 alin.(20) lit.j: factura cuprinde „indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei, în
funcție de cotele taxei”. Taxa dedusă e taxa înscrisă pe factură, pe cotele ei — nu o taxă recalculată de beneficiar din baze. În
XML-ul e-Factura (EN 16931) ea e defalcarea BG-23: BT-116 baza, BT-117 TVA-ul, BT-118 categoria, BT-119 cota.

CE FACE:
1. Tabela `factura_tva_cote`: un rând pe rândul de defalcare al facturii (`efactura_import.tva_cote_din_xml`), în moneda documentului.
   O scrie importul XML (`uc_tenants._factura_importata`); o citesc contarea facturii primite (`contare_facturi.tva_facturii_pe_cote`),
   D300 la rândurile deductibile (`d300.pull`) și a doua cale D300 (`d300_reconciliere`, SQL propriu).
2. DATELE EXISTENTE: facturile importate din XML înainte de tabelă (`facturi.xml` nenul) primesc rândurile din XML-ul lor păstrat —
   e o CITIRE a documentului, nu o rescriere: facturile și notele rămân neatinse. O factură care are deja rânduri nu se atinge
   (idempotent). Un XML care nu se mai poate citi se numește și se sare (factura rămâne pe liniile ei, ca înainte).
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `sql('TENANT_PLACEHOLDER')` (păzit de core/test_lot11_y_tva_primita.py).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_factura_tva_cote.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [factura_tva_cote_v1, lotul 11, C79] TVA-ul de pe factură, pe cote (BG-23) — SURSA: core/migrare_factura_tva_cote.py"
MARCAJ_SFARSIT = "-- [factura_tva_cote_v1] sfârșit"


def sql(s):
    return (
        "CREATE TABLE IF NOT EXISTS %(s)s.factura_tva_cote (\n"
        "  factura_id integer NOT NULL REFERENCES %(s)s.facturi(id) ON DELETE CASCADE,\n"
        "  nr smallint NOT NULL,\n"
        "  categorie text,\n"
        "  cota numeric(5,2) NOT NULL,\n"
        "  baza numeric(15,2) NOT NULL,\n"
        "  tva numeric(15,2) NOT NULL,\n"
        "  sursa text NOT NULL CHECK (sursa IN ('BG-23', 'BT-110')),\n"
        "  PRIMARY KEY (factura_id, nr)\n"
        ");") % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    """DDL + rândurile facturilor importate din XML înainte de tabelă. Întoarce (facturi completate, [(id, motiv)] sărite)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import efactura_import as _ef
    from core import repo_efactura as _re
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))
        cur.execute('SELECT f.id, f.xml FROM "%s".facturi f WHERE f.xml IS NOT NULL AND btrim(f.xml) <> \'\' '
                    'AND NOT EXISTS (SELECT 1 FROM "%s".factura_tva_cote t WHERE t.factura_id = f.id) ORDER BY f.id' % (schema, schema))
        rows = cur.fetchall()
        n, sarite = 0, []
        for fid, xml in rows:
            try:
                cote = _ef.tva_cote_din_xml(xml)
            except Exception as e:  # noqa: BLE001 — XML-ul păstrat nu se mai citește: se numește, factura rămâne pe liniile ei
                sarite.append((fid, "XML-ul nu se poate citi: %s" % str(e)[:120]))
                continue
            if cote and _re.salveaza_tva_cote(cur, '"%s"' % schema, fid, cote):
                n += 1
    return n, sarite


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = 'factura_tva_cote'", (schema,))
        return cur.fetchone()[0] == 1


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, total = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                n, sarite = aplica(conn, s)
                conn.commit()
            ok += 1
            total += n
            for fid, motiv in sarite:
                print("  %s: factura #%s sărită — %s" % (s, fid, motiv))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_factura_tva_cote: %d ok, %d esec, %d facturi completate din XML" % (ok, len(esec), total))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
