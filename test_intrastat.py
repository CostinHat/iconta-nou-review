# -*- coding: utf-8 -*-
from decimal import Decimal
from core import intrastat as m

def test_partener_ue():
    assert m.e_partener_ue("DE123456789")
    assert m.e_partener_ue(" hu 8899 ")
    assert not m.e_partener_ue("RO34142700")
    assert not m.e_partener_ue("US123")
    assert not m.e_partener_ue(None)

def test_sub_prag():
    r = m.analiza_flux({1: 100000, 2: 200000})
    assert r["status"] == "sub_prag" and r["cumulat"] == Decimal("300000")
    assert r["luna_depasirii"] is None

def test_atentie_80():
    r = m.analiza_flux({1: 500000, 2: 350000})
    assert r["status"] == "atentie" and r["procent"] == Decimal("85.0")

def test_depasit_luna_corecta():
    r = m.analiza_flux({1: 600000, 2: 300000, 3: 200000, 4: 50000})
    assert r["status"] == "depasit"
    assert r["luna_depasirii"] == 3
    assert r["cumulat"] == Decimal("1150000")

def test_exact_prag_nu_depaseste():
    r = m.analiza_flux({1: 1000000})
    assert r["status"] == "atentie" and r["luna_depasirii"] is None
