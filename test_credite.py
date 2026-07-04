# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import credite as m

def test_primire_lung():
    assert m.nota_primire(75000)["linii"] == [("5121", "1621", Decimal("75000.00"))]

def test_primire_scurt():
    assert m.nota_primire(36000, "scurt")["linii"] == [("5121", "5191", Decimal("36000.00"))]

def test_tip_gresit():
    with pytest.raises(ValueError, match="tip"):
        m.nota_primire(1, "mediu")

def test_dobanda_angajata():
    assert m.nota_dobanda_angajata(6833)["linii"] == [("666", "1682", Decimal("6833.00"))]
    assert m.nota_dobanda_angajata(150, "scurt")["linii"] == [("666", "5198", Decimal("150.00"))]

def test_plata_completa_lung():
    r = m.nota_plata(6000, 900, 50)
    assert ("1621", "5121", Decimal("6000.00")) in r["linii"]
    assert ("1682", "5121", Decimal("900.00")) in r["linii"]
    assert ("627", "5121", Decimal("50.00")) in r["linii"]

def test_plata_dobanda_directa():
    r = m.nota_plata(0, 150, 0, "scurt", dobanda_angajata=False)
    assert r["linii"] == [("666", "5121", Decimal("150.00"))]

def test_restanta():
    assert m.nota_restanta(6000)["linii"] == [("1621", "1622", Decimal("6000.00"))]
    assert m.nota_restanta(6000, "scurt")["linii"] == [("5191", "5192", Decimal("6000.00"))]

def test_garantie():
    assert m.nota_garantie(200000, "primita")["linii"] == [("8021", "891", Decimal("200000.00"))]
    assert m.nota_garantie(200000, "acordata", "eliberare")["linii"] == [("891", "8011", Decimal("200000.00"))]
