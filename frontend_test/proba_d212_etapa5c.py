# -*- coding: utf-8 -*-
"""PROBA D212 Etapa 5c pe F4 (tenant_052): veniturile din străinătate (Secțiunea 2, cap14) — credit fiscal, metoda scutirii.

    python frontend_test/proba_d212_etapa5c.py <radacina_cod>
Calea aplicației: `declaratii_api.genereaza(conn, schema, "d212", body)` cu ce trimite ecranul — lista „Venituri din
străinătate” (activitate independentă în Germania cu credit fiscal, drepturi de autor din Austria cu credit plafonat, chirie
în Franța pe metoda scutirii, dividende din SUA). Doar CITIRE + ROLLBACK. Anul 2025.
  · codul VECHI: lista nu are unde intra — declarația iese DOAR de identificare, fără cap14, fără impozit, fără CAS/CASS
    (DUK valid: secțiunile sunt opționale);
  · codul NOU: o secțiune cap14 pe țară și sursă, creditul plafonat la impozitul român, CAS/CASS și sumarul, DUK valid.
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
    {"tara": "DE", "categ_venit": "2027", "dubla_impunere": "1", "venit_brut": "80000", "chelt_deduc": "20000", "impozit_platit": "4000"},
    {"tara": "AT", "categ_venit": "2003", "dubla_impunere": "1", "venit_brut": "20000", "impozit_platit": "2000"},
    {"tara": "FR", "categ_venit": "2004", "dubla_impunere": "2", "venit_brut": "30000", "impozit_platit": "5000"},
    {"tara": "US", "categ_venit": "2018", "dubla_impunere": "1", "venit_brut": "10000", "impozit_platit": "1500"},
]


def main():
    _db.init_pool()
    print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d212, "cap14_sectiune") else "VECHI"))
    body = {"tenant_id": 52, "an": AN, "manual": dict(ID, strainatate=STRAINATATE)}
    with _db.get_conn(SCH) as c:
        try:
            rez = da.genereaza(c, SCH, "d212", body)
            xml = rez[0] if isinstance(rez, tuple) else rez["xml"]
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
        print("  CAS: total %s datorat %s · CASS 2.1: total %s datorată %s · CASS 2.2: total %s datorată %s"
              % (a.get("cas_total_ven"), a.get("cas_datorat"), a.get("cass_total_ven_ai"), a.get("cass_datorat_ai"),
                 a.get("cass_total_ven"), a.get("cass_datorat")))
        print("  Sumar: impozit %s · CAS %s · CASS %s · DE PLATĂ %s"
              % (a.get("oblimpoz_real_total"), a.get("cas_plus"), a.get("cass_plus"), a.get("dif_de_plata")))
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=180)
    print("  DUK:", v.get("stare"), "|", (v.get("erori") or "(fara erori)").replace("\n", " ")[:200])
    print("=== ROLLBACK (nimic scris)")


if __name__ == "__main__":
    main()
