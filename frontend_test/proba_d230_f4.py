# -*- coding: utf-8 -*-
"""Task 2 - proba D230 pe F4 (tenant_052), calea completa a UI: valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere intoarce eroarea de contabil (blocul nou).
2) manual real (PF + entitate ONG) -> genereaza -> DUK valid.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d230_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d230  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025


def _cnp(body12):
    w = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(body12[i]) * w[i] for i in range(12)) % 11
    return body12 + str(1 if c == 10 else c)


ID = {"nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ANA MARIA", "cif_c": _cnp("196022915094"),
      "adresa_c": "Str Test 1 Bucuresti", "den_entitate": "Asociatia Binele", "cif_entitate": "12345678",
      "cont_entitate": "RO49AAAA1B31007593840000", "procent": 3.5, "valabilitate_distribuire": 2}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d230", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) PF + entitate ONG -> genereaza -> DUK ===")
    xml, res = d230.genereaza(None, None, Perioada(AN, luna=12), dict(ID))
    print("  beneficiar:", getattr(res, "beneficiar", "?"), "| totalPlata_A:", getattr(res, "total_plata_a", "?"))
    v = duk.valideaza(xml, "d230", an=AN, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D230: %s" % v.get("erori")
    print("=== PROBA D230 OK ===")


if __name__ == "__main__":
    main()
