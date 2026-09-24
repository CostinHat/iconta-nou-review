# -*- coding: utf-8 -*-
"""Task 2 - proba D216 pe F4 (tenant_052), calea completa a UI: valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere refuza (blocul nou).
2) antet + 1 imobil + 1 mobil -> genereaza -> DUK valid (conn=None, pull={}).
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d216_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d216  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025
M = {
    "nume": "POPESCU ION", "cif": "1960101410019", "domiciliuFiscal": "JUD BOTOSANI MUN BOTOSANI",
    "nume_intocmit": "IONESCU MARIA", "functia_intocmit": "CONTABIL", "d_rec": 0,
    "imobile": [{"judet_imobil": "BOTOSANI", "cod_judet_imobil": "7", "localitate_imobil": "BOTOSANI",
                 "cod_localitate_imobil": "1", "strada_imobil": "STR PRIMAVERII", "cod_strada_imobil": "1",
                 "nr_cadastral": "12345", "valoare_impozabila_imobil": 3000000, "cota": 0.3, "plafon_imobil": 2500000}],
    "mobile": [{"an_detinere": 2023, "niv": 5, "valoare_impozabila_mobil": 400000, "plafon_mobil": 375000}],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d216", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) antet + imobil + mobil -> genereaza -> DUK ===")
    xml, res = d216.genereaza(None, None, Perioada(AN, luna=12), M)
    print("  impozit_imobile:", res.impozit_imobile, "| impozit_mobile:", res.impozit_mobile)
    v = duk.valideaza(xml, "d216", an=AN, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D216: %s" % v.get("erori")
    print("=== PROBA D216 OK ===")


if __name__ == "__main__":
    main()
