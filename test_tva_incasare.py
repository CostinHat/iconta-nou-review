# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import tva_incasare as t

def test_suta_marita_21():
    # incasare 1210 la cota 21% -> TVA 210
    assert t.tva_din_incasare(1210, 21) == Decimal("210.00")

def test_suta_marita_11():
    assert t.tva_din_incasare(111, 11) == Decimal("11.00")

def test_partiala():
    # factura 1210 (21%), incasare partiala 500 -> TVA 86.78
    assert t.tva_din_incasare(500, 21) == Decimal("86.78")

def test_alocari_pe_cote():
    r = t.tva_exigibil_alocari([{"suma": 1210, "cota_tva": 21},
                                {"suma": 111, "cota_tva": 11},
                                {"suma": 121, "cota_tva": 21}])
    assert r["total"] == Decimal("242.00")
    assert {"cota": "21", "tva": "231.00"} in r["linii"]

def test_suma_negativa():
    with pytest.raises(ValueError):
        t.tva_din_incasare(0, 21)

def test_plafon():
    assert t.plafon_la("2026-02-15") == Decimal("4500000")
    assert t.plafon_la("2026-07-04") == Decimal("5000000")
    assert t.plafon_la("2027-01-01") == Decimal("5500000")
