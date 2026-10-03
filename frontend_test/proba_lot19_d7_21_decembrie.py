# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 7: termenul obligațiilor cu scadența 25 decembrie (luna noiembrie).

    python frontend_test/proba_lot19_d7_21_decembrie.py <radacina_cod>
F1 (tenant_049) și F3 (tenant_051) din baza de producție, calea aplicației: `firma_rezumat._termene_una_firma` (blocul
per firmă al ecranului «Termene» / lista de 60 de zile), ziua de referință 01.12.2026, plus `cashflow.plati_estimate`.
Numai citire (nicio scriere), conexiunea se anulează.
  · cod VECHI: D300/D112/D390 pentru noiembrie 2026 cu termen 28.12.2026;
  · cod NOU: 21.12.2026 (CPF art.155 alin.(2)).
"""
import datetime
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, firma_rezumat, scadente, cashflow  # noqa: E402

observare.alerteaza = lambda *a, **k: None
print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(scadente, "termen_legal") else "VECHI"))
AZI = datetime.date(2026, 12, 1)
db.init_pool()
with db.get_conn() as c:
    cur = c.cursor()
    cur.execute("SELECT id, nume, cui, accounting_firm_id FROM public.tenants "
                "WHERE schema_name IN ('tenant_049','tenant_051') ORDER BY schema_name")
    firme = cur.fetchall()
    cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (firme[0][3],))
    uid = cur.fetchone()[0]
    c.rollback()
for tid, nume, cui, _cab in firme:
    ev, neev = firma_rezumat._termene_una_firma({"id": tid, "nume": nume, "cui": cui},
                                                {"uid": uid, "rol": "admin_firma"}, AZI)
    if neev:
        print("  %s: neevaluat — %s" % (nume, neev))
        continue
    nov = [t for t in ev["termene"] if t["an"] == 2026 and t["luna"] == 11]
    print("  %s, termene pentru noiembrie 2026 (văzute la %s):" % (nume, AZI.strftime("%d.%m.%Y")))
    for t in nov:
        print("      %-5s termen %s" % (t["tip"].upper(), t["termen"]))
print("  cashflow (azi 10.12.2026): plata obligațiilor fiscale la %s"
      % cashflow.plati_estimate({"fiscale": 1000}, 0, azi=datetime.date(2026, 12, 10))[0]["data_scadenta"])
