# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D603 pe F4 (tenant_052): valideaza_cerere -> genereaza -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d603_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d603  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2026
M = {"numeContrib": "POPESCU ION", "cif": "1800101221144", "taraContrib": "RO", "judetContrib": "CJ",
     "exceptare": 2, "statAsigurare": "DE",
     "dataInceput": "2026-01-01", "dataSfarsit": "2026-12-31", "dataExceptare": "2026-01-15",
     "documente": "Formular A1 emis de autoritatea competenta din Germania"}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d603", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) identitate + exceptare + stat + perioada -> genereaza -> DUK ===")
    xml, res = d603.genereaza(None, None, Perioada(AN, luna=12), M)
    print("  stat:", res.stat_asigurare, "| totalPlata_A:", res.total_plata_a)
    v = duk.valideaza(xml, "d603", an=AN, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D603: %s" % v.get("erori")
    print("=== PROBA D603 OK ===")


if __name__ == "__main__":
    main()
