# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import deconturi as m

def test_plafon_intern():
    r = m.plafon_diurna(80, 10, 5000, 21)
    assert r["limita_2_5x"] == Decimal("57.50")
    assert r["plafon_zi"] == Decimal("57.50")
    assert r["neimpozabil"] == Decimal("575.00")
    assert r["impozabil"] == Decimal("225.00")

def test_plafon_extern():
    r = m.plafon_diurna(437.5, 24, 4100, 20, diurna_bugetara=35, curs=5)
    assert r["limita_2_5x"] == Decimal("437.50")
    assert r["limita_3_salarii"] == Decimal("615.00")
    assert r["impozabil"] == Decimal("0.00")

def test_plafon_3_salarii_mai_mic():
    r = m.plafon_diurna(700, 5, 4050, 18, diurna_bugetara=300)
    assert r["plafon_zi"] == Decimal("675.00")
    assert r["impozabil"] == Decimal("125.00")

def test_avans():
    assert m.nota_avans(1000)["linii"] == [("542", "5311", Decimal("1000.00"))]
    assert m.nota_avans(1000, "banca")["linii"] == [("542", "5121", Decimal("1000.00"))]

def test_decont_cu_rest():
    r = m.nota_decont(1000, diurna=287.50, transport=200, cazare=400)
    assert ("625", "542", Decimal("887.50")) in r["linii"]
    assert ("5311", "542", Decimal("112.50")) in r["linii"]

def test_decont_cu_plata_diferentei():
    r = m.nota_decont(500, diurna=287.50, transport=200, cazare=400)
    assert ("542", "5311", Decimal("387.50")) in r["linii"]

def test_decont_cu_tva():
    r = m.nota_decont(0, diurna=100, transport=0, cazare=1000, cota_tva=21)
    assert ("4426", "542", Decimal("210.00")) in r["linii"]

def test_invalid():
    with pytest.raises(ValueError):
        m.plafon_diurna(0, 1, 1, 1)
