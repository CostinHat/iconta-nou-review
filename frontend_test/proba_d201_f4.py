# -*- coding: utf-8 -*-
"""Task 2 - proba D201 pe F4 (tenant_052), calea completa a UI: valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere intoarce eroarea de contabil (blocul nou).
2) manual real (identitate PF + sectiune categ=3 tara=276 Germania) -> genereaza -> DUK valid.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d201_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d201  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025
ID = {"nume_c": "ION", "initiala_c": "V", "prenume_c": "DAN", "cif_c": "1800101221144"}
SECT = {"categ_venit": 3, "statul": 276, "venit_B": 1000, "chlt_D": 0}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d201", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) identitate + sectiune -> genereaza -> DUK ===")
    xml, res = d201.genereaza(None, None, Perioada(AN, luna=12), dict(ID, sectiuni=[SECT]))
    print("  venit_net_total:", res.get("venit_net_total") if isinstance(res, dict) else getattr(res, "venit_net_total", "?"))
    v = duk.valideaza(xml, "d201", timeout=180)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D201: %s" % v.get("erori")
    print("=== PROBA D201 OK ===")


if __name__ == "__main__":
    main()
