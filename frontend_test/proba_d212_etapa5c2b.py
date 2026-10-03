# -*- coding: utf-8 -*-
"""PROBA D212 Etapa 5c-2b pe F4 (tenant_052): pensii și remunerații de administrator din străinătate (+ CAS/CASS, Secțiunea 2.2).

    python frontend_test/proba_d212_etapa5c2b.py <radacina_cod>
Calea aplicației: `declaratii_api.genereaza(conn, schema, "d212", body)` cu ce trimite ecranul — o pensie din Germania
(12 luni, cu impozit plătit acolo), o remunerație de administrator din Austria (CAS/CASS în România) și una din Franța pentru
un asigurat acolo. Doar CITIRE + ROLLBACK. Anul 2025.
  · codul VECHI (5c-2a): categoriile astea nu sunt acceptate — refuz numit pe categorie;
  · codul NOU: secțiunile cap14, Secțiunea 2 Subsecțiunea a 2-a (CAS/CASS pe remunerație), sumarul, DUK valid.
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
STRAINATATE = [
    {"tara": "DE", "categ_venit": "2020", "venit_brut": "60000", "nr_luni": "12", "dubla_impunere": "1", "impozit_platit": "1000"},
    {"tara": "AT", "categ_venit": "2015", "venit_brut": "40000"},
    {"tara": "FR", "categ_venit": "2015", "venit_brut": "20000", "fara_contributii": True, "chelt_deduc": "4000"},
]


def main():
    _db.init_pool()
    print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d212, "PENSIE_NEIMPOZABIL_LUNAR") else "VECHI"))
    body = {"tenant_id": 52, "an": AN, "manual": dict(ID, strainatate=STRAINATATE)}
    with _db.get_conn(SCH) as c:
        try:
            rez = da.genereaza(c, SCH, "d212", body)
            xml = rez[0] if isinstance(rez, tuple) else rez["xml"]
        except ValueError as e:
            print("  REFUZ: %s" % str(e)[:300])
            print("=== ROLLBACK (nimic scris)")
            return
        finally:
            c.rollback()
    rad = ET.fromstring(xml.split("?>", 1)[1])
    print("  capitole: %s · bifa121=%s bifa132=%s" % ([e.tag.split("}")[1] for e in rad], rad.get("bifa121"), rad.get("bifa132")))
    for s in rad.iter("{%s}cap14" % d212.NS):
        a = s.attrib
        print("   I.2.1 %s categ %s metoda %s: net %s · impozit RO %s · plătit %s · credit %s · de plată %s"
              % (a.get("str_stat_realiz_v"), a.get("str_categ_venit"), a.get("dubla_impunere"), a.get("str_venit_net_anual"),
                 a.get("str_impozit_datorat_Ro"), a.get("str_impozit_platit"), a.get("str_credit_fiscal"), a.get("str_dif_impozit_datorat")))
    o = rad.find("{%s}oblig_realizat" % d212.NS)
    if o is None:
        print("  oblig_realizat: LIPSĂ — nici impozitul, nici CASS nu sunt în declarație")
    else:
        a = o.attrib
        print("  Secț.2.2: bază CAS %s · CAS %s · bază CASS %s · CASS %s"
              % (a.get("str_cas_baza"), a.get("str_cas_datorat"), a.get("str_cass_baza"), a.get("str_cass_datorat")))
        print("  Sumar: impozit %s · CAS %s · CASS %s · DE PLATĂ %s"
              % (a.get("oblimpoz_real_total"), a.get("cas_plus"), a.get("cass_plus"), a.get("dif_de_plata")))
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v.get("stare"), "|", (v.get("erori") or "(fara erori)").replace("\n", " ")[:200])
    print("=== ROLLBACK (nimic scris)")


if __name__ == "__main__":
    main()
