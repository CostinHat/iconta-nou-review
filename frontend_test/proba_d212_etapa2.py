# -*- coding: utf-8 -*-
"""PROBA D212 Etapa 2 pe F4 (tenant_052): venitul din registrul RIP intră în subsecțiunea I.1.1, cap-coadă.

Calea aplicației, nu a funcției: `declaratii_api.genereaza(conn, schema, "d212", body)` — exact ce cheamă
ecranul cu bifa „Include venitul din registrul RIP". Doar CITIRE + ROLLBACK.

  1) INVALID (forma de dinainte): cap11 cu categoria „1" (codul ghicit de prima probă R&D) -> DUK respinge
     („categ_venit: valoarea '1' nu se afla in lista").
  2) VALID: body.manual.din_rip -> cap11 din fișa RIP (venit brut / cheltuieli / venit net / pierdere) ->
     XML -> DUK valid; cifrele din XML == fișa RIP afișată pe ecran.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=. ./venv/bin/python frontend_test/proba_d212_etapa2.py
"""
import os
import sys
import xml.etree.ElementTree as ET

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d212, rip_api  # noqa: E402
from core.common import Perioada  # noqa: E402

SCH = "tenant_052"
AN = 2026   # F4 are operatiuni RIP validate doar in 2026 (masurat 02.10.2026); 2026 e in ANI_VERIFICATI
CNP = "1800101221144"  # cifra de control verificata; suma cifrelor = 25
ID = {"cif": CNP, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}


def main():
    _db.init_pool()
    print("=== 1) INVALID: cap11 cu categoria '1' (forma R&D) ===")
    xml0 = d212.build_xml({}, AN, None, dict(ID, bifa111="1", cap11={"categ_venit": 1, "venit_brut": 100}))
    v0 = duk.valideaza(xml0, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v0.get("stare"), "|", (v0.get("erori") or "").replace("\n", " ")[:160])
    assert v0.get("stare") != "valid"

    print("=== 2) VALID: calea aplicatiei cu din_rip ===")
    with _db.get_conn(SCH) as c:   # pozitionat pe schema, ca ruta (uc_declaratii)
        try:
            f = rip_api.fisa_d212(c, SCH, AN)
            print("  fisa RIP:", {k: f.get(k) for k in ("venit_brut", "cheltuieli_deductibile", "venit_net",
                                                       "ciorne_nevalidate", "cheltuieli_limitate_de_analizat")})
            body = {"tenant_id": 52, "an": AN, "manual": dict(ID, din_rip=True, pierdere_precedenta=0)}
            assert not da.valideaza_cerere("d212", body)
            rez = da.genereaza(c, SCH, "d212", body)
            xml, res = rez if isinstance(rez, tuple) else (rez["xml"], rez)
        finally:
            c.rollback()
    rad = ET.fromstring(xml.split("?>", 1)[1])
    cap = rad.find("{%s}cap11" % d212.NS)
    print("  cap11:", dict(cap.attrib), "| bifa111:", rad.get("bifa111"), "| totalPlata_A:", rad.get("totalPlata_A"))
    print("  avertismente:", getattr(res, "avertismente", None))
    assert int(cap.get("venit_brut")) == round(f["venit_brut"]) and int(cap.get("chelt_deduc")) == round(f["cheltuieli_deductibile"])
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v.get("stare"), "|", (v.get("erori") or "(fara erori)").replace("\n", " ")[:200])
    assert v.get("stare") == "valid"
    print("=== PROBA D212 ETAPA 2 OK ===")


if __name__ == "__main__":
    main()
