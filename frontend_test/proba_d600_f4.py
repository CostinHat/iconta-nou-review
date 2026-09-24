# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D600 pe F4 (tenant_052): valideaza_cerere -> genereaza -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d600_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d600  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2026
M = {"nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ION", "cif_c": "1800101221144",
     "adresa_c": "Cluj-Napoca, Str. A nr.1", "cas_opt": 1}
for _i in range(1, 13):
    M["baza%d" % _i] = 4050


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d600", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) identitate + CAS (optiune + 12 baze) -> genereaza -> DUK ===")
    xml, res = d600.genereaza(None, None, Perioada(AN, luna=12), M)
    print("  contribuabil:", res.contribuabil, "| totalPlata_A:", res.total_plata_a)
    v = duk.valideaza(xml, "d600", an=AN, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D600: %s" % v.get("erori")
    print("=== PROBA D600 OK ===")


if __name__ == "__main__":
    main()
