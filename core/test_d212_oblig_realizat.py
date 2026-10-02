# -*- coding: utf-8 -*-
"""D212 Etapa 4 — CAS, CASS, impozitul în sistem real și sumarul (oblig_realizat), din venitul declarat (02.10.2026).

Rândurile urmează instrucțiunile D212 (OPANAF 2736/2025) Secțiunile 3, 4 și 7; corespondența atribut -> rând e cea din
D212Pdf.jar Pdf_v8 (formularul validatorului J13.0.1). CAS/CASS vin din `d212_engine` (aceeași sursă ca fișa RIP):
CF art.148 (CAS pe trepte 12/24 sm), art.170 alin.(1) + art.174 alin.(6) (CASS pe venit, baza minimă 6 sm), art.118
alin.(2) lit.b) + alin.(2^2) (CAS/CASS deductibile pe pondere, fără diferența de la art.174 alin.(6)), art.64 alin.(1)
(impozit 10%). Aserțiuni pe valori, pe arborele XML și pe verdictul DUK.
"""
import xml.etree.ElementTree as ET

import pytest

from core import d212, d212_engine
from core.common import Perioada

NSX = "{%s}" % d212.NS
ID = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}


def _gen(**m):
    xml, r = d212.genereaza(None, None, Perioada(an=2025), dict(ID, **m))
    rad = ET.fromstring(xml.split("?>", 1)[1])
    o = rad.find(NSX + "oblig_realizat")
    return xml, rad, dict(o.attrib) if o is not None else None


def test_sistem_real_sub_6_sm_aceleasi_cifre_ca_fisa_rip():
    # venit net 20.000 (2025): CAS nu (sub 12 sm, art.148); CASS 2.430 la baza minimă (art.174 alin.(6)); deductibilă doar
    # CASS pe venit 2.000 (art.118 alin.(2) lit.b), I.4.2 rd.5); impozit 10% x 18.000 = 1.800
    _x, rad, o = _gen(cap11=d212.cap11_sistem_real(30000, 10000))
    assert "cas_datorat" not in o and rad.get("bifa131") == "0" and rad.get("bifa132") == "1" and rad.get("bifa14") == "1"
    assert (o["cass_total_ven_ai"], o["baza_cass_datorat_ai"], o["cass_datorat_ai"], o["real_cass_calculata_ai"],
            o["real_cass_deductibila_ai"], o["real_venit_net_impozabil_ai"], o["real_impozit_datorat_ai"]) == \
        ("20000", "24300", "2430", "2000", "2000", "18000", "1800")
    assert (o["oblimpoz_real_total"], o["cass_plus"], o["dif_de_plata"]) == ("1800", "2430", "4230")
    # aceeași sursă ca fișa afișată pe ecran (d212_engine.calculeaza_d212)
    f = d212_engine.calculeaza_d212(30000, 10000, d212_engine.plafoane_an(2025))
    assert (int(f["cass"]["cass"]), int(f["impozit"])) == (2430, 1800)


def test_real_si_norma_ponderea_imparte_contributiile_deductibile():
    # net real 70.000 + normă 30.000 = 100.000 (>= 24 sm): CAS baza 97.200 -> 24.300, căsuța A2; CASS 10.000
    # CF art.118 alin.(2^2): CAS deductibilă = pondere 0,7 x 24.300 = 17.010; CASS deductibilă 0,7 x 10.000 = 7.000
    # impozit sistem real 10% x (70.000 - 17.010 - 7.000) = 4.599; + normă 3.000 -> 7.599
    # MUTAȚIE: fără pondere (deducere integrală) -> 3.130 / impozit 3.270 -> pică
    _x, rad, o = _gen(cap11=d212.cap11_sistem_real(100000, 30000), norma=[{"norma": 30000}])
    assert (o["bifa_cas_real"], o["cas_total_ven"], o["cas_baza"], o["cas_datorat"]) == ("2", "100000", "97200", "24300")
    assert (o["real_cas_pondere_ai"], o["real_cas_deductibila_ai"], o["real_cass_deductibila_ai"]) == ("0.7000", "17010", "7000")
    assert (o["real_venit_net_impozabil_ai"], o["real_impozit_datorat_ai"], o["oblimpoz_real_total"]) == ("45990", "4599", "7599")
    assert o["dif_de_plata"] == str(7599 + 24300 + 10000) and rad.get("bifa131") == "1"


def test_doar_norma_fara_sectiunea_4():
    # normă 30.000: CAS nu (sub 12 sm); CASS pe venit 3.000 (>= 6 sm); fără sistem real -> fără Secțiunea 4
    _x, rad, o = _gen(norma=[{"norma": 30000}])
    assert "real_impozit_datorat_ai" not in o and rad.get("bifa14") == "0"
    assert (o["cass_datorat_ai"], o["oblimpoz_real_total"], o["dif_de_plata"]) == ("3000", "3000", "6000")


def test_exceptia_de_la_baza_minima_scade_cass_la_venit():
    # CF art.174 alin.(7) lit.a): salarii de cel puțin 6 sm -> doar CASS pe venit (2.000)
    _x, _r, o = _gen(cap11=d212.cap11_sistem_real(30000, 10000), exceptie_minim_cass="salarii")
    assert (o["baza_cass_datorat_ai"], o["cass_datorat_ai"]) == ("20000", "2000") and "real_cass_calculata_ai" not in o


def test_pierderea_nu_aduce_contributii_si_nici_impozit():
    # instrucțiuni pct.48 lit.c: pierdere -> CASS nu se datorează; venit net zero -> fără Secțiunea 4
    _x, rad, o = _gen(cap11=d212.cap11_sistem_real(10000, 30000))
    assert (o["cass_plus"], o["oblimpoz_real_total"], o["dif_de_plata"]) == ("0", "0", "0") and rad.get("bifa132") == "0"


def test_optiunea_cas_sub_12_sm_refuzata_fara_casuta():
    # formularul validatorului (Pdf_v8) are doar A1/A2; opțiunea lit.B nu are unde fi declarată fără a minți
    with pytest.raises(ValueError):
        _gen(cap11=d212.cap11_sistem_real(30000, 10000), optiune_cas=1)


def test_anul_neverificat_refuzat():
    with pytest.raises(ValueError):
        d212.genereaza(None, None, Perioada(an=2027), dict(ID, cap11=d212.cap11_sistem_real(30000, 10000)))


def test_cheile_exceptiilor_din_ecran_sunt_ale_motorului():
    import os
    import re
    js = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "static", "js", "ecrane", "declaratii.js"), encoding="utf-8").read()
    bloc = js[js.index("const _D212_EXCEPTII_CASS"):js.index("];", js.index("const _D212_EXCEPTII_CASS"))]
    assert set(re.findall(r'\["(\w*)",', bloc)) - {""} == set(d212_engine.EXCEPTII_MINIM_CASS)


def _duk():
    try:
        from core import duk
        return duk if duk.poate_valida("d212") else None
    except Exception:
        return None


@pytest.mark.parametrize("caz", ["real_sub_minim", "real_si_norma", "doar_norma", "pierdere"])
def test_DUK_valid(caz):
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    m = {"real_sub_minim": {"cap11": d212.cap11_sistem_real(30000, 10000)},
         "real_si_norma": {"cap11": d212.cap11_sistem_real(100000, 30000), "norma": [{"norma": 30000}]},
         "doar_norma": {"norma": [{"norma": 30000}]},
         "pierdere": {"cap11": d212.cap11_sistem_real(10000, 30000)}}[caz]
    xml, _r, _o = _gen(**m)
    v = duk.valideaza(xml, "d212", an=2025, luna=12, timeout=120)
    assert v.get("stare") == "valid", v.get("erori")
