# -*- coding: utf-8 -*-
"""Task 2 - proba D223 pe F4 (tenant_052), calea completa a UI: valideaza_cerere -> genereaza -> DUK.
1) manual gol -> valideaza_cerere refuza (blocul nou).
2) asociere + responsabil + activitate + 2 asociati -> genereaza (pe conn tenant) -> DUK valid.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d223_f4.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import db as _dbm  # noqa: E402
from core import declaratii_api as da, duk, d223  # noqa: E402
from core.common import Perioada  # noqa: E402

AN = 2025


def _cnp(b):
    w = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
    c = sum(int(b[i]) * w[i] for i in range(12)) % 11
    return b + str(1 if c == 10 else c)


M = {
    "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "Responsabil asociere",
    "asociere": {"nume": "ASOCIEREA EXEMPLU", "cif": "100204", "adresa": "Cluj-Napoca, Str. A nr.1"},
    "responsabil": {"den_r": "POPESCU ION", "cif_r": _cnp("180010122114"), "adresa_r": "Cluj-Napoca, Str. A nr.1"},
    "d_rec1": 0, "d_rec": 0,
    "activitate": {"categ_venit": "1", "forma_org": "2", "det_venit": "1", "caen": "4711", "judet": "12",
                   "localitate": "Cluj-Napoca", "sediu": "Cluj-Napoca, Str. A nr.1", "nr_contr": "1",
                   "data_contr": "01.01.2020", "venit_brut": 10000, "cheltuieli": 4000},
    "asociati": [{"nume_d": "POPESCU ION", "cif_d": _cnp("196022915094"), "cota_d": 60},
                 {"nume_d": "IONESCU ANA", "cif_d": _cnp("290030112233"), "cota_d": 40}],
}


def main():
    _db.init_pool()
    print("=== 1) manual GOL -> valideaza_cerere trebuie sa refuze ===")
    er = da.valideaza_cerere("d223", {"tenant_id": 1, "an": AN})
    print("  erori:", er)
    assert er, "apelul gol trebuia refuzat"

    print("=== 2) asociere + responsabil + activitate + 2 asociati -> genereaza -> DUK ===")
    with _dbm.get_conn("tenant_052") as conn:
        xml, res = d223.genereaza(conn, "tenant_052", Perioada(AN, luna=12), M)
        print("  nr_asociati:", res.nr_asociati, "| totalPlata_A:", res.total_plata_a)
        v = duk.valideaza(xml, "d223", an=AN, luna=12)
        print("  DUK stare:", v.get("stare"), "| erori:", (v.get("erori") or "")[:200])
        assert v.get("stare") in ("valid", "gri"), "DUK a respins D223: %s" % v.get("erori")
    print("=== PROBA D223 OK ===")


if __name__ == "__main__":
    main()
