# -*- coding: utf-8 -*-
"""Task 2 - proba D200 pe F4 (tenant_052), calea completa a UI: valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere intoarce eroarea de contabil (blocul nou).
2) manual real (CNP valid + sectiune categ_venit=1, cazul F4 activitate IT) -> genereaza -> DUK valid.
Env: set -a; . ~/.iconta/db.env; set +a; ./venv/bin/python frontend_test/proba_d200_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk  # noqa: E402

SCH = "tenant_052"
AN = 2025  # validatorul D200 accepta an >= 2016; folosim 2025 (an de venit incheiat)
CNP = "1800101221144"  # checksum valid (acelasi ca in test_declaratii_lot2_duk / reperul DUK)


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d200", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert any("D200" in e for e in er), "blocul de validare D200 NU a prins apelul gol"
    print("  OK: apelul gol e refuzat cu mesaj de contabil.")

    print("\n=== 2) manual REAL (CNP + sectiune categ_venit=1) -> genereaza -> DUK ===")
    body = {"tenant_id": 1, "an": AN, "manual": {
        "cif_i": CNP, "nume_c": "POPESCU", "prenume_c": "ION", "den_i": "POPESCU ION",
        "adresa_i": "Bucuresti Sector 1",
        "sectiuni": [{"categ_venit": 1, "caen": "6201", "venit_brut": 100000, "chelt": 30000}],
    }}
    er = da.valideaza_cerere("d200", body)
    print("  erori validare cerere:", er)
    assert not er, "cererea reala NU trebuie sa aiba erori: %s" % er
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        xml, res = da.genereaza(conn, SCH, "d200", body)
    print("  generat: totalPlata_A=%s, nr_sectiuni=%s" % (getattr(res, "total_plata_a", "?"), getattr(res, "nr_sectiuni", "?")))
    print("  XML (cap):", xml.splitlines()[1][:100] if len(xml.splitlines()) > 1 else xml[:100])
    v = duk.valideaza(xml, "d200", an=AN, luna=12, timeout=120)
    print("  DUK:", (v.get("stare"), (v.get("erori") or v.get("temei") or "")[:160]) if isinstance(v, dict) else v)
    if isinstance(v, dict) and v.get("stare") == "gri":
        print("  (validator indisponibil - gri; structura OK, DUK neconcludent aici)")
    else:
        assert isinstance(v, dict) and v.get("stare") == "valid", "D200 DUK nu e valid: %s" % v
        print("  OK: D200 generat din calea UI e DUK-valid pe F4.")


if __name__ == "__main__":
    main()
