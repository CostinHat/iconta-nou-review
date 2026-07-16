# -*- coding: utf-8 -*-
"""Teste gardian pentru D101 - REFACUT A DOUA OARA 16.07.2026.

Prima refacere fusese GRESITA IN EXECUTIE: structura veche (P1-P53) era de fapt
cea CORECTA (confirmata ulterior direct din D101Validator.jar, clasa
Identificare), dar fusese inlocuita cu P1-P16 inventat din cap, crezand gresit
ca modulul vechi genera dupa formularul de grup fiscal (D101G). A doua refacere
foloseste doar atributele confirmate in constant pool-ul validatorului instalat.
"""
import pytest
from core.d101 import calcul_d101, build_xml, erori_generare, _nr_evid, NS


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
            "adresa": "Bd. Timisoara 26Z", "caen": "4711"}


def test_namespace_e_v10():
    assert NS == "mfp:anaf:dgti:d101:declaratie:v10"


def test_calcul_simplu_profit():
    res = calcul_d101(_prof(), 2025, venituri_totale=20000, cheltuieli_totale=12000)
    assert res.P["P1"] == 20000
    assert res.P["P3"] == 8000
    assert res.P["P9"] == 8000
    assert res.P["P11"] == 1280
    assert res.total_plata_a == 1280


def test_pierdere_nu_genereaza_impozit():
    res = calcul_d101(_prof(), 2025, venituri_totale=5000, cheltuieli_totale=9000)
    assert res.P.get("P9", 0) == 0
    assert "P11" not in res.P


def test_toate_flagurile_apar_pe_radacina():
    """Regresie: prima incercare avea doar d_anulare/d_succ. Atributele reale
    (dovedite in Identificare.class): d_rec, d_recN, d_reg, d_reglem, d_anulare,
    d_succ, d_grup, d_prof, d_alte."""
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    for flag in ("d_rec", "d_recN", "d_reg", "d_reglem", "d_anulare",
                 "d_succ", "d_grup", "d_prof", "d_alte"):
        assert '%s="0"' % flag in xml, "lipseste %s" % flag


def test_data_i_si_data_s():
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'Data_I="01.01.2025"' in xml
    assert 'Data_S="31.12.2025"' in xml


def test_nr_evid_are_23_caractere_si_cifra_control():
    n = _nr_evid("14399840", 2025, 12)
    assert len(n) == 23 and n.isdigit()
    suma = sum(int(c) for c in n[:21])
    assert n[21:23] == "%02d" % (suma % 100)


def test_lipsa_caen_e_prinsa_la_generare():
    prof = dict(_prof())
    del prof["caen"]
    assert any("CAEN" in e for e in erori_generare(prof))
