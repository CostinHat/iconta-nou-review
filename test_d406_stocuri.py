# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import d406_stocuri as m

ART = {"id": 7, "denumire": "Faina <tip> 650 & co", "um": "kg", "cont_stoc": "371"}
MIS = [
    {"data": date(2026, 1, 10), "tip": "intrare", "cantitate": 100, "valoare": 500},
    {"data": date(2026, 2, 5), "tip": "iesire", "cantitate": 30, "valoare": 150},
    {"data": date(2026, 3, 20), "tip": "intrare", "cantitate": 50, "valoare": 300},
    {"data": date(2026, 4, 1), "tip": "iesire", "cantitate": 20, "valoare": 110},
]

def test_solduri_perioada():
    s = m.solduri(MIS, date(2026, 3, 1), date(2026, 3, 31))
    assert s["open_q"] == Decimal("70.000") and s["open_v"] == Decimal("350.00")
    assert s["close_q"] == Decimal("120.000") and s["close_v"] == Decimal("650.00")
    assert s["pret"] == Decimal("5.4167")

def test_sold_zero():
    mis = [{"data": date(2026, 1, 1), "tip": "intrare", "cantitate": 10, "valoare": 100},
           {"data": date(2026, 1, 5), "tip": "iesire", "cantitate": 10, "valoare": 100}]
    s = m.solduri(mis, date(2026, 1, 1), date(2026, 1, 31))
    assert s["close_q"] == Decimal("0.000") and s["pret"] == Decimal("0")

def test_stoc_negativ():
    mis = [{"data": date(2026, 1, 5), "tip": "iesire", "cantitate": 5, "valoare": 25}]
    with pytest.raises(ValueError, match="negativ"):
        m.solduri(mis, date(2026, 1, 1), date(2026, 1, 31))

def test_xml_structura_si_escape():
    x = m.xml_physical_stock([(ART, MIS)], date(2026, 3, 1), date(2026, 3, 31), "RO12345")
    for tag in ("WarehouseID", "ProductCode", "OwnerID", "UnitPrice",
                "OpeningStockQuantity", "ClosingStockValue", "StockCharacteristics"):
        assert f"<nsSAFT:{tag}>" in x
    assert "&lt;tip&gt;" in x and "&amp;" in x

def test_fara_miscari():
    with pytest.raises(ValueError, match="niciun articol"):
        m.xml_physical_stock([(ART, [])], date(2026, 1, 1), date(2026, 1, 31), "RO1")
