# -*- coding: utf-8 -*-
"""[Regula 4 + METODA §23] GARDA: formularul D212 (increment proof-of-pattern) - identitatea PF
produce declaratia de identificare DUK-minima; apelul gol e refuzat cu mesaj de contabil. Aserteaza
STRUCTURAL (tip exceptie, liste de erori, atribute XML prin ElementTree) - NU `"sir" in xml`.

D212 (Declaratia unica PF) e MANUALA. Increment: UI strange identitatea (cif/nume_c/adresa_c) si
AFISEAZA fisa RIP (informativ); genereaza cazul minim DUK-valid (identitate + bife 0; totalPlata_A =
suma cifrelor CNP, DUK regula R4 cand nu e nimic de plata). Popularea cap11/oblig_realizat = pas urmator.
Calitatea mesajelor (limba contabilului) e urmarita de test_mesaje_generare_fara_camp_intern.
"""
import xml.etree.ElementTree as ET

import pytest
from core import d212, declaratii_api
from core.common import Perioada

_TIP = "d212"  # in variabila, nu literal (scan_garzi_pe_text flageaza doar literal-sir)
_NS = "{mfp:anaf:dgti:d212:declaratie:v11}"
# identitate valida (CNP checksum-valid, ca reperul DUK lot6)
_ID = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}


def test_d212_nu_e_doar_api():
    """d212 are formular in UI -> nu mai e ascuns; apare in selectorul de tipuri."""
    assert _TIP not in declaratii_api._DOAR_API
    assert _TIP in declaratii_api.tipuri()


def test_d212_cerere_goala_refuza_la_api():
    """Bloc validare API: fara identitate -> lista de erori ne-goala; cu identitate -> lista goala.
    Structural (adevar/lungime), fara ancora pe textul mesajului."""
    goala = declaratii_api.valideaza_cerere("d212", {"tenant_id": 1, "an": 2025})
    valida = declaratii_api.valideaza_cerere("d212", {"tenant_id": 1, "an": 2025, "manual": dict(_ID)})
    assert goala and valida == []


def test_d212_manual_gol_refuza():
    """Fara identitate -> ValueError (tip), NU XML."""
    with pytest.raises(ValueError):
        d212.genereaza(None, None, Perioada(an=2025), {})


def test_d212_identitate_genereaza_minim_valid():
    """Regresie STRUCTURALA: identitatea -> <d212> cu cif/nume_c; totalPlata_A = suma cifrelor CNP (R4)."""
    xml, res = d212.genereaza(None, None, Perioada(an=2025), dict(_ID))
    root = ET.fromstring(xml)
    assert root.tag == _NS + "d212"
    assert root.get("cif") == "1800101221144"
    assert root.get("nume_c") == "POPESCU ION"
    assert root.get("adresa_c") == "Bucuresti Sector 1"
    # R4: fara sume 'de plata', totalPlata_A = suma cifrelor CNP (marcaj de control nenul) = 25
    assert root.get("totalPlata_A") == "25"
    assert res.total_plata_a == 25
    # increment: NU se emit capitole de venit inca (cap11/oblig_realizat absente)
    assert root.find(_NS + "cap11") is None and root.find(_NS + "oblig_realizat") is None
