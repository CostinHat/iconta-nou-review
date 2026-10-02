# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — D394 op2 Î1 din rapoartele Z (decizia Costin B, 02.10.2026). INVALID pe codul vechi, VALID pe nou.

    python frontend_test/proba_d394_op2.py <radacina_cod>
F1 (tenant_049, plătitor lunar) din baza de producție, septembrie 2026. TOTUL într-o tranzacție ANULATĂ la final;
`observare.alerteaza` neutralizat. Datele probei: două rapoarte Z validate pe două case (scrise ca de rute: notă +
`rapoarte_z_cote` + `rapoarte_z_amef`, tabela creată în tranzacție dacă baza n-o are încă).
  1) codul VECHI: D394 iese fără op2 — încasările prin casa de marcat lipsesc tăcut (DUK nu are cum să vadă).
  2) codul NOU, cu un raport Z fără casă/bonuri: refuz NUMIT (cod + raportul), nu op2 pe zero.
  3) codul NOU, cu rapoartele complete: op2 Î1 (2 case, bonuri însumate), DUK valid.
"""
import os
import sys
import xml.etree.ElementTree as ET

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare  # noqa: E402
from core.common import Perioada  # noqa: E402

observare.alerteaza = lambda *a, **k: None
from core import d394, duk  # noqa: E402
NOU = hasattr(d394, "OP2_RUBRICI_NOMENCL")
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
S = "tenant_049"
Z = (("2026-09-10", "8000000101", "0031", 160, ((21, "1000.00", "210.00"), (11, "200.00", "22.00"))),
     ("2026-09-11", "8000000102", "0012", 95, ((21, "300.00", "63.00"),)))


def _scrie_z(cur, cu_amef=True):
    ids = []
    for data, nui, nr, bonuri, cote in Z:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) VALUES (%s,%s,'proba op2',"
                    "'horeca_z','validata') RETURNING id", (data, "Z-%s-%s" % (nui, nr)))
        iid = cur.fetchone()[0]
        ids.append(iid)
        tot = sum(float(b) + float(t) for _c, b, t in cote)
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'5311','707',%s)", (iid, tot))
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'707','4427',%s)",
                    (iid, sum(float(t) for _c, _b, t in cote)))
        for c, b, t in cote:
            cur.execute("INSERT INTO rapoarte_z_cote (inregistrare_id, cota, baza, tva) VALUES (%s,%s,%s,%s)", (iid, c, b, t))
        if cu_amef and NOU:
            cur.execute("INSERT INTO rapoarte_z_amef (inregistrare_id, nui, nr_bonuri) VALUES (%s,%s,%s)", (iid, nui, bonuri))
    return ids


def _arata(xml):
    rad = ET.fromstring(xml.split("?>", 1)[1])
    ns = rad.tag.split("}")[0] + "}"
    inf = rad.find(ns + "informatii")
    op2 = [dict(e.attrib) for e in rad.iter(ns + "op2")]
    print("  informatii nr_BF_i1=%s incasari_i1=%s · op_efectuate=%s · secțiuni op2: %d"
          % (inf.get("nr_BF_i1"), inf.get("incasari_i1"), rad.get("op_efectuate"), len(op2)))
    for o in op2:
        print("   op2:", o)
    v = duk.valideaza(xml, "d394", an=2026, luna=9, timeout=180)
    print("  DUK: %s%s" % (v["stare"], (" — " + (v.get("erori") or "").replace("\n", " ")[:300]) if v.get("erori") else ""))
    return op2


db.init_pool()
with db.get_conn() as conn:
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO %s, public" % S)
        if NOU:
            from core import raport_z
            raport_z.aplica_tabel_cote(conn, S)       # tabela nouă, în tranzacția probei (producția o primește la restart)
        if NOU:
            cur.execute("SAVEPOINT fara_amef")
            _scrie_z(cur, cu_amef=False)
            try:
                d394.genereaza(conn, S, Perioada(2026, luna=9))
                print("[2] Z fără casă/bonuri: GENERAT (greșit)")
            except ValueError as e:
                print("[2] Z fără casă/bonuri: REFUZ cod=%s rapoarte=%s" % (getattr(e, "cod", None), getattr(e, "rapoarte", None)))
                print("    mesaj: %s" % str(e)[:300])
            cur.execute("ROLLBACK TO SAVEPOINT fara_amef")
        _scrie_z(cur, cu_amef=True)
        cur.execute("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l JOIN inregistrari i ON i.id=l.inregistrare_id "
                    "WHERE i.status='validata' AND i.sursa='horeca_z' AND l.cont_debit='5311' AND i.data>='2026-09-01' AND i.data<'2026-10-01'")
        print("[%s] încasări prin casa de marcat în evidență (5311 din Z): %s lei" % ("3" if NOU else "1", cur.fetchone()[0]))
        try:
            xml, res = d394.genereaza(conn, S, Perioada(2026, luna=9))
            op2 = _arata(xml)
            print("  VERDICT:", "COMPLET" if op2 else "INCOMPLET — încasările prin casa de marcat lipsesc din D394")
        except Exception as e:
            print("  REFUZ: %s" % str(e)[:400])
    finally:
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
