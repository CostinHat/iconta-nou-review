# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D201 gol NU produce declaratie; identitatea + sectiunile +
regulile pe sectiune tin. Aserteaza STRUCTURAL (tip exceptie, liste erori, atribute XML prin ElementTree) -
NU `"sir" in xml`.

D201 (venituri din strainatate PF) = sectiuni pe (tara, categorie de venit) introduse de contabil (lista,
ecran nou, scos din _DOAR_API). Structura din D201Validator.jar (radacina declaratie201, ns declaratie:v2).
Reguli probate: pereche (statul, categ_venit) unica; imp2 doar la categ_venit=14 (R33); categ_venit=23 net-only.
Calitatea mesajelor (limba contabilului) e urmarita de test_mesaje_generare_fara_camp_intern.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d201, declaratii_api
from core.common import Perioada

_TIP = "d201"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d201:declaratie:v2}"
_ID = {"nume_c": "ION", "initiala_c": "V", "prenume_c": "DAN", "cif_c": "1800101221144"}
_SECT_OK = {"categ_venit": 3, "statul": 276, "venit_B": 1000, "chlt_D": 0}


def test_d201_nu_se_mai_ofera_formular_inlocuit_de_declaratia_unica():
    """[lotul 13, deficiența 660] D201 e înlocuită de Declarația unică (D212): nu e în selector, nici în dispecer, iar o cerere — chiar
    completă — primește motivul cu textul Codului fiscal (`declaratii_api.FORMULARE_INLOCUITE`), nu XML."""
    assert _TIP not in declaratii_api.tipuri() and _TIP not in declaratii_api.DECLARATII
    er = declaratii_api.valideaza_cerere(_TIP, {"tenant_id": 1, "an": 2025, "manual": dict(_ID, sectiuni=[_SECT_OK])})
    assert len(er) == 1 and "nu se mai depune" in er[0] and declaratii_api.FORMULARE_INLOCUITE[_TIP][1] in er[0], er


def test_d201_formular_gol_refuza():
    """Nicio sectiune -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d201.genereaza(None, None, Perioada(2025, luna=12), dict(_ID, sectiuni=[]))


def test_d201_imp2_doar_la_categ14_discrimineaza():
    """R33: imp2 (impozit pe salarii) la categ != 14 -> refuz; la categ=14 -> genereaza (calibrare)."""
    with pytest.raises(ValueError):
        d201.genereaza(None, None, Perioada(2025, luna=12),
                       dict(_ID, sectiuni=[{"categ_venit": 3, "statul": 276, "venit_B": 1000, "chlt_D": 0, "imp2": 50}]))
    xml, _ = d201.genereaza(None, None, Perioada(2025, luna=12),
                            dict(_ID, sectiuni=[{"categ_venit": 14, "statul": 276, "venit_B": 1000, "chlt_D": 0, "imp2": 50}]))
    assert ET.fromstring(xml).findall(_NS + "sect_2")[0].get("categ_venit") == "14"


def test_d201_sectiune_valida_genereaza():
    """Regresie STRUCTURALA: o sectiune reala -> <sect_2> cu categ_venit=3, statul=276, venit_N=venit_B-chlt_D (R30)."""
    xml, res = d201.genereaza(None, None, Perioada(2025, luna=12), dict(_ID, sectiuni=[_SECT_OK]))
    root = ET.fromstring(xml)
    assert root.get("cif_c") == "1800101221144"
    sects = root.findall(_NS + "sect_2")
    assert len(sects) == 1
    assert sects[0].get("categ_venit") == "3" and sects[0].get("statul") == "276"
    assert sects[0].get("venit_N") == "1000"   # R30: 1000 - 0
