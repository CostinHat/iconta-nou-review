# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D114 pe F4 (tenant_052): valideaza_cerere -> genereaza -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d114_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d114  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2026
LUNA = 6
M = {"cif_declarant": "12345674", "den_declarant": "SC TEST SRL", "adresa_declarant": "Bucuresti, Str. A nr.1",
     "functia_intocmit": "Contabil", "den_intocmit": "Ionescu Ana", "d_rec": "0",
     "contracte": [{"cui_lucrator": "1800101410013", "den_lucrator": "Popescu Ion", "nui_lucrator": "1",
                    "nr_contract": "10", "data_contract": "01.01.2026",
                    "venit_lucrator": 10000, "contributie_lucrator": 100}]}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d114", {"tenant_id": 1, "an": AN, "luna": LUNA})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) declarant + un contract -> genereaza -> DUK ===")
    xml, res = d114.genereaza(None, None, Perioada(AN, luna=LUNA), M)
    print("  total_venit:", res.total_venit, "| suma_datorata:", res.suma_datorata, "| Nr_evid:", res.nr_evid)
    v = duk.valideaza(xml, "d114", an=AN, luna=LUNA)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D114: %s" % v.get("erori")
    print("=== PROBA D114 OK ===")


if __name__ == "__main__":
    main()
