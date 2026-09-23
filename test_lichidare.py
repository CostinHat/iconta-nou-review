# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import lichidare as m

def test_vanzare_activ():
    r = m.nota_vanzare_activ(2000, 6500, 4833.33, cota_tva=21)
    assert ("461", "7583", Decimal("2000.00")) in r["linii"]
    assert ("461", "4427", Decimal("420.00")) in r["linii"]
    assert ("2813", "2131", Decimal("4833.33")) in r["linii"]
    assert ("6583", "2131", Decimal("1666.67")) in r["linii"]

def test_partaj():
    r = m.partaj(200, 40, 160, date(2026, 7, 4))
    assert ("1012", "456", Decimal("200.00")) in r["linii"]
    assert ("1061", "456", Decimal("40.00")) in r["linii"]
    assert ("1171", "456", Decimal("160.00")) in r["linii"]
    assert ("456", "446", Decimal("20.00")) in r["linii"]   # 10% FIX (CF art.97 alin.5), NU cota dividendelor
    assert ("456", "5121", Decimal("380.00")) in r["linii"]  # net = 200 + 200 - 20
    assert r["castig_impozabil"] == Decimal("200.00")

def test_partaj_doar_capital():
    r = m.partaj(200, 0, 0)
    assert r["impozit"] == Decimal("0.00")
    assert r["net_asociat"] == Decimal("200.00")

def test_cota_lichidare_10pct_fix():
    # castigul din lichidare la asociat PF = 10% FIX (CF art.97 alin.5), pe orice an - NU cota dividendelor
    assert m.partaj(0, 0, 100, date(2025, 6, 1))["impozit"] == Decimal("10.00")
    assert m.partaj(0, 0, 100, date(2026, 6, 1))["impozit"] == Decimal("10.00")   # 2026: tot 10%, nu 16%

def test_invalid():
    with pytest.raises(ValueError):
        m.partaj(0)
