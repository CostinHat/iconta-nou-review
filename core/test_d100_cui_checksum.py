# -*- coding: utf-8 -*-
"""Gard T1 (CATALOG_INVALIDITATE.md, D100 #7/#11/#19): CUI-ul firmei trebuie validat de app
(checksum/format) PRE-DUK, cu mesajul EXACT al motivului, nu emis tacit si prins doar de DUK.

FAIL pe HEAD 8b74ccb: erori_generare verifica doar non-gol -> un CUI non-numeric / prea lung /
cu cifra de control gresita trece tacit (lista de erori goala, XML emis, doar DUK zice 'CUI invalid').
PASS dupa reparatie: erori_generare intoarce mesajul cu motivul exact din core.identitate.valideaza_cui,
iar genereaza ridica ValueError INAINTE de orice XML."""
from core import d100
from core.identitate import valideaza_cui

_BAZA = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR", "cui": "301111003", "nume": "ALFA MICRO SRL", "adresa": "Str. Test 1 Bucuresti"}


def _prof(cui):
    p = dict(_BAZA)
    p["cui"] = cui
    return p


def test_cui_valid_nu_produce_eroare():
    assert d100.erori_generare(_prof("301111003")) == []


def test_cui_non_numeric_prinde_cu_motiv():
    # #7 non-numeric -> valideaza_cui extrage cifrele; "30ABC" -> "30" lungime prea mica
    cui = "30A1B"
    erori = d100.erori_generare(_prof(cui))
    assert any("CUI firm" in e and "invalid" in e for e in erori), erori
    # motivul EXACT din sursa canonica apare in mesaj
    _, motiv = valideaza_cui(cui)
    assert any(motiv in e for e in erori), (motiv, erori)


def test_cui_over_length_prinde_cu_motiv():
    # #11 lungime > 10 cifre
    cui = "12345678901"
    erori = d100.erori_generare(_prof(cui))
    assert any("CUI firm" in e and "invalid" in e for e in erori), erori
    _, motiv = valideaza_cui(cui)
    assert "lungime" in motiv and any(motiv in e for e in erori), (motiv, erori)


def test_cui_checksum_gresit_prinde_cu_motiv():
    # #19 cifra de control gresita: 301111004 (valid = ...003)
    cui = "301111004"
    assert valideaza_cui(cui) == (False, "cifra de control")
    erori = d100.erori_generare(_prof(cui))
    assert any("cifra de control" in e for e in erori), erori


def test_mesajul_contine_cui_si_indicatie_profil():
    erori = d100.erori_generare(_prof("301111004"))
    e = [x for x in erori if "CUI firm" in x][0]
    assert "301111004" in e            # arata VALOAREA gresita
    assert "Profil firm" in e          # spune UNDE se corecteaza
