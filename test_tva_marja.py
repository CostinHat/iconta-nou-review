# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import tva_marja as m

def test_exemplu_oficial_recalculat_21():
    # vanzare 98000, cost 88500 -> marja 9500; la 21%: TVA=9500*21/121=1648.76
    r = m.vanzare_marja(98000, 88500, 21)
    assert r["marja_bruta"] == Decimal("9500.00")
    assert r["tva"] == Decimal("1648.76")
    assert r["marja_neta"] == Decimal("7851.24")

def test_marja_negativa():
    r = m.vanzare_marja(1000, 1200, 21)
    assert r["tva"] == Decimal("0.00") and "reporteaza" in r["nota"]

def test_pret_invalid():
    with pytest.raises(ValueError):
        m.vanzare_marja(0, 100, cota=21)
