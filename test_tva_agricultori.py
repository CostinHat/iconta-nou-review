# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import tva_agricultori as m

def test_compensatie_8():
    r = m.compensatie(3000)
    assert r["compensatie"] == Decimal("240.00")
    assert r["total"] == Decimal("3240.00")

def test_compensatie_rotunjire():
    r = m.compensatie(1234.56)
    assert r["compensatie"] == Decimal("98.76")

def test_compensatie_invalida():
    with pytest.raises(ValueError):
        m.compensatie(0)

def test_achizitie_in_registru():
    r = m.achizitie_de_la_agricultor(3000, True)
    assert r["compensatie"] == Decimal("240.00")

def test_achizitie_neinscris():
    with pytest.raises(ValueError, match="NU este deductibila"):
        m.achizitie_de_la_agricultor(3000, False)
