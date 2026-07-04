# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import sponsorizari as m

def test_plafon():
    p = m.plafon_credit(4000000, 100000)
    assert p["limita_ca"] == Decimal("30000.00")
    assert p["limita_impozit"] == Decimal("20000.00")
    assert p["plafon"] == Decimal("20000.00")

def test_credit_partial():
    r = m.credit_sponsorizare(4000000, 100000, 12000)
    assert r["credit"] == Decimal("12000.00")
    assert r["redirectionabil_d177"] == Decimal("8000.00")

def test_credit_peste_plafon():
    r = m.credit_sponsorizare(4000000, 100000, 25000)
    assert r["credit"] == Decimal("20000.00")
    assert r["redirectionabil_d177"] == Decimal("0.00")

def test_micro_fara_facilitate():
    r = m.credit_sponsorizare(1000000, 10000, 5000, tip_impozit="micro")
    assert r["credit"] == Decimal("0.00") and "OUG 115/2023" in r["nota"]

def test_beneficiar_neinscris():
    r = m.credit_sponsorizare(4000000, 100000, 5000, beneficiar_in_registru=False)
    assert r["credit"] == Decimal("0.00") and "NEINSCRIS" in r["nota"]

def test_nota():
    assert m.nota_sponsorizare(5000)["linii"] == [("6582", "401", Decimal("5000.00"))]
    assert m.nota_sponsorizare(5000, "plata")["linii"] == [("6582", "5121", Decimal("5000.00"))]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_sponsorizare(0)
