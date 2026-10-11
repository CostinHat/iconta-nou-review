# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import bacsis as m

def test_incasare_card():
    r = m.nota_incasare(100)
    assert ("461", "462", Decimal("100.00")) in r["linii"]
    assert ("5121", "461", Decimal("100.00")) in r["linii"]

def test_incasare_numerar():
    r = m.nota_incasare(100, "numerar")
    assert ("5311", "461", Decimal("100.00")) in r["linii"]

def test_distribuire():
    r = m.nota_distribuire(100, "2026-10-11")          # data notei: cota CF art.64 alin.(1) din registru (R3)
    assert ("462", "446", Decimal("10.00")) in r["linii"]
    assert ("462", "5121", Decimal("90.00")) in r["linii"]
    assert r["impozit"] == Decimal("10.00") and r["net"] == Decimal("90.00")

def test_distribuire_numerar():
    r = m.nota_distribuire(250, "2026-10-11", "casa")
    assert ("462", "5311", Decimal("225.00")) in r["linii"]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_incasare(0)
