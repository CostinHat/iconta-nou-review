# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core.stocuri_cv import fisa_magazie, valoare_iesire

D = Decimal

def I(cant, pret, data="2026-07-01"):
    return {"tip": "intrare", "cantitate": cant, "pret_unitar": pret, "data": data}

def E(cant, data="2026-07-15"):
    return {"tip": "iesire", "cantitate": cant, "data": data}

def test_intrare_simpla():
    f = fisa_magazie([I(10, "5")])
    assert f[0]["sold_cantitate"] == D("10")
    assert f[0]["sold_valoare"] == D("50.00")
    assert f[0]["cmp"] == D("5.0000")

def test_cmp_dupa_doua_intrari():
    # 10 buc x5 + 10 buc x7 -> CMP 6
    f = fisa_magazie([I(10, "5"), I(10, "7")])
    assert f[-1]["cmp"] == D("6.0000")
    assert f[-1]["sold_valoare"] == D("120.00")

def test_iesire_la_cmp():
    f = fisa_magazie([I(10, "5"), I(10, "7"), E(5)])
    assert f[-1]["valoare"] == D("30.00")       # 5 x 6
    assert f[-1]["sold_cantitate"] == D("15")
    assert f[-1]["sold_valoare"] == D("90.00")

def test_golire_completa_fara_rest():
    f = fisa_magazie([I(3, "3.33"), E(3)])
    assert f[-1]["sold_cantitate"] == D("0")
    assert f[-1]["sold_valoare"] == D("0.00")   # fara rest de rotunjire
    assert f[-1]["cmp"] is None

def test_iesire_peste_stoc():
    with pytest.raises(ValueError):
        fisa_magazie([I(5, "2"), E(6)])

def test_iesire_din_stoc_gol():
    with pytest.raises(ValueError):
        fisa_magazie([E(1)])

def test_stoc_initial():
    f = fisa_magazie([E(4)], stoc_initial={"cantitate": 10, "valoare": 25})
    assert f[0]["valoare"] == D("10.00")        # 4 x 2.5
    assert f[0]["sold_valoare"] == D("15.00")

def test_cmp_se_recalculeaza_dupa_intrare():
    # OMFP 1802 pct. 96: CMP dupa fiecare intrare
    f = fisa_magazie([I(10, "10"), E(5), I(5, "16")])
    # dupa iesire: 5 buc x10=50; +5 x16=80 -> 130/10 = 13
    assert f[-1]["cmp"] == D("13.0000")

def test_valoare_iesire_noua():
    r = valoare_iesire([I(10, "5"), I(10, "7")], None, 8)
    assert r["valoare"] == D("48.00")
    assert r["cmp"] == D("6.0000")
    assert r["temei"].startswith("OMFP 1802")

def test_valoare_iesire_peste_stoc():
    with pytest.raises(ValueError):
        valoare_iesire([I(2, "1")], None, 3)

def test_cantitate_invalida():
    with pytest.raises(ValueError):
        fisa_magazie([I(0, "5")])
