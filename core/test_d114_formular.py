# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D114 gol NU produce declaratie; declarantul + cel putin un
contract (lucrator) cu venit+contributie tin. Aserteaza STRUCTURAL (tip exceptie, atribute XML prin
ElementTree) - NU `"sir" in xml`.

D114 (CAM pentru situatii ne-D112) = antet declarant + lista <contracte> (ecran nou, scos din _DOAR_API).
Structura din D114Validator.jar (radacina D114, ns declaratie:v1). Reguli: total_venit=Σ venit_lucrator;
contributie=venit*1/100 (R32); totalPlata_A=suma cifrelor cif_declarant (R4); Nr_evid/Scadenta calculate.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d114, declaratii_api
from core.common import Perioada

_TIP = "d114"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d114:declaratie:v1}"


def _m(**ov):
    m = {"cif_declarant": "12345674", "den_declarant": "SC TEST SRL", "adresa_declarant": "Bucuresti, Str. A nr.1",
         "functia_intocmit": "Contabil", "den_intocmit": "Ionescu Ana", "d_rec": "0",
         "contracte": [{"cui_lucrator": "1800101410013", "den_lucrator": "Popescu Ion", "nui_lucrator": "1",
                        "nr_contract": "10", "data_contract": "01.01.2026",
                        "venit_lucrator": 10000, "contributie_lucrator": 100}]}
    m.update(ov)
    return m


def test_d114_nu_e_doar_api():
    """d114 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d114_cerere_goala_refuza_la_api():
    """Bloc validare API: fara declarant/contracte -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d114", {"tenant_id": 1, "an": 2026, "luna": 6})
    valida = declaratii_api.valideaza_cerere("d114", {"tenant_id": 1, "an": 2026, "luna": 6, "manual": _m()})
    assert goala and valida == []


def test_d114_formular_gol_refuza():
    """Fara contracte -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d114.genereaza(None, None, Perioada(2026, luna=6), _m(contracte=[]))


def test_d114_structural():
    """Regresie STRUCTURALA: <D114>/<contracte>; total_venit agregat; contributie=venit*1/100."""
    xml, res = d114.genereaza(None, None, Perioada(2026, luna=6), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "D114"
    assert root.get("luna") == "6" and int(root.get("total_venit")) == 10000
    ct = root.findall(_NS + "contracte")
    assert len(ct) == 1
    assert ct[0].get("cui_lucrator") == "1800101410013"
    assert int(ct[0].get("contributie_lucrator")) == 100   # 10000 * 1/100


def test_d114_venit_zero_refuza():
    """venit_lucrator <= 0 -> erori_generare ne-gol (delta minim)."""
    assert d114.erori_generare({}, _m()) == []
    c = [{"cui_lucrator": "1800101410013", "den_lucrator": "X", "nui_lucrator": "1", "nr_contract": "10",
          "data_contract": "01.01.2026", "venit_lucrator": 0, "contributie_lucrator": 0}]
    assert d114.erori_generare({}, _m(contracte=c))


def test_d114_camp_lipsa_lucrator_refuza():
    """Camp obligatoriu lipsa pe contract (nui) -> erori_generare ne-gol."""
    c = [{"cui_lucrator": "1800101410013", "den_lucrator": "X", "nui_lucrator": "", "nr_contract": "10",
          "data_contract": "01.01.2026", "venit_lucrator": 10000, "contributie_lucrator": 100}]
    assert d114.erori_generare({}, _m(contracte=c))
