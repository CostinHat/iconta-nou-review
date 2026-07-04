# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import retete

L = [{"articol_id": 1, "cantitate": "0.150", "cmp": "20"},   # 150g carne @20/kg
     {"articol_id": 2, "cantitate": "0.100", "cmp": "5"}]    # 100g garnitura @5/kg

def test_consum_10_portii():
    r = retete.consum_pe_portii(L, 10)
    assert r["linii"][0]["cantitate"] == Decimal("1.500")
    assert r["linii"][0]["valoare"] == Decimal("30.00")
    assert r["linii"][1]["valoare"] == Decimal("5.00")
    assert r["cost_total"] == Decimal("35.00")

def test_portii_invalide():
    with pytest.raises(ValueError):
        retete.consum_pe_portii(L, 0)

def test_food_cost():
    r = retete.food_cost(L, 14)
    assert r["cost_portie"] == Decimal("3.50")
    assert r["food_cost_pct"] == Decimal("25.0")

def test_food_cost_pret_zero():
    r = retete.food_cost(L, 0)
    assert r["food_cost_pct"] is None
