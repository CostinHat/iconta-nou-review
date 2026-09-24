# -*- coding: utf-8 -*-
"""Task 2 - proba D204 pe F4 (tenant_052), calea completa a UI: valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere refuza (blocul nou).
2) o activitate cu 2 asociati (Σ cota=100, Σ venit=net3) -> genereaza -> DUK valid.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d204_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d204  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025


def _cnp(b):
    w = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
    c = sum(int(b[i]) * w[i] for i in range(12)) % 11
    return b + str(1 if c == 10 else c)


M = {
    "asociere": {"den": "ASOCIEREA EXEMPLU", "cif": "100204", "adresa": "Str. Test 1, Cluj-Napoca"},
    "reprezentant": {"nume": "POPESCU ION", "cif": _cnp("180010122114"), "adresa": "Str. Test 2, Cluj-Napoca"},
    "activitate": {"categ_venit": 1, "det_ven_net": 1, "caen": "6201", "forma_org": 1, "judet": "12",
                   "sediu": "Str. Test 1, Cluj-Napoca", "nr_contr": "1", "data_contr": "01.01.2020",
                   "venit3": 10000, "chelt3": 4000},
    "asociati": [{"cif": _cnp("196022915094"), "nume": "POPESCU ION", "cota": 60, "venit": 3600, "pierd": 0},
                 {"cif": _cnp("290030112233"), "nume": "IONESCU ANA", "cota": 40, "venit": 2400, "pierd": 0}],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d204", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) o activitate + 2 asociati -> genereaza -> DUK ===")
    xml, res = d204.genereaza(None, None, Perioada(AN, luna=12), M)
    print("  nr_activitati:", res.nr_activitati, "| nr_asociati:", res.nr_asociati)
    v = duk.valideaza(xml, "d204", an=AN, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D204: %s" % v.get("erori")
    print("=== PROBA D204 OK ===")


if __name__ == "__main__":
    main()
