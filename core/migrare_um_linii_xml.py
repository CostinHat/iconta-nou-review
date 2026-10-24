"""
core/migrare_um_linii_xml.py — unitatea de măsură a liniilor facturilor importate din XML (lotul 12, deficiența C104).

DEFECTUL. Importul XML e-Factura (`efactura_import.parseaza_xml` -> `repo_main.insert_factura_linii`) nu citea BT-130 („Invoiced quantity
unit of measure code”, `cbc:InvoicedQuantity/@unitCode`, coduri UN/ECE Rec 20): fiecare linie intra cu implicitul coloanei, „buc”, iar
intrarea în stoc din factură crea articolul nou tot în „buc” — 50 m de cablu și 12,5 kg de detergent (fișierul de probă F1 DNT-RT-1020).

REGULA DE STRUCTURĂ (nu normă; EN 16931): BT-130 e obligatoriu pe fiecare linie (BR-23), iar unitatea aplicației se află din cod prin harta
e-Factura (`efactura_send.um_din_unece`, inversul lui `efactura_send._UM` — sursa unică).

DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): facturile cu XML păstrat (`facturi.xml`
nenul) primesc pe liniile-articol (`nivel_document` false) unitatea din XML, în ordinea liniilor — numai când numărul lor e numărul
`cac:InvoiceLine` din XML (altfel potrivirea ar fi ghicită: factura se numește și se sare) și numai unde linia are încă implicitul „buc”
(o unitate pusă de om nu se rescrie). E o CITIRE a documentului: cantitatea, prețul, notele și declarațiile depuse nu se ating.
ARTICOLELE DIN STOC create din aceste facturi NU se schimbă (un articol poate fi folosit și de alte documente, iar cantitățile din fișă
sunt deja scrise): cele a căror unitate diferă de a liniei se NUMESC, ca să le corecteze contabilul în Produse (decizie cerută în raportul
lotului 12, pachetul `scad`). Idempotentă.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_um_linii_xml.py`.
"""
from core import db
from core.common import cate as _cate

IMPLICIT = "buc"


def unitati_din_xml(xml):
    """PURĂ. [unitatea iConta a fiecărei `cac:InvoiceLine`, în ordinea din XML] (None = linia n-are `unitCode`)."""
    import xml.etree.ElementTree as ET
    from core import efactura_import as _ef, efactura_send as _es
    if isinstance(xml, (bytes, bytearray)):
        xml = xml.decode("utf-8-sig", errors="replace")
    root = ET.fromstring(xml)
    out = []
    for ln in root.findall("cac:InvoiceLine", _ef.NS):
        q = ln.find("cbc:InvoicedQuantity", _ef.NS)
        out.append(_es.um_din_unece(q.get("unitCode") if q is not None else None))
    return out


def aplica(conn, schema):
    """Unitatea din XML pe liniile facturilor importate înainte de reparație. Întoarce {"linii", "sarite": [(id, motiv)],
    "articole": [(id_articol, denumire, um_articol, um_linie, factura)]} — articolele din stoc cu altă unitate decât linia lor."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    rez = {"linii": 0, "sarite": [], "articole": []}
    with conn.cursor() as cur:
        cur.execute('SELECT f.id, f.numar, f.xml FROM "%s".facturi f WHERE f.xml IS NOT NULL AND btrim(f.xml) <> \'\' ORDER BY f.id' % schema)
        for fid, numar, xml in cur.fetchall():
            try:
                um_xml = unitati_din_xml(xml)
            except Exception as e:  # noqa: BLE001 — XML-ul păstrat nu se mai citește: se numește, liniile rămân cum sunt
                rez["sarite"].append((fid, "XML-ul nu se poate citi: %s" % str(e)[:120]))
                continue
            cur.execute('SELECT id, um FROM "%s".factura_linii WHERE factura_id = %%s AND NOT nivel_document ORDER BY id' % schema, (fid,))
            linii = cur.fetchall()
            if len(linii) != len(um_xml):
                rez["sarite"].append((fid, "are %s în bază și %s în XML — potrivirea nu se ghicește" % (
                    _cate(len(linii), "linie", "linii"), _cate(len(um_xml), "linie", "linii"))))
                continue
            for (lid, um), u in zip(linii, um_xml):
                if u and u != IMPLICIT and (um or IMPLICIT) == IMPLICIT:
                    cur.execute('UPDATE "%s".factura_linii SET um = %%s WHERE id = %%s' % schema, (u, lid))
                    rez["linii"] += 1
            cur.execute('SELECT DISTINCT a.id, a.denumire, a.um, l.um FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id '
                        'JOIN "%s".factura_linii l ON l.factura_id = m.factura_id AND lower(btrim(l.descriere)) = lower(btrim(a.denumire)) '
                        "WHERE m.factura_id = %%s AND a.um IS DISTINCT FROM l.um" % (schema, schema, schema), (fid,))
            rez["articole"] += [(aid, den, uma, uml, numar) for aid, den, uma, uml in cur.fetchall()]
    return rez


def verifica(conn, schema):
    """Nicio linie-articol cu XML păstrat rămasă pe „buc” când XML-ul ei spune altă unitate (pe facturile potrivibile)."""
    r = aplica(conn, schema)
    conn.rollback()
    return r["linii"] == 0


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
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            total += r["linii"]
            for fid, motiv in r["sarite"]:
                print("  %s: factura #%s sărită — %s" % (s, fid, motiv))
            for aid, den, uma, uml, numar in r["articole"]:
                print("  %s: articolul #%s „%s” e în „%s”, iar linia facturii %s spune „%s” — de corectat în Produse"
                      % (s, aid, den, uma, numar, uml))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_um_linii_xml: %d ok, %d esec, %d linii cu unitatea din XML" % (ok, len(esec), total))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
