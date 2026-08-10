# -*- coding: utf-8 -*-
"""Valideaza prin DUKIntegrator toate declaratiile pe cele 4 firme (4163). Output incremental."""
from core import db, duk, declaratii_api
from core import d100, d300, d394, d390, d112, d205, d101, d301, d406
from core.common import Perioada

db.init_pool()
FIRME = [("tenant_013", "ALFA"), ("tenant_014", "BETA"), ("tenant_015", "GAMA"), ("tenant_016", "DELTA")]
AN, LUNA, TRIM = 2026, 8, 3


def gen(tip, conn, sch):
    if tip == "d100": return d100.genereaza(conn, sch, Perioada(AN, trim=TRIM))
    if tip == "d300": return d300.genereaza(conn, sch, Perioada(AN, luna=LUNA))
    if tip == "d394": return d394.genereaza(conn, sch, Perioada(AN, luna=LUNA))
    if tip == "d205": return d205.genereaza(conn, sch, Perioada(AN))
    if tip == "d101": return d101.genereaza(conn, sch, Perioada(AN))
    if tip == "d301": return d301.genereaza(conn, sch, Perioada(AN, luna=LUNA))
    if tip == "d390": return d390.genereaza(conn, sch, AN, LUNA)
    if tip == "d112": return d112.genereaza(conn, sch, AN, LUNA)
    if tip == "d406": return d406.genereaza(conn, sch, AN, LUNA)


TIPURI = ["d100", "d300", "d394", "d390", "d112", "d205", "d101", "d301", "d406"]
print("FIRMA | TIP | genereaza | DUK | total_plata_a/op | zero-suspect | erori", flush=True)
for sch, nm in FIRME:
    for tip in TIPURI:
        try:
            with db.get_conn(sch) as conn:
                xml, res = gen(tip, conn, sch)
        except Exception as e:
            print("%-5s %-5s | BLOCAT/EROARE: %s" % (nm, tip, str(e).splitlines()[0][:90]), flush=True)
            continue
        op = declaratii_api.numar_operatiuni(tip, res)
        tpa = getattr(res, "total_plata_a", None)
        av = getattr(res, "avertismente", None)
        if av is None and isinstance(res, list):
            av = res
        avz = [a for a in (av or []) if isinstance(a, str) and ("zero" in a.lower() or "factur" in a.lower())]
        try:
            v = duk.valideaza(xml, tip, an=AN, luna=LUNA, timeout=110)
            st = v.get("stare"); er = (v.get("erori") or "").replace("\n", " ")[:130]
        except Exception as e:
            st = "gri(exc)"; er = str(e)[:90]
        print("%-5s %-5s | da | %-6s | tpa=%s op=%s | %s | %s" % (
            nm, tip, st, tpa, op, ("DA:" + avz[0][:36] if avz else "nu"), er), flush=True)
print("=== gata ===", flush=True)
