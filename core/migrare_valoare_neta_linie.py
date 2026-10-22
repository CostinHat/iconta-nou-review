"""
core/migrare_valoare_neta_linie.py — valoarea netă a liniei de pe factură, păstrată exact (lotul 11, C82).

DEFECTUL. `factura_linii.pret_unitar` e `numeric(12,2)`. Importul XML scrie acolo `LineExtensionAmount / cantitate` (prețul EFECTIV,
`efactura_import._pret_efectiv`), iar toți consumatorii refac valoarea liniei ca `cantitate × pret_unitar`. Pe o cantitate neîntreagă
împărțirea nu încape în 2 zecimale: 100,00 / 3,333 = 30,0030003… -> 30,00, iar 3,333 × 30,00 = 99,99 — baza liniei pierde un ban față
de factură (BT-131), deci și baza cotei, nota, D300, D394, D406.

REGULA DE STRUCTURĂ (nu normă; EN 16931, artefactele CEN `EN16931-model.sch`): BR-DEC-23 „The allowed maximum number of decimals for the
Invoice line net amount (BT-131) is 2.” — valoarea netă a liniei e o sumă la ban, scrisă pe factură; BR-CO-10 „Sum of Invoice line net
amount (BT-106) = Σ Invoice line net amount (BT-131).” Valoarea liniei e deci cea de pe factură, nu una refăcută din preț.

CE FACE:
1. Coloana `factura_linii.valoare_neta numeric(15,2)` (NULL = linia n-are valoare scrisă separat — factura făcută în aplicație, unde
   valoarea e chiar `net_linie(cantitate, preț)`, BR-DEC-23). O scrie importul (`repo_main.insert_factura_linii`); o citesc regula unică
   (`tva_calcul.net_linie` / `pe_cote`), D300, D394, D406 și căile lor a doua.
   [C80] `factura_linii.nivel_document` (implicit false): linia e o reducere / taxă la nivelul FACTURII (BG-20 / BG-21, scrisă de import ca
   linie pe cota ei — `efactura_import.linii_nivel_document`), nu un articol: recepția în stoc o împarte pe liniile de stoc ale cotei, nu
   face din ea un articol.
2. DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): facturile importate din XML (`facturi.xml`
   nenul) se completează din XML-ul păstrat — BT-131 pe liniile lor, în ordinea liniilor (numai când numărul liniilor-articol din bază e
   numărul `cac:InvoiceLine` din XML; altfel potrivirea ar fi ghicită: factura se numește și se sare), iar reducerile / taxele de document
   ca linii `nivel_document` (C80). E o CITIRE a documentului: prețul, cantitatea, notele și stocul rămân neatinse; o factură care avea
   deja nota contării și primește linii de document se NUMEȘTE (`aplica`). Idempotentă.
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (păzit de core/test_lot11_y2_import_fidel.py).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_valoare_neta_linie.py`.
"""
from core import db
from core.common import cate as _cate

MARCAJ_INCEPUT = "-- [valoare_neta_linie_v1, lotul 11, C82 / C80] BT-131 al liniei, exact; linia de document — SURSA: core/migrare_valoare_neta_linie.py"
MARCAJ_SFARSIT = "-- [valoare_neta_linie_v1] sfârșit"


def sql(s):
    return ("ALTER TABLE %(s)s.factura_linii ADD COLUMN IF NOT EXISTS valoare_neta numeric(15,2);\n"
            "ALTER TABLE %(s)s.factura_linii ADD COLUMN IF NOT EXISTS nivel_document boolean NOT NULL DEFAULT false;") % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def valori_din_xml(xml):
    """PURĂ. [BT-131 al fiecărei `cac:InvoiceLine`, în ordinea din XML] (text sau None)."""
    return [v for v, _doc in _din_xml(xml)[0]]


def _din_xml(xml):
    """PURĂ. ([(BT-131, None)] ale liniilor, [linia de document]) — liniile de document cum le scrie importul
    (`efactura_import.linii_nivel_document`)."""
    import xml.etree.ElementTree as ET
    from core import efactura_import as _ef
    if isinstance(xml, (bytes, bytearray)):
        xml = xml.decode("utf-8-sig", errors="replace")
    root = ET.fromstring(xml)
    return ([((_ef._txt(ln, "cbc:LineExtensionAmount") or None), None) for ln in root.findall("cac:InvoiceLine", _ef.NS)],
            _ef.linii_nivel_document(root))


def aplica(conn, schema):
    """DDL + datele facturilor importate din XML înainte de reparație („Orice reparație acoperă și datele existente”, comanda Costin 11.2
    pct.3):
      * [C82] BT-131 pe liniile lor (`valoare_neta`), în ordinea liniilor, numai când numărul liniilor-articol din bază e numărul
        `cac:InvoiceLine` din XML — altfel potrivirea ar fi ghicită: factura se numește și se sare;
      * [C80] reducerile / taxele de document (BG-20 / BG-21) ca linii `nivel_document`, cum le scrie importul acum — numai pe o factură
        care nu le are deja (idempotent).
    Notele contabile, stocul și declarațiile depuse NU se ating: o factură care avea deja nota contării și primește acum linii de document
    se NUMEȘTE (nota ei a fost scrisă pe baza fără reducere; o ciornă se vede depășită la validare — `ciorne_depasite` —, o notă validată
    o reface omul). Întoarce {"linii_bt131", "linii_document", "sarite": [(id, motiv)], "cu_nota": [(id, număr)]}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import repo_main as _rm
    rez = {"linii_bt131": 0, "linii_document": 0, "sarite": [], "cu_nota": []}
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))
        cur.execute('SELECT f.id, f.numar, f.xml FROM "%s".facturi f WHERE f.xml IS NOT NULL AND btrim(f.xml) <> \'\' ORDER BY f.id' % schema)
        for fid, numar, xml in cur.fetchall():
            try:
                linii_xml, doc_xml = _din_xml(xml)
            except Exception as e:  # noqa: BLE001 — XML-ul păstrat nu se mai citește: se numește, factura rămâne pe liniile ei
                rez["sarite"].append((fid, "XML-ul nu se poate citi: %s" % str(e)[:120]))
                continue
            cur.execute('SELECT id, valoare_neta, nivel_document FROM "%s".factura_linii WHERE factura_id = %%s ORDER BY id' % schema, (fid,))
            toate = cur.fetchall()
            articole = [(lid, vn) for lid, vn, nd in toate if not nd]
            if any(vn is None for _lid, vn in articole):
                if len(articole) != len(linii_xml):
                    rez["sarite"].append((fid, "are %s în bază și %s în XML — potrivirea nu se ghicește" % (_cate(len(articole), "linie", "linii"), _cate(len(linii_xml), "linie", "linii"))))
                else:
                    for (lid, vn), (v, _x) in zip(articole, linii_xml):
                        if vn is None and v is not None:
                            cur.execute('UPDATE "%s".factura_linii SET valoare_neta = %%s WHERE id = %%s' % schema, (v, lid))
                            rez["linii_bt131"] += 1
            if doc_xml and not any(nd for _lid, _vn, nd in toate):
                for d in doc_xml:
                    _rm.insert_factura_linii(cur, '"%s"' % schema, fid, d)
                    rez["linii_document"] += 1
                cur.execute('SELECT 1 FROM "%s".inregistrari WHERE factura_id = %%s LIMIT 1' % schema, (fid,))
                if cur.fetchone():
                    rez["cu_nota"].append((fid, numar))
    return rez


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = 'factura_linii' "
                    "AND column_name IN ('valoare_neta', 'nivel_document')", (schema,))
        return cur.fetchone()[0] == 2


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, total, total_doc = 0, [], 0, 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            total += r["linii_bt131"]
            total_doc += r["linii_document"]
            for fid, motiv in r["sarite"]:
                print("  %s: factura #%s sărită — %s" % (s, fid, motiv))
            for fid, numar in r["cu_nota"]:
                print("  %s: factura #%s (%s) are nota contării scrisă fără reducerile / taxele de document — de refăcut contarea"
                      % (s, fid, numar))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_valoare_neta_linie: %d ok, %d esec, %d linii cu BT-131 completate din XML, %d linii de document adăugate"
          % (ok, len(esec), total, total_doc))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
