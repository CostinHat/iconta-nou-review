# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — CASS sub 6 salarii minime (neconformitate reparată 02.10.2026). Cod vechi vs nou, aceleași date.

    python frontend_test/proba_cass_minim.py <radacina_cod>
F4 (tenant_052, PFA, partidă simplă) din baza de producție: fișa D212 pe anul 2025 (an verificat) cu două operațiuni
VALIDATE ale probei — încasare 30.000 lei, cheltuială deductibilă 10.000 lei -> venit net 20.000 (sub 6 sm = 24.300).
Calea aplicației: `rip_api.fisa_d212` (ce cheamă butonul «Fișa D212»). Tranzacție ANULATĂ la final.
  · cod VECHI: CASS 0 („neobligatoriu”), impozit pe 20.000 -> 2.000;
  · cod NOU: CASS 2.430 (baza minimă, CF art.174 alin.(6)), din care 430 diferență nedeductibilă; impozit pe 18.000 -> 1.800.
"""
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, rip_api, d212_engine  # noqa: E402

observare.alerteaza = lambda *a, **k: None
print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d212_engine, "EXCEPTII_MINIM_CASS") else "VECHI"))
S = "tenant_052"
db.init_pool()
with db.get_conn() as conn:
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("SELECT COUNT(*) FROM rip_operatiuni WHERE EXTRACT(YEAR FROM data_operatiune)=2025")
        print("  operațiuni RIP existente în 2025: %s" % cur.fetchone()[0])
        for data, tip, cat, suma in (("2025-05-10", "incasare", "activitate", 30000),
                                     ("2025-06-10", "plata", "cheltuiala_deductibila", 10000)):
            cur.execute("INSERT INTO rip_operatiuni (data_operatiune, tip, explicatie, suma, metoda, categorie, status) "
                        "VALUES (%s,%s,'proba CASS minim',%s,'banca',%s,'validata')", (data, tip, suma, cat))
        f = rip_api.fisa_d212(conn, S, 2025)
        cass = f["cass"]
        print("  venit net %s · CAS %s · CASS %s (baza %s, obligatoriu=%s)%s"
              % (f["venit_net"], f["cas"]["cas"], cass["cass"], cass["baza"], cass["obligatoriu"],
                 (" · din care diferență până la 6 sm %s, pe venit %s" % (cass["diferenta_minim"], cass["cass_pe_venit"]))
                 if "diferenta_minim" in cass else ""))
        print("  baza impozit %s · impozit %s · total datorat %s" % (f["baza_impozit"], f["impozit"], f["total_datorat"]))
    finally:
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
