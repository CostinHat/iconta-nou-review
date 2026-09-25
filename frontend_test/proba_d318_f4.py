# -*- coding: utf-8 -*-
"""Task 2 front-7 - proba D318 pe F4: valideaza_cerere -> genereaza -> DUK.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d318_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d318  # noqa: E402
from core.common import Perioada  # noqa: E402

M = {
    "an": 2025, "luna_inceput": 1, "luna_sfarsit": 12, "annual": 1, "d_rec": 0,
    "cui": "40410000",
    "refunding_country": "DE", "language": "RO", "currency": "EUR",
    "iban": "DE89370400440532013000", "bic": "DEUTDEFF",
    "owner_name": "SC TEST SRL", "owner_type": "A",
    "declarant": "POPESCU ION", "functie": "administrator",
    "solicitant": {"denumire": "SC TEST SRL", "strada": "Str. Exemplu 1, Cluj-Napoca",
                   "email": "test@example.ro", "cod_postal": "400000"},
    "activitati": [{"activitate": "6201", "descriere": "Activitati de realizare software la comanda"}],
    "achizitii": [{
        "reference_number": "DE-2025-000123", "issuing_date": "15.06.2025",
        "taxable_amount": 1000, "vat_amount": 190, "deductible_vat": 190,
        "furnizor": {"denumire": "Muster GmbH", "strada": "Hauptstrasse 1, Berlin",
                     "tara": "DE", "vat_id": "DE123456789"},
        "bunuri": [{"code": "3"}],
    }],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d318", {"tenant_id": 1, "an": 2025})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) cerere valida -> valideaza_cerere lista goala ===")
    er2 = da.valideaza_cerere("d318", {"tenant_id": 1, "an": 2025, "manual": M})
    print("  erori:", er2)
    assert er2 == [], "cererea valida a fost respinsa: %s" % er2

    print("=== 3) genereaza -> DUK ===")
    xml, res = d318.genereaza(None, None, Perioada(2025, luna=12), M)
    print("  amount:", res.amount, "| nr_achizitii:", res.nr_achizitii, "| tara:", res.tara_rambursare)
    print(xml[:600])
    v = duk.valideaza(xml, "d318", an=2025, luna=12)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:400])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins D318: %s" % v.get("erori")
    print("=== PROBA D318 OK ===")


if __name__ == "__main__":
    main()
