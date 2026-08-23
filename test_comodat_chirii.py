# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import comodat_chirii as m

def test_comodat():
    assert m.nota_comodat(50000)["linii"] == [("8038", "891", Decimal("50000.00"))]
    assert m.nota_comodat(50000, "restituire")["linii"] == [("891", "8038", Decimal("50000.00"))]

def test_chirie_pj():
    r = m.nota_chirie_platita(3000, cota_tva=21)
    assert ("612", "401", Decimal("3000.00")) in r["linii"]
    assert ("4426", "401", Decimal("630.00")) in r["linii"]

def test_chirie_pf():
    r = m.nota_chirie_platita(3000, proprietar="pf", cota_tva=21)
    assert r["linii"] == [("612", "462", Decimal("3000.00"))]
    assert "Declaratia Unica" in r["nota"]

def test_chirie_incasata():
    r = m.nota_chirie_incasata(3000, cota_tva=21)
    assert ("4111", "706", Decimal("3000.00")) in r["linii"]
    assert ("4111", "4427", Decimal("630.00")) in r["linii"]

def test_refacturare():
    r = m.nota_refacturare(1000, 400, cota_tva=21)
    assert ("605", "401", Decimal("600.00")) in r["primire"]
    assert ("4426", "401", Decimal("126.00")) in r["primire"]
    assert ("461", "401", Decimal("484.00")) in r["primire"]
    assert ("4111", "708", Decimal("400.00")) in r["emitere"]
    assert ("4111", "4427", Decimal("84.00")) in r["emitere"]

def test_refacturare_totala():
    r = m.nota_refacturare(1000, 1000, cota_tva=21)
    assert r["primire"] == [("461", "401", Decimal("1210.00"))]

def test_invalid():
    with pytest.raises(ValueError, match="refacturata"):
        m.nota_refacturare(1000, 1500, cota_tva=21)
