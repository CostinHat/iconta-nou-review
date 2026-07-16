# -*- coding: utf-8 -*-
"""Teste gardian pentru D300 — lantul de calcul R27->R42 lipsea complet.

Descoperit prin audit pe date reale (16.07.2026): modulul calcula R17 (colectata)
si R22/R30/R31 (deductibila), apoi sarea direct la R40/R42 (rezultat), ignorand
lantul obligatoriu R27->R28->R32->R34->R37->R40->R42 pe care validatorul il
verifica formula cu formula (structura_D300_v12.0.0_10022026.pdf).
"""
from decimal import Decimal
from core.d300 import calcul_d300


def _prof(pro_rata=100):
    return {"cui": "14399840", "nume": "X", "adresa": "Y", "banca": "BCR",
            "iban": "RO1", "caen": "4711", "tip_decont": "L", "pro_rata": pro_rata}


def test_lantul_R27_R42_se_calculeaza_complet():
    """Livrare 10000@21% (TVA 2100), achizitie 1000@21% (TVA 210) -> de plata 1890."""
    facturi = [
        {"directie": "emisa", "total": 12100, "tva": 2100},
        {"directie": "primita", "total": 1210, "tva": 210},
    ]
    res = calcul_d300(_prof(), 2026, 6, facturi)
    assert res.R["R17_2"] == 2100          # total colectata
    assert res.R["R27_2"] == 210           # total deductibila (lipsea complet)
    assert res.R["R28_2"] == 210           # subtotal dedusa
    assert res.R["R32_2"] == 210           # total dedusa
    assert res.R["R34_2"] == 1890          # taxa de plata (17-32)
    assert res.R["R37_2"] == 1890          # TVA de plata cumulat
    assert res.R["R41_2"] == 1890          # sold de plata la sfarsit
    assert "R42_2" not in res.R            # nu exista sold negativ simultan
    assert res.tva_de_plata == 1890


def test_formula_R27_respecta_structura_oficiala():
    """R27_2 = R18_2+R19_2+R20_2+R21_2+R22_2+R23_2+R24_2+R25_2+R43_2+R44_2+R74_2+R75_2"""
    facturi = [{"directie": "primita", "total": 1210, "tva": 210}]  # -> R22_2=210
    res = calcul_d300(_prof(), 2026, 6, facturi)
    assert res.R["R27_2"] == res.R["R22_2"]


def test_achizitie_mai_mare_decat_livrarea_da_sold_negativ():
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},
        {"directie": "primita", "total": 12100, "tva": 2100},
    ]
    res = calcul_d300(_prof(), 2026, 6, facturi)
    assert res.R["R33_2"] == 1890          # suma negativa in perioada
    assert res.R["R40_2"] == 1890          # suma negativa cumulata
    assert res.R["R42_2"] == 1890          # sold negativ la sfarsit
    assert "R34_2" not in res.R
    assert res.tva_de_recuperat == 1890


def test_fara_operatiuni_nu_scrie_randuri_goale():
    res = calcul_d300(_prof(), 2026, 6, [])
    assert "R27_2" not in res.R
    assert "R32_2" not in res.R
