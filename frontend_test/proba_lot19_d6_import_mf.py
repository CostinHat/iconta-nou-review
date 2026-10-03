# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 6: importul de mijloace fixe punea valoarea RĂMASĂ în `rezidual`.

    python frontend_test/proba_lot19_d6_import_mf.py <radacina_cod>
F1 (tenant_049) din baza de producție. Calea aplicației: `mijloace_fixe_import_api.extrage` (butonul «Încarcă») ->
`importa` (butonul «Salvează») -> `repo_mijloace_fixe.de_amortizat` + `d406_active.amortizare_luna` (exact bucla din
`uc_tenants.tenant_amortizare`, nota lunară), plus amortizarea la zi. Tranzacție ANULATĂ la final.
Fișierul: exportul tipic al unui program anterior — valoare de intrare + valoare rămasă; al doilea, fără coloana rămas.
  · cod VECHI: rezidual = rămasul (6.000) -> amortizare lunară 100 în loc de 200; fără coloană rezidual = valoarea -> 0;
  · cod NOU: rezidual 0, amortizare lunară 200 / 1.000 (OMFP 1802/2014 pct.139 alin.(2)).
"""
import datetime
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, mijloace_fixe_import_api as mfi, repo_mijloace_fixe, d406_active  # noqa: E402

observare.alerteaza = lambda *a, **k: None
print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(mfi, "_la_zi") else "VECHI"))
FISIERE = {
    "cu coloana rămas": b"cod;denumire;valoare intrare;valoare ramasa;durata luni;data PIF;metoda;cont imobilizare\n"
                        b"PRB-MF1;Strung CNC;12000;6000;60;2024-03-15;liniara;2131\n",
    "fără rămas / rezidual": b"cod;denumire;valoare;durata;pif;metoda;cont imobilizare\n"
                             b"PRB-MF3;Autoutilitara;60000;60;2025-01-10;liniara;2133\n",
}
S = "tenant_049"
db.init_pool()
with db.get_conn() as conn:
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("SELECT COUNT(*) FROM mijloace_fixe")
        print("  mijloace fixe existente în F1: %s" % cur.fetchone()[0])
        for nume, fisier in FISIERE.items():
            randuri = mfi.extrage(fisier, "export.csv")
            mfi.importa(conn, randuri)
            r = randuri[0]
            print("  [%s] extrage: valoare %s · rezidual %s · amortizat %s · avertismente %s"
                  % (nume, r["valoare"], r["rezidual"], r.get("amortizat"), r["avertismente"] or "—"))
            for mid, den, cont_am, val, rez, dnf, pif, cont_imob, met, reev in repo_mijloace_fixe.de_amortizat(cur, S):
                mf = {"cod": den, "denumire": den, "cont_imobilizare": cont_imob, "cont_amortizare": cont_am,
                      "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif, "metoda": met, "reevaluari": reev}
                z = d406_active.amortizat_la_data(mf, datetime.date(2026, 10, 31))
                print("      în bază: rezidual %s -> nota AMORT-2026-10: %s pe %s · amortizat la 31.10.2026: %s · rămas %s"
                      % (rez, d406_active.amortizare_luna(mf, 2026, 10), cont_am, z["amortizat"], z["ramas"]))
    finally:
        conn.rollback()
        print("  ROLLBACK — nimic scris")
