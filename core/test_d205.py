# -*- coding: utf-8 -*-
"""Teste gardian pentru D205 - REFACUT A DOUA OARA 16.07.2026.

Prima incercare avea trei greseli, gasite toate prin validatorul oficial:
1. Atributele reale ale <benef> nu erau cele extrase dintr-un grep ingust pe
   binar: den1 (nu nume1), cifR (nu cif), Rezid cu majuscula, tip_venit1 pe
   FIECARE beneficiar (nu doar pe sect_II), id_inreg (secvential).
2. tip_venit pentru dividende e "08" (confirmat: "08 1.a) venituri din
   dividende"), NU "25" - la 08 se completeaza divid_D/divid_P, la 25
   baza1/imp1 sunt INTERZISE (regulile R44/R45).
3. Tcastig/Tpierd/T_VB/T_GAR se calculeaza STRICT pe tip_venit1 corespunzator
   (25 si 29) - la tip_venit=08 raman 0, nu se calculeaza din divid_D/divid_P.
4. totalPlata_A = suma(nrben)+suma(Tcastig)+suma(Tpierd)+suma(T_VB)+
   suma(T_GAR)+suma(Tbaza)+suma(Timp) - suma pe TOATE campurile din sect_II,
   nu doar Timp.
"""
import pytest
from core.d205 import calcul_d205, build_xml


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA", "adresa": "X"}


def test_dividende_valid():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "POPESCU Ion", "cif": "1850101450013",
         "baza": 10000, "imp": 1000, "castig": 10000}])
    xml = build_xml(res)
    assert 'tip_venit="08"' in xml
    assert 'divid_D="10000"' in xml


def test_tcastig_ramane_zero_la_dividende():
    """Regresie: Tcastig=10000 (calculat din divid_D) era gresit - regula
    oficiala il calculeaza doar din beneficiari cu tip_venit1=25."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013",
         "baza": 5000, "imp": 500, "castig": 5000}])
    xml = build_xml(res)
    assert 'Tcastig="0"' in xml
    assert 'Tpierd="0"' in xml


def test_totalPlata_A_e_suma_tuturor_campurilor_sect_II():
    """Regresie: totalPlata_A=Timp era gresit. Formula reala include si nrben,
    Tbaza (T_VB/T_GAR/Tcastig/Tpierd raman 0 la dividende)."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013",
         "baza": 10000, "imp": 1000, "castig": 10000}])
    xml = build_xml(res)
    # nrben(1) + Tcastig(0) + Tpierd(0) + T_VB(0) + T_GAR(0) + Tbaza(10000) + Timp(1000)
    assert 'totalPlata_A="11001"' in xml


def test_id_inreg_e_secvential():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "A", "cif": "1850101450013", "baza": 100, "imp": 10, "castig": 100},
        {"categ": "1.a", "nume": "B", "cif": "1850101450013", "baza": 200, "imp": 20, "castig": 200},
    ])
    xml = build_xml(res)
    assert 'id_inreg="1"' in xml
    assert 'id_inreg="2"' in xml


def test_atributele_reale_pe_benef():
    """Regresie: den1 (nu nume1), cifR (nu cif), Rezid majuscula (nu rezid),
    tip_venit1 pe fiecare beneficiar. 'categ' nu e atribut valid - omis."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013", "baza": 100, "imp": 10, "castig": 100}])
    xml = build_xml(res)
    linie = [l for l in xml.split("\n") if "<benef" in l][0]
    assert "den1=" in linie and "nume1=" not in linie
    assert "cifR=" in linie and 'cif="' not in linie
    assert "Rezid=" in linie
    assert "tip_venit1=" in linie
    assert "categ=" not in linie
