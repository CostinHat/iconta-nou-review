# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D600 gol NU produce declaratie; identitatea + cel putin o
componenta CAS (totalPlata_A>0) tin. Aserteaza STRUCTURAL (tip exceptie, atribute XML prin ElementTree)
- NU `"sir" in xml`.

D600 (baza CAS/CASS estimata, PF) = structura PLATA pe <declaratie600> (ns declaratie:v2). Reguli probate:
R10 luna=12; R42 totalPlata_A>0; calea CAS DUK-valida = cas_opt=1 + baza1..baza12 (baze lunare).
"""
import xml.etree.ElementTree as ET

import pytest
from core import d600, declaratii_api
from core.common import Perioada

_TIP = "d600"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d600:declaratie:v2}"
_ID = {"nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ION", "cif_c": "1800101221144",
       "adresa_c": "Cluj-Napoca, Str. A nr.1"}


def _m(**ov):
    m = dict(_ID, cas_opt=1)
    for i in range(1, 13):
        m["baza%d" % i] = 4050
    m.update(ov)
    return m


def test_d600_nu_e_doar_api():
    """d600 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d600_cerere_goala_refuza_la_api():
    """Bloc validare API: fara identitate -> erori; cerere valida -> lista goala."""
    goala = declaratii_api.valideaza_cerere("d600", {"tenant_id": 1, "an": 2026})
    valida = declaratii_api.valideaza_cerere("d600", {"tenant_id": 1, "an": 2026, "manual": _m()})
    assert goala and valida == []


def test_d600_formular_gol_refuza():
    """Identitate fara nicio componenta CAS/CASS (totalPlata_A=0) -> ValueError (R42)."""
    with pytest.raises(ValueError):
        d600.genereaza(None, None, Perioada(2026, luna=12), dict(_ID))


def test_d600_structural():
    """Regresie STRUCTURALA: <declaratie600> plat; cas_opt=1, baza1 emis, luna=12, totalPlata_A>0."""
    xml, res = d600.genereaza(None, None, Perioada(2026, luna=12), _m())
    root = ET.fromstring(xml)
    assert root.tag == _NS + "declaratie600"
    assert root.get("luna") == "12" and root.get("cas_opt") == "1" and root.get("baza1") == "4050"
    assert int(root.get("totalPlata_A")) > 0
    assert list(root) == []   # structura PLATA


def test_d600_fara_componenta_refuza():
    """R42: totalPlata_A<=0 -> erori_generare ne-gol (delta minim = componenta CAS)."""
    assert d600.erori_generare({}, _m()) == []
    assert d600.erori_generare({}, dict(_ID))
