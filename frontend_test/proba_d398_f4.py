# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D398 pe F4 (tenant_052): valideaza_cerere -> genereaza -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d398_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d398  # noqa: E402
from core.common import Perioada  # noqa: E402

M = {"moes_voes_imp": 1, "e_int": 0, "name": "SC TEST SRL", "vat_id_no": "RO40410000",
     "an_r": 2026, "luna_r": 3, "period_start_date": "01.01.2026", "period_end_date": "31.03.2026",
     "d_rec": 0, "currency": "EUR",
     "ms": [{"mscon_state": "DE", "supplies": [
         {"supply_type": 1, "trade_type": 1, "vat_rate_type": 1, "vat_rate": 19, "taxable_amount": 1000}]}]}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d398", {"tenant_id": 1, "an": 2026, "trim": 1})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) regim UE + un stat + un supply -> genereaza -> DUK ===")
    xml, res = d398.genereaza(None, None, Perioada(2026, luna=3), M)
    print("  grand_total_vat_due:", res.grand_total_vat_due, "| nr_state:", res.nr_state)
    v = duk.valideaza(xml, "d398", an=2026, luna=3)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D398: %s" % v.get("erori")
    print("=== PROBA D398 OK ===")


if __name__ == "__main__":
    main()
