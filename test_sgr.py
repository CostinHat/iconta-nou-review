# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import sgr as m

def test_achizitie_pe_ambalaje():
    r = m.nota_garantie_achizitie(nr_ambalaje=100)
    assert r["linii"] == [("461", "401", Decimal("50.00"))]

def test_vanzare():
    r = m.nota_garantie_vanzare(suma=25)
    assert r["linii"] == [("5311", "462", Decimal("25.00"))]

def test_restituire():
    r = m.nota_restituire_consumator(nr_ambalaje=10)
    assert r["linii"] == [("461", "5311", Decimal("5.00"))]

def test_autofactura():
    r = m.nota_autofactura_returo(500, 120, cota_tva=21)
    assert ("5121", "461", Decimal("500.00")) in r["linii"]
    assert ("4111", "708", Decimal("120.00")) in r["linii"]
    assert ("4111", "4427", Decimal("25.20")) in r["linii"]

def test_autofactura_doar_garantii():
    r = m.nota_autofactura_returo(500, cota_tva=21)
    assert len(r["linii"]) == 1

def test_virare():
    assert m.nota_virare_garantii(300)["linii"] == [("462", "401", Decimal("300.00"))]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_garantie_achizitie()
