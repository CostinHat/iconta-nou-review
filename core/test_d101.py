# -*- coding: utf-8 -*-
"""Teste gardian pentru D101 - modulul a fost REFACUT complet 16.07.2026.

Fisierul vechi genera dupa schema D101G ("Grup fiscal"), o declaratie diferita
pentru grupuri fiscale consolidate - nu D101 individual, pe care il foloseste o
firma obisnuita. Structura de calcul (P1-P53) era dintr-o versiune veche,
incompatibila cu formularul curent (P1-P16, OPANAF 206/2025). Namespace-ul corect
(v10) a fost confirmat direct de validatorul oficial ANAF, dupa o prima incercare
gresita (v1).
"""
import pytest
from core.d101 import calcul_d101, build_xml, erori_generare, NS


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
            "adresa": "Bd. Timisoara 26Z", "caen": "4711"}


def test_namespace_e_v10_nu_v1():
    """Confirmat direct de validatorul oficial: 'Valoarea corecta este
    xmlns=mfp:anaf:dgti:d101:declaratie:v10'."""
    assert NS == "mfp:anaf:dgti:d101:declaratie:v10"


def test_calcul_simplu_profit():
    """Venituri 20000, cheltuieli 12000 -> profit 8000, impozit 16% = 1280."""
    res = calcul_d101(_prof(), 2025, venituri_totale=20000, cheltuieli_totale=12000)
    assert res.P["P1"] == 20000
    assert res.P["P2"] == 12000
    assert res.P["P3"] == 8000
    assert res.P["P9"] == 8000
    assert res.P["P11"] == 1280
    assert res.total_plata_a == 1280


def test_pierdere_nu_genereaza_impozit_negativ():
    res = calcul_d101(_prof(), 2025, venituri_totale=5000, cheltuieli_totale=9000)
    assert res.P.get("P9", 0) == 0
    assert "P11" not in res.P
    assert res.total_plata_a == 0


def test_plati_anticipate_mai_mari_dau_diferenta_de_recuperat():
    """Impozit calculat 1280, dar platit deja 1500 prin D100 -> P16 (de recuperat)."""
    res = calcul_d101(_prof(), 2025, venituri_totale=20000, cheltuieli_totale=12000,
                       impozit_trimestrial_d100=1500)
    assert res.P["P16"] == 220
    assert "P15" not in res.P
    assert res.total_plata_a == 0


def test_data_i_si_data_s_sunt_obligatorii_in_xml():
    """Regresie: Data_S lipsea complet - cauza erorii dovedite pe validatorul
    oficial ('Data_S: atributul trebuie sa existe')."""
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'Data_I="01.01.2025"' in xml
    assert 'Data_S="31.12.2025"' in xml


def test_lipsa_caen_e_prinsa_la_generare():
    prof = dict(_prof())
    del prof["caen"]
    erori = erori_generare(prof)
    assert any("CAEN" in e for e in erori)
