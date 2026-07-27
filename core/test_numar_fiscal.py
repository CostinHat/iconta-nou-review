# -*- coding: utf-8 -*-
"""Teste core.common.numar_fiscal + garda pe generatoarele de declaratii.

Fondul: o valoare stricata NU trebuie sa devina tacit 0 intr-o declaratie depusa
la ANAF. Absenta (None/"") e legitima si ramane 0; invalidul e eroare.
"""
import pytest
from decimal import Decimal
from core.numere import numar_fiscal


@pytest.mark.parametrize("v,astept", [
    (None, 0), ("", 0), ("   ", 0), (0, 0), ("0", 0),
    (12, 12), ("12", 12), (12.5, Decimal("12.5")), ("12.5", Decimal("12.5")),
    (Decimal("3.33"), Decimal("3.33")), (-5, -5),
])
def test_valori_bune(v, astept):
    assert numar_fiscal(v) == astept


@pytest.mark.parametrize("v", ["abc", "12,5", float("nan"), float("inf"),
                               [], {"a": 1}, True, False, object()])
def test_valori_invalide_arunca(v):
    """Inclusiv '12,5' - virgula zecimala romaneasca, plauzibila si periculoasa:
    inainte iesea 0 lei fara niciun semnal."""
    with pytest.raises(ValueError):
        numar_fiscal(v)


def test_mesajul_poarta_campul_si_valoarea():
    with pytest.raises(ValueError) as e:
        numar_fiscal("12,5", "baza impozabila")
    m = str(e.value)
    assert "baza impozabila" in m and "12,5" in m


def test_generatoarele_nu_mai_inghit_gunoiul():
    """Garda: cele trei functii de rotunjire din D112/D300/D390 trebuie sa ARUNCE
    pe valoare invalida, ca d205._i / d101._i. Daca cineva reintroduce masca,
    testul pica."""
    from core.d112 import _d112int
    from core.d300 import _int as d300_int
    from core.d390 import _int as d390_int
    for nume, fn in (("d112", _d112int), ("d300", d300_int), ("d390", d390_int)):
        assert fn(None) == 0, "%s: absenta trebuie sa ramana 0" % nume
        assert fn("12") == 12, "%s: valoarea buna trebuie sa treaca" % nume
        with pytest.raises(ValueError):
            fn("12,5")
        with pytest.raises(ValueError):
            fn("abc")


def test_d112_pastreaza_rotunjirea_aritmetica():
    """Regresie: reparatia mastii NU are voie sa atinga rotunjirea (ANAF cere
    aritmetica, nu bancara - dovedit prin validator, regula A91b)."""
    from core.d112 import _d112int
    assert _d112int(112.5) == 113
    assert _d112int(112.4) == 112
