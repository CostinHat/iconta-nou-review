# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import provizioane as m

def test_deduct_30():
    p, t = m.deductibilitate_creanta(300, False, False)
    assert p == 30 and "270" in t

def test_deduct_100_faliment():
    p, t = m.deductibilitate_creanta(100, False, False, faliment_declarat=True)
    assert p == 100

def test_deduct_0_garantata():
    p, _ = m.deductibilitate_creanta(400, True, False)
    assert p == 0

def test_deduct_0_afiliata():
    p, _ = m.deductibilitate_creanta(400, False, True)
    assert p == 0

def test_deduct_0_sub_270():
    p, _ = m.deductibilitate_creanta(100, False, False)
    assert p == 0

def test_ajustare_creanta():
    assert m.nota_ajustare_creanta(5000)["linii"] == [("6814", "491", Decimal("5000.00"))]
    assert m.nota_ajustare_creanta(5000, "reluare")["linii"] == [("491", "7814", Decimal("5000.00"))]

def test_provizion_garantii():
    r = m.nota_provizion(10000, "garantii")
    assert r["linii"] == [("6812", "1512", Decimal("10000.00"))] and r["deductibil"]

def test_provizion_litigii_nedeductibil():
    r = m.nota_provizion(10000, "litigii", "reluare")
    assert r["linii"] == [("1511", "7812", Decimal("10000.00"))] and not r["deductibil"]

def test_ajustare_stoc():
    r = m.nota_ajustare_stoc(2000, "397")
    assert r["linii"] == [("6814", "397", Decimal("2000.00"))] and not r["deductibil"]

def test_stoc_cont_gresit():
    with pytest.raises(ValueError, match="39x"):
        m.nota_ajustare_stoc(1, "491")
