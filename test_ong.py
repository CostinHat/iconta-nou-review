# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import ong as m

def test_cotizatie():
    r = m.nota_venit(500)
    assert r["linii"] == [("5311", "731", Decimal("500.00"))]

def test_donatie_banca():
    r = m.nota_venit(10000, "donatie", "banca")
    assert r["linii"] == [("5121", "733", Decimal("10000.00"))]

def test_ocazional():
    assert m.nota_venit(2000, "ocazional")["cont_venit"] == "738"

def test_fel_gresit():
    with pytest.raises(ValueError, match="fel"):
        m.nota_venit(1, "altceva")

def test_scutire_sub_plafon():
    r = m.scutire_economica(50000, 1000000, 5)
    assert r["plafon"] == Decimal("75000.00")
    assert r["scutit"] == Decimal("50000.00")
    assert r["impozabil"] == Decimal("0.00")

def test_scutire_peste_plafon():
    r = m.scutire_economica(100000, 1000000, 5)
    assert r["scutit"] == Decimal("75000.00")
    assert r["impozabil"] == Decimal("25000.00")
    assert r["impozit_estimat"] == Decimal("4000.00")

def test_plafon_10pct_mai_mic():
    r = m.scutire_economica(20000, 100000, 5)
    assert r["plafon"] == Decimal("10000.00")
    assert r["impozabil"] == Decimal("10000.00")
