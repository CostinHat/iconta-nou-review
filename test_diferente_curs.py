# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import diferente_curs as m

def test_creanta_castig():
    d = m.diferenta(1000, "4.97", "5.02", "creanta")
    assert d == {"diferenta": Decimal("50.00"), "cont": "765", "sens": "favorabila"}

def test_creanta_pierdere():
    d = m.diferenta(1000, "5.02", "4.97", "creanta")
    assert d["cont"] == "665" and d["diferenta"] == Decimal("50.00")

def test_datorie_curs_creste_pierdere():
    d = m.diferenta(1000, "4.97", "5.02", "datorie")
    assert d["cont"] == "665"

def test_datorie_curs_scade_castig():
    d = m.diferenta(1000, "5.02", "4.97", "datorie")
    assert d["cont"] == "765"

def test_fara_diferenta():
    d = m.diferenta(1000, "5.00", "5.00", "disponibil")
    assert d["diferenta"] == Decimal("0.00") and d["cont"] is None

def test_tip_gresit():
    with pytest.raises(ValueError, match="tip"):
        m.diferenta(1, 1, 1, "altceva")

def test_nota_incasare_creanta_castig():
    r = m.nota_decontare(1000, "4.97", "5.02", "creanta", "4111")
    assert r["lei_evidenta"] == Decimal("4970.00")
    assert ("5124", "4111", Decimal("4970.00")) in r["linii"]
    assert ("5124", "765", Decimal("50.00")) in r["linii"]

def test_nota_plata_datorie_pierdere():
    r = m.nota_decontare(2000, "4.97", "5.02", "datorie", "401")
    assert ("401", "5124", Decimal("9940.00")) in r["linii"]
    assert ("665", "5124", Decimal("100.00")) in r["linii"]

def test_reevaluare_creanta():
    r = m.reevaluare_sold(500, "4.97", "5.02", "creanta", "4111")
    assert r["linie"] == ("4111", "765", Decimal("25.00"))

def test_reevaluare_datorie():
    r = m.reevaluare_sold(500, "4.97", "5.02", "datorie", "401")
    assert r["linie"] == ("665", "401", Decimal("25.00"))

def test_reevaluare_fara_dif():
    assert m.reevaluare_sold(500, "5.00", "5.00", "creanta", "4111") is None
