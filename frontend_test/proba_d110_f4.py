# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D110 pe F4 (tenant_052): valideaza_cerere -> genereaza (conn tenant) -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d110_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import db as _dbm  # noqa: E402
from core import declaratii_api as da, duk, d110  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2026
LUNA = 6
M = {"d_temei": 0, "d_rec": 0, "obligatii": [{"cod_oblig": "602", "suma_dat": 1000, "suma_rest": 800}]}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d110", {"tenant_id": 1, "an": AN, "luna": LUNA})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) o obligatie (identitate din firma_profil) -> genereaza -> DUK ===")
    with _dbm.get_conn("tenant_052") as conn:
        xml, res = d110.genereaza(conn, "tenant_052", Perioada(AN, luna=LUNA), M)
        print("  nr_obligatii:", res.nr_obligatii, "| totalPlata_A:", res.total_plata_a)
        v = duk.valideaza(xml, "d110", an=AN, luna=LUNA)
        print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
        assert v.get("stare") in ("valid", "gri"), "DUK a respins D110: %s" % v.get("erori")
    print("=== PROBA D110 OK ===")


if __name__ == "__main__":
    main()
