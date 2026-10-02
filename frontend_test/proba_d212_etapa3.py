# -*- coding: utf-8 -*-
"""PROBA D212 Etapa 3 pe F4 (tenant_052): activitățile pe normă de venit intră în subsecțiunea I.1.2 (cap12).

Calea aplicației: `declaratii_api.genereaza(conn, schema, "d212", body)` — exact ce trimite ecranul cu lista
„Venit pe normă de venit". Aceleași date, două rădăcini de cod. Doar CITIRE + ROLLBACK.

    python frontend_test/proba_d212_etapa3.py <radacina_cod>
  · codul VECHI ignoră `manual.norma`: declarația iese fără cap12, bifa112=0 — venitul pe normă și impozitul
    lipsesc tăcut din declarație (DUK nu are cum să observe: cap12 e opțional);
  · codul NOU: o secțiune cap12 pe activitate, rd.9 proratat la 365 de zile, rd.9.1 cu zilele scutite, impozit 10%,
    bifa112=1, DUK valid.
Env: set -a; . ~/.iconta/db.env; set +a
"""
import os
import sys
import xml.etree.ElementTree as ET

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d212, observare  # noqa: E402

observare.alerteaza = lambda *a, **k: None
SCH = "tenant_052"
AN = 2026
CNP = "1800101221144"  # cifra de control verificată
ID = {"cif": CNP, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
NORMA = [{"norma": 30000, "caen": "9602", "sediu": "Bucuresti, Str. Lunga 1", "nr_doc_autoriz": "12345",
          "data_doc_autoriz": "2020-05-04"},
         {"norma": 27000, "norma_ajustata": 24000, "caen": "4520", "data_incep": "2026-07-01", "nr_zile_scutite": 20}]


def main():
    _db.init_pool()
    print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d212, "cap12_norma") else "VECHI"))
    body = {"tenant_id": 52, "an": AN, "manual": dict(ID, norma=NORMA)}
    print("  cerere refuzată de validarea rutei:", da.valideaza_cerere("d212", body) or "nu")
    with _db.get_conn(SCH) as c:
        try:
            rez = da.genereaza(c, SCH, "d212", body)
            xml = rez[0] if isinstance(rez, tuple) else rez["xml"]
        finally:
            c.rollback()
    rad = ET.fromstring(xml.split("?>", 1)[1])
    secs = rad.findall("{%s}cap12" % d212.NS)
    print("  bifa112=%s · secțiuni cap12: %d" % (rad.get("bifa112"), len(secs)))
    for i, s in enumerate(secs, 1):
        print("   activitatea %d: %s" % (i, {k: s.get(k) for k in ("norma_caen", "real_norma_venit", "real_ajustare",
                                                                      "norma_data_incep", "norma_nr_zile_scutite",
                                                                      "real_venit_net_anual", "real_venit_impozit",
                                                                      "real_impozit")}))
    impozit = sum(int(s.get("real_impozit") or 0) for s in secs)
    print("  impozit pe normă în declarație: %d lei (de declarat: 3000 + 10%% × 10784 = 4078)" % impozit)
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v.get("stare"), "|", (v.get("erori") or "(fara erori)").replace("\n", " ")[:200])
    print("  VERDICT:", "COMPLET" if (len(secs) == 2 and impozit == 4078 and v.get("stare") == "valid")
          else "INCOMPLET — venitul pe normă lipsește din declarație")
    print("=== ROLLBACK (nimic scris)")


if __name__ == "__main__":
    main()
