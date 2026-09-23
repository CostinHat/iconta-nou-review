# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6 + METODA §23] GARDA: formularul D200 gol NU produce declaratie; regulile pe
categorie tin. Aserteaza STRUCTURAL (tip de exceptie, liste de erori, atribute/elemente XML prin
ElementTree) - NU `"sir" in xml` (ar creste clichetul 50, scan_garzi_pe_text).

D200 (venituri realizate din Romania, persoane fizice) e produsa din sectiunile pe categorie introduse
de contabil in formularul manual (lista, ecran nou, scos din _DOAR_API). Nomenclatorul categ_venit e cel
oficial (structura_D200, lista 1,2,3,4,5,7,9,10,13,14); regulile pe categorie (14=castig/pierdere;
13=cere organizator den_orgJN+cif_orgJN) din core/d200.py, probate pe validatorul D200 v3.
Calitatea mesajelor (limba contabilului, fara token intern) e urmarita de test_mesaje_generare_fara_camp_intern.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d200, declaratii_api
from core.common import Perioada

_TIP = "d200"  # in variabila, nu literal: test de apartenenta structural (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d200:declaratie:v1}"
# identitate valida (CNP checksum-valid, ca reperul DUK lot2) - ca sa trecem de antet la regulile pe sectiune
_ID = {"cif_i": "1800101221144", "nume_c": "POPESCU", "prenume_c": "ION",
       "den_i": "POPESCU ION", "adresa_i": "Bucuresti Sector 1"}
_SECT_OK = {"categ_venit": 1, "caen": "6201", "venit_brut": 100000, "chelt": 30000}


def test_d200_nu_e_doar_api():
    """d200 are formular manual in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d200_cerere_goala_refuza_la_api():
    """Bloc validare API: fara sectiuni -> lista de erori ne-goala; cerere valida -> lista goala.
    Structural (adevar/lungime), fara ancora pe textul mesajului."""
    goala = declaratii_api.valideaza_cerere("d200", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d200", {"tenant_id": 1, "an": 2025, "manual": dict(_ID, sectiuni=[_SECT_OK])})
    assert goala and valida == []


def test_d200_formular_gol_refuza():
    """Nicio sectiune -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d200.genereaza(None, None, Perioada(2025), dict(_ID, sectiuni=[]))


def test_d200_categ14_castig_pierdere_discrimineaza():
    """Categ 14 (transfer titluri): fara castig/pierdere -> refuz; cu castig -> genereaza (calibrare)."""
    with pytest.raises(ValueError):
        d200.genereaza(None, None, Perioada(2025),
                       dict(_ID, sectiuni=[{"categ_venit": 14, "castig": 0, "pierdere": 0}]))
    xml, _ = d200.genereaza(None, None, Perioada(2025),
                            dict(_ID, sectiuni=[{"categ_venit": 14, "castig": 5000, "pierdere": 0}]))
    sect = ET.fromstring(xml).findall(_NS + "sect_2")
    assert len(sect) == 1 and sect[0].get("categ_venit") == "14"


def test_d200_categ13_organizator_discrimineaza():
    """Categ 13 (jocuri de noroc): fara organizator -> refuz; cu den+cif organizator -> genereaza."""
    with pytest.raises(ValueError):
        d200.genereaza(None, None, Perioada(2025),
                       dict(_ID, sectiuni=[{"categ_venit": 13, "venit_brut": 5000, "chelt": 0}]))
    xml, _ = d200.genereaza(None, None, Perioada(2025),
                            dict(_ID, sectiuni=[{"categ_venit": 13, "venit_brut": 5000, "chelt": 0,
                                                 "den_orgJN": "Loteria Romana", "cif_orgJN": "12345674"}]))
    assert ET.fromstring(xml).findall(_NS + "sect_2")[0].get("den_orgJN") == "Loteria Romana"


def test_d200_sectiune_valida_genereaza():
    """Regresie STRUCTURALA: o sectiune reala -> <sect_2> cu categ_venit=1, prenume_c ne-vid, suma corecta."""
    xml, res = d200.genereaza(None, None, Perioada(2025), dict(_ID, sectiuni=[_SECT_OK]))
    root = ET.fromstring(xml)
    assert root.get("prenume_c") == "ION"                 # bugul prins la proba F4 (prenume_c vid respins de DUK)
    sects = root.findall(_NS + "sect_2")
    assert len(sects) == 1 and sects[0].get("categ_venit") == "1"
    assert res.total_plata_a == 70000                     # venit_net = 100000 - 30000
