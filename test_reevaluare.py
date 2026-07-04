# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import reevaluare as m

def test_crestere_simpla():
    r = m.nota_reevaluare(100000, 40000, 90000, "212", "2812")
    assert ("2812", "212", Decimal("40000.00")) in r["linii"]
    assert ("212", "105", Decimal("30000.00")) in r["linii"]
    assert r["valoare_neta"] == Decimal("60000.00")

def test_crestere_cu_655_anterior():
    r = m.nota_reevaluare(100000, 40000, 90000, "212", "2812",
                          pierdere_655_anterioara=10000)
    assert ("212", "755", Decimal("10000.00")) in r["linii"]
    assert ("212", "105", Decimal("20000.00")) in r["linii"]

def test_scadere_cu_105():
    r = m.nota_reevaluare(100000, 40000, 45000, "212", "2812", sold_105_activ=10000)
    assert ("105", "212", Decimal("10000.00")) in r["linii"]
    assert ("655", "212", Decimal("5000.00")) in r["linii"]

def test_scadere_fara_105():
    r = m.nota_reevaluare(100000, 40000, 50000, "212", "2812")
    assert ("655", "212", Decimal("10000.00")) in r["linii"]

def test_fara_diferenta():
    r = m.nota_reevaluare(100000, 40000, 60000, "212", "2812")
    assert len(r["linii"]) == 1

def test_amortizare_zero():
    r = m.nota_reevaluare(100000, 0, 120000, "211", "2811")
    assert r["linii"] == [("211", "105", Decimal("20000.00"))]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_reevaluare(100, 200, 50, "212", "2812")

def test_surplus():
    assert m.nota_realizare_surplus(5000)["linii"] == [("105", "1175", Decimal("5000.00"))]
