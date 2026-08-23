# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import perisabilitati as m

def test_in_limita():
    r = m.calcul(1000, "1.25", 10, cota_tva=21)
    assert r["limita"] == Decimal("12.50")
    assert r["deductibil"] == Decimal("10.00")
    assert r["nedeductibil"] == Decimal("0.00")
    assert r["ajustare_tva"] == Decimal("0.00")
    assert r["linii"] == [("607", "371", Decimal("10.00"))]

def test_peste_limita():
    r = m.calcul(1000, "1.25", 30, cota_tva=21)
    assert r["deductibil"] == Decimal("12.50")
    assert r["nedeductibil"] == Decimal("17.50")
    assert ("635", "4426", Decimal("3.68")) in r["linii"]

def test_degradare_dovedita_fara_ajustare():
    r = m.calcul(1000, "1.25", 30, degradare_dovedita_distrusa=True, cota_tva=21)
    assert r["ajustare_tva"] == Decimal("0.00")
    assert len(r["linii"]) == 2

def test_cont_stoc():
    r = m.calcul(1000, "0.5", 3, cont_stoc="301", cota_tva=21)
    assert r["linii"][0][1] == "301"

def test_invalid():
    with pytest.raises(ValueError):
        m.calcul(0, 1, 1, cota_tva=21)
