# -*- coding: utf-8 -*-
"""Teste gardian pentru D300 — lantul de calcul R27->R42 lipsea complet.

Descoperit prin audit pe date reale (16.07.2026): modulul calcula R17 (colectata)
si R22/R30/R31 (deductibila), apoi sarea direct la R40/R42 (rezultat), ignorand
lantul obligatoriu R27->R28->R32->R34->R37->R40->R42 pe care validatorul il
verifica formula cu formula (structura_D300_v12.0.0_10022026.pdf).
"""
from decimal import Decimal
from core.common import Perioada
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
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
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
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R["R27_2"] == res.R["R22_2"]


def test_achizitie_mai_mare_decat_livrarea_da_sold_negativ():
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},
        {"directie": "primita", "total": 12100, "tva": 2100},
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R["R33_2"] == 1890          # suma negativa in perioada
    assert res.R["R40_2"] == 1890          # suma negativa cumulata
    assert res.R["R42_2"] == 1890          # sold negativ la sfarsit
    assert "R34_2" not in res.R
    assert res.tva_de_recuperat == 1890


def test_fara_operatiuni_nu_scrie_randuri_goale():
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [])
    assert "R27_2" not in res.R
    assert "R32_2" not in res.R


def test_d300_manual_cheie_necunoscuta_ridica():
    """Contract A1: manual d300 accepta doar chei Rxx_y; o cheie straina (typo) RIDICA, nu se
    ignora tacut (clasa 'or 21')."""
    import pytest
    with pytest.raises(ValueError) as e:
        calcul_d300(_prof(), Perioada(2026, luna=6), [], {"R9_1": 100, "totalGresit": 5})
    assert "necunoscut" in str(e.value).lower() and "totalGresit" in str(e.value)

import pytest
from core import duk as _duk300
from core.d300 import build_xml
_D300_DUK = _duk300.poate_valida("d300")


# ============================================================
#  Cluster cote TVA -> randuri | d300. Maparea cotelor pe randurile D300 (structura
#  v12.0.0, confirmata prin marja validatorului DUK). Bug reparat: achizitii deductibile
#  11% erau puse la R74 (=Rd.24.1, cota 19% legacy, marja 18-20%) si 9% la R76 (=taxare
#  inversa Rd.27.4). Corect: 11%->R23 (Rd.25), 21%->R22 (Rd.24).
# ============================================================
def test_cote_tva_maparea_pe_randuri_d300():
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},    # 21%
        {"directie": "emisa", "total": 1110, "tva": 110},    # 11%
        {"directie": "emisa", "total": 1090, "tva": 90},     # 9%
        {"directie": "primita", "total": 1210, "tva": 210},  # 21% deductibil
        {"directie": "primita", "total": 1110, "tva": 110},  # 11% deductibil
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    # LIVRARI (colectata): 21->Rd.9, 11->Rd.10, 9->Rd.11
    assert (res.R["R9_1"], res.R["R9_2"]) == (1000, 210)
    assert (res.R["R10_1"], res.R["R10_2"]) == (1000, 110)
    assert (res.R["R11_1"], res.R["R11_2"]) == (1000, 90)
    # ACHIZITII DEDUCTIBILE: 21->Rd.24(R22), 11->Rd.25(R23)
    assert (res.R["R22_1"], res.R["R22_2"]) == (1000, 210)
    assert (res.R["R23_1"], res.R["R23_2"]) == (1000, 110)   # 11% -> R23, NU R74
    # GARD anti-regresie: 11% NU merge la R74 (=19% legacy) si nici la R76 (=taxare inversa)
    assert res.R.get("R74_1", 0) == 0 and res.R.get("R74_2", 0) == 0
    assert res.R.get("R76_1", 0) == 0


def test_9pct_deductibil_nu_emite_rand_invalid_si_avertizeaza():
    # 9% deductibil: R75 (v12) / R76 respinse de validatorul DUK instalat -> NU se emit
    # (un atribut invalid ar respinge intreaga declaratie); se semnaleaza pentru declarare manuala.
    facturi = [{"directie": "primita", "total": 1090, "tva": 90}]  # 9% deductibil
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R.get("R75_1", 0) == 0 and res.R.get("R76_1", 0) == 0
    assert any("9%" in a and "MANUAL" in a for a in res.avertismente)


@pytest.mark.skipif(not _D300_DUK, reason="DUK d300 indisponibil")
def test_cote_tva_d300_proba_duk_valid():
    # Proba pana la declaratie: D300 cu livrari 21/11/9 + achizitii 21/11 trece DUKIntegrator.
    # Marja validatorului (R9_2 in 20-22%R9_1, R10_2 in 10-12%, R11_2 in 8-10%, R22=21%, R23=11%)
    # respinge orice swap cota<->rand - validarea confirma maparea. Un 9% deductibil in R76 (vechiul
    # cod) ERA respins de DUK - de aceea reparatia trece proba aici.
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},
        {"directie": "emisa", "total": 1110, "tva": 110},
        {"directie": "emisa", "total": 1090, "tva": 90},
        {"directie": "primita", "total": 1210, "tva": 210},
        {"directie": "primita", "total": 1110, "tva": 110},
        {"directie": "primita", "total": 1090, "tva": 90},   # 9% deductibil -> manual (avertisment), nu emis
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D300: %s" % rez.get("erori")
