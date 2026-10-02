# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — factura emisă pe baza bonului fiscal (decizia Costin A, 02.10.2026). Cod vechi vs nou.

    python frontend_test/proba_factura_bon.py <radacina_cod>
F1 (tenant_049, plătitor lunar), septembrie 2026, într-o tranzacție ANULATĂ: un raport Z validat (bonurile zilei, 1.210 lei
la 21%), apoi o factură emisă clientului pentru unul dintre bonuri (100 + 21 TVA). Codul vechi nu poate marca factura
(câmpul nu există) — o emite ca pe o vânzare nouă; codul nou o marchează „conform bon fiscal nr./data”.
Se citesc: nota contabilă a facturii, D300 rd.9 (față de 4427 din evidență), D394 op1 + op2 Î1, DUK.
"""
import inspect
import os
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, facturi_api, d300, d394, duk, raport_z  # noqa: E402
from core.common import Perioada  # noqa: E402

observare.alerteaza = lambda *a, **k: None
NOU = "bon_fiscal_nr" in inspect.signature(facturi_api.creeaza_factura).parameters
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
S = "tenant_049"
db.init_pool()
with db.get_conn() as conn:
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO %s, public" % S)
        raport_z.aplica_tabel_cote(conn, S)
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) VALUES "
                    "('2026-09-10','Z-8000000101-0031','proba bon->factura','horeca_z','validata') RETURNING id")
        iz = cur.fetchone()[0]
        for dbt, cr, s_ in (("5311", "707", 1210), ("707", "4427", 210)):
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (iz, dbt, cr, s_))
        cur.execute("INSERT INTO rapoarte_z_cote (inregistrare_id, cota, baza, tva) VALUES (%s,21,1000,210)", (iz,))
        cur.execute("SELECT to_regclass('rapoarte_z_amef')")
        if cur.fetchone()[0]:
            cur.execute("INSERT INTO rapoarte_z_amef (inregistrare_id, nui, nr_bonuri) VALUES (%s,'8000000101',160)", (iz,))
        marca = {"bon_fiscal_nr": "0042", "bon_fiscal_data": "2026-09-10"} if NOU else {}
        r = facturi_api.creeaza_factura(conn, "PROBA-BON-1", "2026-09-10", "emisa",
                                        [{"descriere": "Meniu zilei", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21,
                                          "um": "buc", "cont_venit": "707"}],
                                        tert_nume="CLIENT SRL", tert_cui="RO14399840", status="emisa", **marca)
        cur.execute("UPDATE inregistrari SET status='validata' WHERE factura_id=%s", (r["factura_id"],))
        cur.execute("SELECT count(*) FROM inregistrari WHERE factura_id=%s", (r["factura_id"],))
        print("  factura PROBA-BON-1: contare=%s · note de vânzare pe factură: %s" % (r["contare"].get("stare"), cur.fetchone()[0]))
        cur.execute("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l JOIN inregistrari i ON i.id=l.inregistrare_id "
                    "WHERE i.status='validata' AND l.cont_credit='4427' AND i.data>='2026-09-01' AND i.data<'2026-10-01'")
        c4427 = Decimal(cur.fetchone()[0])
        print("  TVA colectat în evidență (credit 4427, sept., toată firma): %s lei (Z-ul probei adaugă 210; factura din bon, 21 dacă e contată)" % c4427)
        cur.execute("SAVEPOINT p300")
        try:
            x3, res = d300.genereaza(conn, S, Perioada(2026, luna=9))
            v3 = duk.valideaza(x3, "d300", an=2026, luna=9, timeout=180)
            print("  D300 rd.9: baza %s / TVA %s · DUK D300: %s %s" % (res.R.get("R9_1"), res.R.get("R9_2"), v3["stare"],
                                                                    (v3.get("erori") or "").replace("\n", " ")[:200]))
        except Exception as e:
            print("  D300 REFUZ: %s" % str(e)[:300])
        cur.execute("ROLLBACK TO SAVEPOINT p300")
        try:
            xml, _r = d394.genereaza(conn, S, Perioada(2026, luna=9))
            rad = ET.fromstring(xml.split("?>", 1)[1])
            ns = rad.tag.split("}")[0] + "}"
            o2 = [e.attrib for e in rad.iter(ns + "op2")]
            o1 = [(e.get("tip"), e.get("cuiP"), e.get("baza"), e.get("tva")) for e in rad.iter(ns + "op1") if e.get("cuiP") == "14399840"]
            print("  D394 op1 (CLIENT SRL): %s · op2: %s" % (o1, [(o.get("total"), o.get("baza21"), o.get("TVA21")) for o in o2]))
            v = duk.valideaza(xml, "d394", an=2026, luna=9, timeout=180)
            print("  DUK D394: %s %s" % (v["stare"], (v.get("erori") or "").replace("\n", " ")[:200]))
        except Exception as e:
            print("  D394 REFUZ: %s" % str(e)[:300])
    finally:
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
