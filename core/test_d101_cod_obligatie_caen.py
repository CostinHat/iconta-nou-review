# -*- coding: utf-8 -*-
"""GARD (TURA 3, 10.08.2026): D101 respinge PRE-DUK cod_obligatie in afara nomenclatorului
{102,103,104,105} si un cod CAEN care nu e N(4). Pe HEAD ambele se emit TACIT -> DUK
'valoarea ... nu se afla in lista'. Fara DB."""
import pytest
from core import d101

_PROF = {"cui": "19", "nume": "ALFA SRL", "adresa": "Str. Test 1", "caen": "6201"}
_BASE = {"P1": 200000, "P2": 100000, "P4": 0, "P5": 0}


def test_cod_obligatie_out_of_nomenclator_raise():
    with pytest.raises(ValueError, match="cod_obligatie invalid"):
        d101.calcul_d101(_PROF, 2026, _BASE, cod_obligatie="999")


def test_cod_obligatie_din_nomenclator_nu_raise():
    for c in ("102", "103", "104", "105"):
        d101.calcul_d101(_PROF, 2026, _BASE, cod_obligatie=c)


def test_caen_non_n4_prins_pre_duk():
    for bad in ("12", "ABCD", "62011"):
        erori = d101.erori_generare(dict(_PROF, caen=bad))
        assert any("cod CAEN invalid" in e for e in erori), (bad, erori)


def test_caen_n4_trece():
    assert d101.erori_generare(_PROF) == []
