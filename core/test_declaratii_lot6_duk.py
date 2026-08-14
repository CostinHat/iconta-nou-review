# -*- coding: utf-8 -*-
"""Lot 6 (final): Declaratia Unica D212, proba DUK cu validatorul OFICIAL ANAF.

D212 - declaratia unica privind impozitul pe venit si contributiile sociale datorate de
persoanele fizice (PFA/II/IF/venituri diverse). Generator MANUAL (core/d212.py, root <d212>,
ns mfp:anaf:dgti:d212:declaratie:v11, OPANAF - vezi anaf_surse/D212_IstoriaVersiunilor.txt).
Cazul minim = identificarea (cif/nume/adresa); capitolele (cap11 realizat, cap12 estimat,
cap14, obligatii, coasigurat) sunt extensibile prin manual. totalPlata_A se calculeaza.
Probat DUK valid pe calea standard core.duk.valideaza (retry DecValidation nou).
"""
from core.common import Perioada
from core import duk, d212


def test_d212_duk_valid():
    manual = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
    xml, _res = d212.genereaza(None, None, Perioada(an=2025), manual)
    v = duk.valideaza(xml, "d212", an=2025, luna=12, timeout=120)
    if v.get("stare") == "gri":
        import pytest
        pytest.skip("validator d212 indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", "d212 DUK nu e valid: %s" % v
