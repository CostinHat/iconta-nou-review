# -*- coding: utf-8 -*-
"""Task 2 - proba D221 pe F4 (tenant_052): valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere refuza (blocul nou).
2) contribuabil individual + o activitate agricola cu produse -> genereaza (conn tenant) -> DUK valid.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d221_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import db as _dbm  # noqa: E402
from core import declaratii_api as da, duk, d221  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025
M = {
    "nume_declar": "POPESCU", "prenume_declar": "ION", "functie_declar": "TITULAR",
    "cif": "1850715400015", "nume_a": "Popescu Ion", "adresa_a": "Comuna Test, jud. Cluj",
    "forma_org": "1", "d_rec": 0,
    "activitati": [{"judet": "12", "localitate": "Comuna Test", "optiune": "0",
                    "produse": [{"codp": "101", "prod1": 12.5}, {"codp": "201", "prod1": 8}]}],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d221", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) individual + o activitate agricola + produse -> genereaza -> DUK ===")
    with _dbm.get_conn("tenant_052") as conn:
        xml, res = d221.genereaza(conn, "tenant_052", Perioada(AN, luna=12), M)
        print("  nr_activitati:", res.nr_activitati, "| nr_asociati:", res.nr_asociati)
        v = duk.valideaza(xml, "d221", an=AN, luna=12)
        print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
        assert v.get("stare") in ("valid", "gri"), "DUK a respins D221: %s" % v.get("erori")
    print("=== PROBA D221 OK ===")


if __name__ == "__main__":
    main()
