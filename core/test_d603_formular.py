# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D603 gol NU produce declaratie; identitatea + categoria de
exceptare + statul de asigurare (!=RO) + perioada tin. Aserteaza STRUCTURAL (tip exceptie, atribute XML
prin ElementTree) - NU `"sir" in xml`.

D603 (exceptare CASS, PF) = structura PLATA (toate campurile atribute pe <d603>). Structura din
D603Validator.jar (radacina d603, ns declaratie:v1). Reguli probate: statAsigurare!=RO (R36);
judetContrib (cod auto 2 litere) obligatoriu la taraContrib=RO (R21); luna=12; exceptare in {2,3,4}.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d603, declaratii_api
from core.common import Perioada

_TIP = "d603"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d603:declaratie:v1}"


def _m(**ov):
    m = {"numeContrib": "POPESCU ION", "cif": "1800101221144", "taraContrib": "RO", "judetContrib": "CJ",
         "exceptare": 2, "statAsigurare": "DE",
         "dataInceput": "2026-01-01", "dataSfarsit": "2026-12-31", "dataExceptare": "2026-01-15",
         "documente": "Formular A1 emis de autoritatea competenta din Germania"}
    m.update(ov)
    return m


def test_d603_nu_e_doar_api():
    """d603 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d603_cerere_goala_refuza_la_api():
    """Bloc validare API: fara identitate/stat/exceptare -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d603", {"tenant_id": 1, "an": 2026})
    valida = declaratii_api.valideaza_cerere("d603", {"tenant_id": 1, "an": 2026, "manual": _m()})
    assert goala and valida == []


def test_d603_formular_gol_refuza():
    """Fara stat/date -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d603.genereaza(None, None, Perioada(2026, luna=12), {"numeContrib": "X", "cif": "1800101221144"})


def test_d603_structural():
    """Regresie STRUCTURALA: <d603> plat cu atributele cheie; luna=12."""
    xml, res = d603.genereaza(None, None, Perioada(2026, luna=12), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "d603"
    assert root.get("luna") == "12" and root.get("exceptare") == "2"
    assert root.get("statAsigurare") == "DE" and root.get("judetContrib") == "CJ"
    assert list(root) == []   # structura PLATA: fara elemente copil


def test_d603_stat_ro_refuza():
    """statAsigurare=RO -> erori_generare ne-gol (delta minim; R36)."""
    assert d603.erori_generare({}, _m()) == []
    assert d603.erori_generare({}, _m(statAsigurare="RO"))


def test_d603_perioada_inversata_refuza():
    """dataInceput >= dataSfarsit -> erori_generare ne-gol (R36)."""
    assert d603.erori_generare({}, _m(dataInceput="2026-12-31", dataSfarsit="2026-01-01"))
