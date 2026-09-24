# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D104 pe F4 (tenant_052): valideaza_cerere -> genereaza (conn tenant) -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d104_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import db as _dbm  # noqa: E402
from core import declaratii_api as da, duk, d104  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025


def _cnp(b):
    w = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
    c = sum(int(b[i]) * w[i] for i in range(12)) % 11
    return b + str(1 if c == 10 else c)


M = {
    "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "Asociat desemnat",
    "asociere": {"cui": "100204", "den": "ASOCIEREA EXEMPLU", "adresa": "Cluj-Napoca, Str. A nr.1"},
    "profit_pierd": 6000, "d_rec": 0,
    "asociati": [{"den": "POPESCU ION", "cif": _cnp("196022915094"), "cota": 60, "venit": 6000, "chelt": 2000, "imp_datorat": 900},
                 {"den": "IONESCU ANA", "cif": _cnp("290030112233"), "cota": 40, "venit": 4000, "chelt": 1000, "imp_datorat": 600}],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d104", {"tenant_id": 1, "an": AN, "trim": 1})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) declarant + asociere + 2 asociati (trim I) -> genereaza -> DUK ===")
    with _dbm.get_conn("tenant_052") as conn:
        xml, res = d104.genereaza(conn, "tenant_052", Perioada(AN, trim=1), M)
        print("  nr_asociati:", res.nr_asociati, "| totalPlata_A:", res.total_plata_a)
        v = duk.valideaza(xml, "d104", an=AN, luna=3)
        print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
        assert v.get("stare") in ("valid", "gri"), "DUK a respins D104: %s" % v.get("erori")
    print("=== PROBA D104 OK ===")


if __name__ == "__main__":
    main()
