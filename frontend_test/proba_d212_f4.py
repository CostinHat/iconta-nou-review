# -*- coding: utf-8 -*-
"""Task 2 - proba D212 (increment) pe F4 (tenant_052): calea completa a UI.
1) manual gol -> valideaza_cerere refuza (mesaj de contabil).
2) manual identitate -> genereaza -> DUK valid (cazul minim: identificare).
3) fisa RIP: rip_api.fisa_d212(2025) intoarce venit net / CAS / CASS / impozit (afisat informativ in UI).
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d212_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d212, rip_api  # noqa: E402
from core.common import Perioada  # noqa: E402

SCH = "tenant_052"
AN = 2025
CNP = "1800101221144"  # checksum valid (reper DUK)
ID = {"cif": CNP, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d212", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) identitate -> genereaza -> DUK ===")
    xml, res = d212.genereaza(None, None, Perioada(an=AN), dict(ID))
    print("  totalPlata_A:", res.total_plata_a)
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
    assert v.get("stare") in ("valid", "gri"), "DUK a respins identitatea: %s" % v.get("erori")

    print("=== 3) fisa RIP pe tenant_052 (informativ, afisat in UI) ===")
    with _db.get_conn() as c:
        f = rip_api.fisa_d212(c, SCH, AN)
        c.rollback()
    if f.get("eroare"):
        print("  fisa eroare:", f["eroare"])
    else:
        print("  venit_net:", f.get("venit_net"),
              "| CAS:", (f.get("cas") or {}).get("cas"),
              "| CASS:", (f.get("cass") or {}).get("cass"),
              "| impozit:", f.get("impozit"))
    print("=== PROBA D212 OK ===")


if __name__ == "__main__":
    main()
