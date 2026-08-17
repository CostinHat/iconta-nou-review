# -*- coding: utf-8 -*-
"""Gard Task2 (10.08.2026): achizitiile cu taxare inversa PRIMITA nu mai dispar tacit din D300.

Confruntat cu sursa oficiala (anaf_surse/d300_struct_anaf.txt):
  - rd.12 (R12_1/R12_2) = "Achizitii de bunuri si servicii supuse masurilor de simplificare pentru
    care beneficiarul este obligat la plata TVA (taxare inversa)" = COLECTAT.
  - rd.25 (R25_1/R25_2) = acelasi text = DEDUCTIBIL. Net zero (colectat = deductibil).
  - rd.7 NU se foloseste: DUK impune V13/V14 R20_x = R7_x (alta familie), deci pentru masuri de
    simplificare perechea DUK-valida e R12<->R25 (probat DUK).

NECONFORMITATE (HEAD 6cd0054): calea `if ti: if emisa ... continue` arunca TACIT latura
beneficiarului (primita) - nici rand, nici avertisment. Cerinta Costin: fara drop tacit.

POST-FIX: se DERIVA R12 (colectat) + R25 (deductibil) din liniile facturii, net zero, cu gard
anti-dubla-numarare fata de introducerea manuala.
"""
import pytest
from core.common import Perioada
from core.d300 import calcul_d300


def _prof():
    return {"cui": "14399840", "nume": "X", "banca": "BCR", "iban": "RO1", "caen": "4711",
            "tip_decont": "L", "pro_rata": 100}


def _fact_rc(baza=1000, cota=21):
    return {"directie": "primita", "taxare_inversa": True, "linii": [(1, baza, cota)]}


def test_beneficiar_deriva_R12_R25():
    """MUTATIE (RED pe HEAD: R12/R25 lipseau, latura beneficiarului disparea tacit)."""
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [_fact_rc(1000, 21)])
    assert (res.R.get("R12_1"), res.R.get("R12_2")) == (1000, 210), "colectat rd.12 derivat"
    assert (res.R.get("R25_1"), res.R.get("R25_2")) == (1000, 210), "deductibil rd.25 derivat"
    # NU se pune la achizitia normala deductibila (rd.24/R22) - alta familie de randuri.
    assert res.R.get("R22_1", 0) == 0 and res.R.get("R22_2", 0) == 0


def test_beneficiar_net_zero():
    """Taxare inversa = colectat + deductibil egale -> impact ZERO pe TVA de plata."""
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [_fact_rc(40000, 21)])
    assert res.tva_de_plata == 0 and res.tva_de_recuperat == 0
    # intra si in totaluri: R17_2 (colectata) si R27_2 (deductibila) cresc cu aceeasi suma.
    assert res.R.get("R17_2", 0) == res.R.get("R27_2", 0) == 8400


def test_beneficiar_derivat_PLUS_manual_dubla_numarare_EROARE():
    """Gard anti-dubla-numarare (ca la rd.13): derivat automat + manual -> EROARE, nu insumare."""
    with pytest.raises(ValueError) as ei:
        calcul_d300(_prof(), Perioada(2026, luna=8), [_fact_rc(1000, 21)], {"R12_1": 1000, "R12_2": 210})
    assert "dublă numărare" in str(ei.value)


def test_beneficiar_fara_flag_NU_deriva_ci_deduce_normal():
    """MUTATIE inversa: aceeasi achizitie 21% FARA flag taxare_inversa -> deducere normala R22,
    NU rd.12/rd.25. Proba ca derivarea depinde de flag."""
    f = {"directie": "primita", "linii": [(1, 1000, 21)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f])
    assert res.R.get("R22_2") == 210 and "R12_1" not in res.R and "R25_1" not in res.R
