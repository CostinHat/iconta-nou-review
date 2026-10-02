# -*- coding: utf-8 -*-
"""PROBA D212 Etapa 5 pe F4 (tenant_052): veniturile fără date în aplicație (Subsecțiunea I.1.1 pe categorii) și CASS 2.2.

    python frontend_test/proba_d212_etapa5.py <radacina_cod>
Calea aplicației: `declaratii_api.genereaza(conn, schema, "d212", body)` cu ce trimite ecranul — lista „Alte venituri”
(drepturi de autor pe cote forfetare, o chirie, activitate agricolă în sistem real, câștig din investiții, alte surse) și
dividendele nete pentru treapta CASS. Doar CITIRE + ROLLBACK. Anul 2025 (regulile pe categorii sunt ale veniturilor 2025).
  · codul VECHI: lista nu are unde intra — declarația iese DOAR de identificare, fără venituri, fără impozit, fără CASS
    (DUK valid: secțiunile sunt opționale, deci validatorul nu poate vedea lipsa);
  · codul NOU: o secțiune I.1.1 pe sursă, impozitul pe fiecare, CASS 2.2 pe treaptă, sumarul de plată, DUK valid.
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
SCH, AN = "tenant_052", 2025
ID = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
VENITURI = [
    {"categ_venit": "1003", "det_ven_net": "2", "venit_brut": "30000"},
    {"categ_venit": "1015", "venit_brut": "24000", "sediu": "Bucuresti, Str. Lunga 3", "nr_doc": "123", "data_doc": "2024-12-20"},
    {"categ_venit": "1009", "venit_brut": "50000", "chelt_deduc": "30000", "pierdere_precedenta": "5000", "sediu": "Comuna Afumati"},
    {"categ_venit": "1012", "castig_net": "8000", "pierdere_precedenta": "10000"},
    {"categ_venit": "1024", "venit_impozabil": "3000"},
]


def main():
    _db.init_pool()
    print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d212, "cap11_categorie") else "VECHI"))
    body = {"tenant_id": 52, "an": AN, "manual": dict(ID, venituri=VENITURI, alte_cass={"dividende_dobanzi": 10000})}
    with _db.get_conn(SCH) as c:
        try:
            rez = da.genereaza(c, SCH, "d212", body)
            xml = rez[0] if isinstance(rez, tuple) else rez["xml"]
        finally:
            c.rollback()
    rad = ET.fromstring(xml.split("?>", 1)[1])
    print("  capitole: %s · bifa111=%s bifa132=%s" % ([e.tag.split("}")[1] for e in rad], rad.get("bifa111"), rad.get("bifa132")))
    for s in rad.iter("{%s}cap11" % d212.NS):
        a = s.attrib
        print("   I.1.1 categ %s: brut %s chelt %s net %s comp %s rd.7 %s impozit %s"
              % (a.get("categ_venit"), a.get("venit_brut"), a.get("chelt_deduc"), a.get("venit_net_anual"),
                 a.get("pierdere_compensata"), a.get("venit_recalculat"), a.get("impozit11")))
    o = rad.find("{%s}oblig_realizat" % d212.NS)
    if o is None:
        print("  oblig_realizat: LIPSĂ — nici impozitul, nici CASS nu sunt în declarație")
    else:
        a = o.attrib
        print("  CASS 2.2: dpi %s cfb %s inv %s asp %s alt %s · total %s · treapta %s · baza %s · datorată %s"
              % (a.get("cass_ven_dpi"), a.get("cass_ven_cfb"), a.get("cass_ven_inv"), a.get("cass_ven_asp"),
                 a.get("cass_ven_alt"), a.get("cass_total_ven"), a.get("bifa_cass_real"), a.get("cass_baza"), a.get("cass_datorat")))
        print("  Sumar: impozit %s · CAS %s · CASS %s · DE PLATĂ %s"
              % (a.get("oblimpoz_real_total"), a.get("cas_plus"), a.get("cass_plus"), a.get("dif_de_plata")))
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v.get("stare"), "|", (v.get("erori") or "(fara erori)").replace("\n", " ")[:200])
    print("=== ROLLBACK (nimic scris)")


if __name__ == "__main__":
    main()
