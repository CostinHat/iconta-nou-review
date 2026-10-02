# -*- coding: utf-8 -*-
"""PROBA D212 Etapa 4 pe F4 (tenant_052): contribuțiile și impozitul (oblig_realizat) din venitul declarat.

    python frontend_test/proba_d212_etapa4.py <radacina_cod>
Calea aplicației: `declaratii_api.genereaza(conn, schema, "d212", body)` cu venitul din registrul RIP (din_rip) și o
activitate pe normă — ce trimite ecranul. Doar CITIRE + ROLLBACK. Anul 2026 (singurul an cu operațiuni RIP la F4).
  · codul VECHI: declarația are venitul (cap11 + cap12), dar NU are Secțiunile 3/4/7 — nici CAS, nici CASS, nici
    impozitul în sistem real, iar sumarul obligațiilor lipsește (DUK valid: secțiunile sunt opționale);
  · codul NOU: oblig_realizat cu CAS/CASS/impozit pe rânduri, sumarul de plată, DUK valid.
"""
import os
import sys
import xml.etree.ElementTree as ET

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

import core.db as _db  # noqa: E402
from core import declaratii_api as da, duk, d212, observare, rip_api  # noqa: E402

observare.alerteaza = lambda *a, **k: None
SCH, AN = "tenant_052", 2026
ID = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}


def main():
    _db.init_pool()
    print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d212, "oblig_realizat") else "VECHI"))
    body = {"tenant_id": 52, "an": AN, "manual": dict(ID, din_rip=True, pierdere_precedenta=0,
                                                     norma=[{"norma": 30000, "caen": "9602"}])}
    with _db.get_conn(SCH) as c:
        try:
            f = rip_api.fisa_d212(c, SCH, AN)
            print("  fișa RIP %d: venit net %s · CAS %s · CASS %s · impozit %s"
                  % (AN, f["venit_net"], f["cas"]["cas"], f["cass"]["cass"], f["impozit"]))
            rez = da.genereaza(c, SCH, "d212", body)
            xml = rez[0] if isinstance(rez, tuple) else rez["xml"]
        finally:
            c.rollback()
    rad = ET.fromstring(xml.split("?>", 1)[1])
    o = rad.find("{%s}oblig_realizat" % d212.NS)
    print("  capitole: %s · bifa131=%s bifa132=%s bifa14=%s" % ([e.tag.split("}")[1] for e in rad],
          rad.get("bifa131"), rad.get("bifa132"), rad.get("bifa14")))
    if o is None:
        print("  oblig_realizat: LIPSĂ — CAS, CASS și impozitul nu sunt în declarație")
    else:
        a = o.attrib
        print("  CAS: total %s baza %s datorat %s · CASS: total %s baza %s datorată %s"
              % (a.get("cas_total_ven"), a.get("cas_baza"), a.get("cas_datorat"), a.get("cass_total_ven_ai"),
                 a.get("baza_cass_datorat_ai"), a.get("cass_datorat_ai")))
        print("  Secț.4: recalculat %s · pondere CAS %s ded %s · CASS ded %s · impozabil %s · impozit %s"
              % (a.get("real_venit_net_recalculat_ai"), a.get("real_cas_pondere_ai"), a.get("real_cas_deductibila_ai"),
                 a.get("real_cass_deductibila_ai"), a.get("real_venit_net_impozabil_ai"), a.get("real_impozit_datorat_ai")))
        print("  Sumar: impozit %s · CAS %s · CASS %s · DE PLATĂ %s"
              % (a.get("oblimpoz_real_total"), a.get("cas_plus"), a.get("cass_plus"), a.get("dif_de_plata")))
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v.get("stare"), "|", (v.get("erori") or "(fara erori)").replace("\n", " ")[:200])
    print("=== ROLLBACK (nimic scris)")


if __name__ == "__main__":
    main()
