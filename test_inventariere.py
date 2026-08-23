# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import inventariere as m

def test_plus_marfa():
    assert m.nota_plus(500)["linii"] == [("371", "607", Decimal("500.00"))]

def test_plus_produse():
    assert m.nota_plus(500, "345")["linii"] == [("345", "711", Decimal("500.00"))]

def test_plus_mf():
    assert m.nota_plus_mf(3000)["linii"] == [("2131", "4754", Decimal("3000.00"))]

def test_minus_neimputabil_neasigurat():
    r = m.nota_minus(1000, cota_tva=21)
    assert ("607", "371", Decimal("1000.00")) in r["linii"]
    assert ("635", "4426", Decimal("210.00")) in r["linii"]

def test_minus_neimputabil_distrus():
    r = m.nota_minus(1000, asigurat_sau_distrus=True, cota_tva=21)
    assert len(r["linii"]) == 1

def test_minus_imputabil_salariat():
    r = m.nota_minus(1000, imputabil=True, valoare_imputare=1200, cota_tva=21)
    assert ("607", "371", Decimal("1000.00")) in r["linii"]
    assert ("4282", "7581", Decimal("1200.00")) in r["linii"]
    assert ("4282", "4427", Decimal("252.00")) in r["linii"]
    assert not any(l[0] == "635" for l in r["linii"])

def test_minus_imputabil_tert():
    r = m.nota_minus(1000, imputabil=True, vinovat="tert", cota_tva=21)
    assert ("461", "7581", Decimal("1000.00")) in r["linii"]

def test_casare():
    r = m.nota_casare_mf(6500, 4833.33)
    assert ("2813", "2131", Decimal("4833.33")) in r["linii"]
    assert ("6583", "2131", Decimal("1666.67")) in r["linii"]

def test_casare_amortizat_integral():
    r = m.nota_casare_mf(6500, 6500)
    assert len(r["linii"]) == 1

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_plus(100, "999")
