# -*- coding: utf-8 -*-
"""Task 2 - proba D208 pe F4 (tenant_052): valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere refuza (blocul nou).
2) antet notar + o tranzactie/imobil + beneficiari + parti (forma flat) -> DUK valid.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d208_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d208  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2026
M = {
    "nume": "BIROU INDIVIDUAL NOTARIAL POPESCU ION", "cif": "12345674",
    "domiciliu": "Bucuresti, Str. Exemplu nr. 1", "nume_intocmit": "POPESCU ION",
    "functia_intocmit": "Notar public", "dRec": "0",
    "nr_act_notarial": "1024/2026", "mod_transfer": "1", "taxa_notar": 1500,
    "imobile": [{"judet": "40", "localitate": "MUNICIPIUL BUCURESTI SECTOR 1", "codSIRUTA": "179141",
                 "tip_nr_cadastral": "1", "nr_cadastral": "200145", "tip_imobil": "teren",
                 "val_tranzactie_imobil": 300000, "val_piata_imobil": 300000,
                 "beneficiari": [{"cui": "1800101410013", "nume": "IONESCU MARIA", "cota": 100,
                                  "cotaImpozit": 3, "baza_calcul": 300000, "impozit": 9000, "impozit_scutit": 0}],
                 "parti": [{"cui": "1750202410022", "nume": "GEORGESCU VASILE", "cota": 100}]}],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d208", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) notar + tranzactie/imobil + beneficiari + parti -> genereaza -> DUK ===")
    xml, res = d208.genereaza(None, None, Perioada(AN, luna=12), M)
    print("  val_tranzactii_T:", res.val_tranzactii_T, "| impozit_T:", res.impozit_T, "| nr_beneficiari:", res.nr_beneficiari)
    v = duk.valideaza(xml, "d208", an=AN, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D208: %s" % v.get("erori")
    print("=== PROBA D208 OK ===")


if __name__ == "__main__":
    main()
