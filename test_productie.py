# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import productie as m

def test_obtinere_standard():
    r = m.nota_obtinere(10000)
    assert r["linii"] == [("345", "711", Decimal("10000.00"))]

def test_obtinere_nefavorabila():
    r = m.nota_obtinere(10000, 10800)
    assert ("348", "711", Decimal("800.00")) in r["linii"]
    assert r["diferenta"]["sens"] == "nefavorabila"

def test_obtinere_favorabila():
    r = m.nota_obtinere(10000, 9600)
    assert ("711", "348", Decimal("400.00")) in r["linii"]

def test_pic():
    assert m.nota_productie_in_curs(3000)["linii"] == [("331", "711", Decimal("3000.00"))]
    assert m.nota_productie_in_curs(3000, "reluare")["linii"] == [("711", "331", Decimal("3000.00"))]

def test_coeficient():
    assert m.coeficient_348(200, 800, 5000, 15000) == Decimal("0.050000")

def test_vanzare_cu_repartizare():
    r = m.nota_vanzare(8000, 5000, 21, "0.05")
    assert ("4111", "701", Decimal("8000.00")) in r["linii"]
    assert ("4111", "4427", Decimal("1680.00")) in r["linii"]
    assert ("711", "345", Decimal("5000.00")) in r["linii"]
    assert ("711", "348", Decimal("250.00")) in r["linii"]

def test_vanzare_coef_favorabil():
    r = m.nota_vanzare(8000, 5000, 21, "-0.02")
    assert ("348", "711", Decimal("100.00")) in r["linii"]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_obtinere(0)
