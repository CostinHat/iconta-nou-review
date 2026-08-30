# -*- coding: utf-8 -*-
"""GARD T1 (LANT legislatie TURA 3, 10.08.2026): D101 valideaza cifra de control a CUI-ului
firmei PRE-DUK. Pe HEAD (8b74ccb) erori_generare verifica DOAR non-gol -> un CUI cu checksum
gresit trece TACIT (lista goala) si-l prinde abia DUK la depunere. Dupa fix: mesaj EXACT
'CUI firmă invalid (...)'. Construit fara DB (profil sintetic + erori_generare)."""
from core import d101
from core.identitate import valideaza_cui

_PROF_OK = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR", "cui": "19", "nume": "ALFA SRL", "adresa": "Str. Test 1, Bucuresti", "caen": "6201"}


def test_cui_checksum_gresit_prins_pre_duk():
    assert valideaza_cui("12345678")[0] is False    # checksum invalid (validator comun)
    erori = d101.erori_generare(dict(_PROF_OK, cui="12345678"))
    assert any("CUI firmă invalid" in e and "12345678" in e for e in erori), erori


def test_cui_valid_trece():
    assert d101.erori_generare(_PROF_OK) == []
