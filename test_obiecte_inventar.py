# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import obiecte_inventar as m

def test_prag():
    assert m.prag_mf(date(2026, 2, 24)) == Decimal("2500")
    assert m.prag_mf(date(2026, 2, 25)) == Decimal("5000")

def test_e_oi():
    assert m.e_obiect_inventar(4500, date(2026, 7, 1))
    assert not m.e_obiect_inventar(4500, date(2026, 1, 15))
    assert m.e_obiect_inventar(9000, durata_sub_1_an=True)

def test_achizitie():
    r = m.nota_achizitie(1200, cota_tva=21)
    assert ("303", "401", Decimal("1200.00")) in r["linii"]
    assert ("4426", "401", Decimal("252.00")) in r["linii"]

def test_dare_folosinta():
    r = m.nota_dare_folosinta(1200)
    assert ("603", "303", Decimal("1200.00")) in r["linii"]
    assert ("8035", "891", Decimal("1200.00")) in r["linii"]

def test_scoatere():
    assert m.nota_scoatere_uz(1200)["linii"] == [("891", "8035", Decimal("1200.00"))]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_achizitie(0, cota_tva=21)
