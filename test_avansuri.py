# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import avansuri as m

def test_avans_platit_stocuri():
    r = m.nota_avans_platit(1000)
    assert ("4091", "401", Decimal("1000.00")) in r["linii"]
    assert ("4426", "401", Decimal("210.00")) in r["linii"]

def test_avans_platit_imobilizari():
    r = m.nota_avans_platit(30000, 21, "imobilizari")
    assert r["cont_avans"] == "4093"

def test_destinatie_gresita():
    with pytest.raises(ValueError, match="destinatie"):
        m.nota_avans_platit(1, 21, "altceva")

def test_regularizare_platit():
    r = m.nota_regularizare_avans_platit(1000)
    assert ("401", "4091", Decimal("1000.00")) in r["linii"]
    assert ("401", "4426", Decimal("210.00")) in r["linii"]

def test_avans_incasat():
    r = m.nota_avans_incasat(5000, 11)
    assert ("4111", "419", Decimal("5000.00")) in r["linii"]
    assert ("4111", "4427", Decimal("550.00")) in r["linii"]

def test_regularizare_incasat():
    r = m.nota_regularizare_avans_incasat(5000, 11)
    assert ("419", "4111", Decimal("5000.00")) in r["linii"]
    assert ("4427", "4111", Decimal("550.00")) in r["linii"]

def test_cota_zero():
    r = m.nota_avans_incasat(5000, 0)
    assert len(r["linii"]) == 1
