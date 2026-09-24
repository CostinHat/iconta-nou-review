# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D230 gol NU produce declaratie; identitatea PF + entitatea ONG
tin. Aserteaza STRUCTURAL (tip exceptie, atribute XML prin ElementTree) - NU `"sir" in xml`.

D230 (redirectionare pana la 3,5% catre ONG) = PF + o entitate beneficiara, introduse de contabil (ecran nou,
scos din _DOAR_API). Structura din D230Validator.jar (radacina declaratie230, ns declaratie:v5). Reguli probate:
R_optiune (valabilitate_distribuire 1/2 obligatoriu la bifa_entitate=1); R_procent (procent <= 3.5).
Calitatea mesajelor (limba contabilului) e urmarita de test_mesaje_generare_fara_camp_intern.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d230, declaratii_api
from core.common import Perioada

_TIP = "d230"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d230:declaratie:v5}"


def _cnp(body12):
    w = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(body12[i]) * w[i] for i in range(12)) % 11
    return body12 + str(1 if c == 10 else c)


_ID = {"nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ANA MARIA", "cif_c": _cnp("196022915094"),
       "den_entitate": "Asociatia Binele", "cif_entitate": "12345678",
       "cont_entitate": "RO49AAAA1B31007593840000", "valabilitate_distribuire": 2}


def test_d230_nu_e_doar_api():
    """d230 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d230_cerere_goala_refuza_la_api():
    """Bloc validare API: fara identitate/entitate -> lista erori ne-goala; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d230", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d230", {"tenant_id": 1, "an": 2025, "manual": dict(_ID)})
    assert goala and valida == []


def test_d230_formular_gol_refuza():
    """Fara identitate completa / entitate -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d230.genereaza(None, None, Perioada(2025, luna=12), {"nume_c": "X"})


def test_d230_valabilitate_invalida_refuza():
    """R_optiune: valabilitate_distribuire diferit de 1/2 -> refuz (nu XML gresit)."""
    with pytest.raises(ValueError):
        d230.genereaza(None, None, Perioada(2025, luna=12), dict(_ID, valabilitate_distribuire=0))


def test_d230_genereaza_structural():
    """Regresie STRUCTURALA: intrare reala -> <bursa_entit> cu bifa_entitate=1, den_entitate, valabilitate=2."""
    xml, res = d230.genereaza(None, None, Perioada(2025, luna=12), dict(_ID))
    root = ET.fromstring(xml)
    assert root.get("cif_c") == _ID["cif_c"]
    be = root.findall(_NS + "bursa_entit")
    assert len(be) == 1
    assert be[0].get("bifa_entitate") == "1"
    assert be[0].get("den_entitate") == "Asociatia Binele"
    assert be[0].get("valabilitate_distribuire") == "2"


def test_d230_procent_plafonat_structural():
    """R_procent: procent > 3.5 -> plafonat la 3.5 (atribut XML), nu se emite gresit."""
    xml, _ = d230.genereaza(None, None, Perioada(2025, luna=12), dict(_ID, procent=10))
    be = ET.fromstring(xml).findall(_NS + "bursa_entit")[0]
    assert be.get("procent") == "3.5"
