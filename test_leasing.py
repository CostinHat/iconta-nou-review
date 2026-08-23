# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import leasing as m

def test_primire():
    r = m.nota_primire_financiar(120000, 7110)
    assert ("2133", "167", Decimal("120000.00")) in r["linii"]
    assert ("8051", "891", Decimal("7110.00")) in r["linii"]

def test_primire_fara_dobanda():
    r = m.nota_primire_financiar(50000, 0)
    assert len(r["linii"]) == 1

def test_primire_invalida():
    with pytest.raises(ValueError):
        m.nota_primire_financiar(0, 100)

def test_rata():
    r = m.nota_rata_financiar(1000, 150, 20, cota_tva=21)
    assert ("167", "404", Decimal("1000.00")) in r["linii"]
    assert ("666", "404", Decimal("150.00")) in r["linii"]
    assert ("628", "404", Decimal("20.00")) in r["linii"]
    assert ("4426", "404", Decimal("245.70")) in r["linii"]
    assert ("891", "8051", Decimal("150.00")) in r["linii"]

def test_rata_doar_capital():
    r = m.nota_rata_financiar(1000, cota_tva=21)
    assert len(r["linii"]) == 2

def test_reziduala():
    r = m.nota_reziduala(278.15, cota_tva=21)
    assert ("167", "404", Decimal("278.15")) in r["linii"]
    assert r["tva"] == Decimal("58.41")

def test_operational():
    r = m.nota_rata_operational(2500, cota_tva=21)
    assert ("612", "401", Decimal("2500.00")) in r["linii"]
    assert ("4426", "401", Decimal("525.00")) in r["linii"]
