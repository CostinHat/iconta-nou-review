# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import decontari_asociati as m

def test_cota():
    assert m.cota_dividend(date(2025, 12, 31)) == Decimal("10")
    assert m.cota_dividend(date(2026, 1, 1)) == Decimal("16")

def test_anual():
    r = m.nota_dividend(120000, date(2026, 7, 4))
    assert ("1171", "457", Decimal("120000.00")) in r["linii"]
    assert ("457", "446", Decimal("19200.00")) in r["linii"]
    assert ("457", "5121", Decimal("100800.00")) in r["linii"]

def test_interimar_fara_plata():
    r = m.nota_dividend(50000, date(2026, 7, 4), interimar=True, cu_plata=False)
    assert ("463", "456", Decimal("50000.00")) in r["linii"]
    assert ("456", "446", Decimal("8000.00")) in r["linii"]
    assert len(r["linii"]) == 2

def test_regularizare_normala():
    r = m.nota_regularizare_interimar(50000, 80000)
    assert ("1171", "457", Decimal("80000.00")) in r["linii"]
    assert ("457", "463", Decimal("50000.00")) in r["linii"]
    assert r["exces_de_restituit"] == Decimal("0.00")

def test_regularizare_exces():
    r = m.nota_regularizare_interimar(150000, 140000)
    assert ("457", "463", Decimal("140000.00")) in r["linii"]
    assert ("5121", "456", Decimal("10000.00")) in r["linii"]

def test_imprumut():
    assert m.nota_imprumut_asociat(20000)["linii"] == [("5121", "4551", Decimal("20000.00"))]
    r = m.nota_imprumut_asociat(20000, "restituire", dobanda=1000)
    assert ("4551", "5121", Decimal("20000.00")) in r["linii"]
    assert ("666", "4551", Decimal("1000.00")) in r["linii"]
    assert ("4551", "446", Decimal("100.00")) in r["linii"]
    assert ("4551", "5121", Decimal("900.00")) in r["linii"]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_dividend(0)
