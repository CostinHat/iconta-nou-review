# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 8: D208 (notari) e lunară (CF art.113), nu semestrială.

    python frontend_test/proba_lot19_d8_d208_lunar.py <radacina_cod>
F1 (tenant_049) din baza de producție, calea aplicației: `declaratii_api.valideaza_cerere` + `declaratii_api.genereaza`
(ce cheamă ruta de generare), cu cererea EXACT cum o trimitea ecranul pentru o periodicitate ne-lunară (fără `luna`),
apoi cu luna aleasă (martie 2026); XML-ul trece prin validatorul DUK instalat. Tranzacție ANULATĂ.
  · cod VECHI: cererea fără lună e acceptată și D208 iese pe luna 12 (decembrie), oricare ar fi luna actelor;
  · cod NOU: cererea fără lună e refuzată cu motiv; cu luna 3 -> luna="3", DUK valid; termen 27.04.2026.
"""
import os
import re
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, declaratii_api, duk, scadente  # noqa: E402
from core.test_d208_formular import _m  # noqa: E402

observare.alerteaza = lambda *a, **k: None
print("=== COD: %s (%s)" % (RAD, "NOU" if declaratii_api.periodicitate("d208") == "lunar" else "VECHI"))
print("  periodicitate D208: %s" % declaratii_api.periodicitate("d208"))
S = "tenant_049"
db.init_pool()
with db.get_conn() as conn:
    try:
        conn.cursor().execute("SET search_path TO %s, public" % S)
        for body in ({"tenant_id": 105779, "an": 2026, "manual": _m(nr_act_notarial="311/2026")},
                     {"tenant_id": 105779, "an": 2026, "luna": 3, "manual": _m(nr_act_notarial="311/2026")}):
            er = declaratii_api.valideaza_cerere("d208", body)
            eticheta = "cerere %s" % ("FĂRĂ lună (cum o trimitea ecranul)" if "luna" not in body else "luna=3")
            if er:
                print("  [%s] refuzată: %s" % (eticheta, er))
                continue
            xml, res = declaratii_api.genereaza(conn, S, "d208", body)
            luna = re.search(r' luna="(\d+)"', xml).group(1)
            r = duk.valideaza(xml, "d208", an=2026, luna=int(luna))
            print("  [%s] acceptată -> XML luna=\"%s\" · DUK: %s · termen %s"
                  % (eticheta, luna, r["stare"], scadente.scadenta("d208", 2026, luna=int(luna))))
    finally:
        conn.rollback()
        print("  ROLLBACK — nimic scris")
