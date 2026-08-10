# -*- coding: utf-8 -*-
"""Gard D205: Rezid (2.Rezident/Nerezident) DERIVAT din identitate, nu hardcodat "1".

NECONFORMITATE reparata la radacina (HEAD 6cd0054): build_xml emitea Rezid="1" hardcodat pentru
orice beneficiar. Model corect confruntat cu structura ANAF (anaf_surse/d205_struct_anaf.txt,
rand 32/33) SI cu validatorul oficial DUK:
  - Rezid N(1) =(1,2): 1=rezident, 2=nerezident, derivat din CNP/NIF (rand 32).
  - DUK regula R32: Rezid=2 admis DOAR pt. tip_venit1 in (04,16,18,25,26,27,28,29,30) - NU 08.
  - DUK regula R33: daca Rezid=2 atunci Stat_R (statul de rezidenta) obligatoriu.
=> pt. DIVIDENDE (tip_venit1=08) un beneficiar nerezident e ILEGAL pe D205 (se declara pe D207);
   in plus tabelul `asociati` NU are camp de tara pentru Stat_R. Deci un beneficiar de dividende
   fara CNP romanesc de rezident e REFUZAT la generare (nu emis cu Rezid="1" fals).

MUTATIE DOVEDITA:
  HEAD 6cd0054: build_xml emite Rezid="1" pt. orice cif, fara refuz -> pytest.raises PICA (nu ridica).
  Post-fix: beneficiar nerezident -> ValueError; beneficiar rezident -> Rezid="1" derivat.
"""
import re
import pytest

from core.d205 import calcul_d205, build_xml


def _prof():
    return {"cui": "14399840", "nume": "TEST SRL", "adresa": "X"}


def test_cnp_rezident_derivare():
    from core.d205 import _rezid, _cnp_rezident   # helpere noi (post-fix) - local, ca sa nu
    # rupa colectarea celorlalte teste pe HEAD (unde simbolurile nu exista inca).
    # CNP romanesc de rezident (prima cifra 1..8) -> rezident
    assert _cnp_rezident("1700510400076") and _rezid("1700510400076") == "1"
    assert _cnp_rezident("2900101410012")   # prima cifra 2 (test fixture) - rezident structural
    # prima cifra 9 = persoana fizica straina (nerezident)
    assert not _cnp_rezident("9900101410011") and _rezid("9900101410011") == "2"
    # pasaport / cod non-13-cifre -> nerezident
    assert not _cnp_rezident("X1234567") and _rezid("X1234567") == "2"
    assert not _cnp_rezident("") and _rezid("") == "2"


def test_rezident_emite_rezid_1_derivat():
    """Cazul standard (rezident) ramane valid: Rezid emis = '1', derivat din CNP."""
    res = calcul_d205(_prof(), 2026, [
        {"categ": "1.a", "nume": "POPESCU ION", "cif": "1700510400076",
         "baza": 10000, "imp": 1600, "divid_d": 10000, "divid_p": 10000}])
    xml = build_xml(res)
    linie = re.search(r'<benef[^>]*/>', xml).group(0)
    assert 'Rezid="1"' in linie, linie
    assert res.beneficiari[0].rezid == "1"


def test_nerezident_dividende_refuzat():
    """MUTATIE: HEAD emite Rezid='1' pt. un nerezident (CNP prima cifra 9), fara sa ridice
    (pytest.raises PICA pe HEAD). Post-fix: ValueError care numeste nerezidentul + R32/R33."""
    res = calcul_d205(_prof(), 2026, [
        {"categ": "1.a", "nume": "SCHMIDT HANS", "cif": "9900101410011",
         "baza": 5000, "imp": 800, "divid_d": 5000, "divid_p": 5000}])
    assert len(res.beneficiari) == 1
    with pytest.raises(ValueError) as ei:
        build_xml(res)
    msg = str(ei.value)
    assert "NEREZIDENT" in msg and "R32" in msg, msg


def test_nerezident_pasaport_refuzat():
    """Pasaport (cod non-13-cifre) = nerezident -> refuzat (HEAD l-ar fi emis cu Rezid='1')."""
    res = calcul_d205(_prof(), 2026, [
        {"categ": "1.a", "nume": "JOHN DOE", "cif": "X1234567",
         "baza": 5000, "imp": 800, "divid_d": 5000, "divid_p": 5000}])
    with pytest.raises(ValueError):
        build_xml(res)
