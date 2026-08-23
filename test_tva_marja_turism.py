# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import tva_marja_turism as m

def test_regim_default_special():
    assert m.determina_regim("PF", ["RO"]) == "special"
    assert m.determina_regim("PJ", ["UE"]) == "special"

def test_regim_normal_permis_doar_pj_ro():
    assert m.determina_regim("PJ", ["RO", "RO"], optiune_normal=True) == "normal"

def test_regim_normal_interzis_pf():
    with pytest.raises(ValueError, match="lit. a"):
        m.determina_regim("PF", ["RO"], optiune_normal=True)

def test_regim_normal_interzis_extern():
    with pytest.raises(ValueError, match="lit. b"):
        m.determina_regim("PJ", ["RO", "UE"], optiune_normal=True)

def test_regim_intermediar_prioritar():
    assert m.determina_regim("PF", ["UE"], intermediar=True) == "intermediar"

def test_special_simplu_21():
    r = m.marja_turism_special(12100, 10000, cota=21)
    assert r["marja_bruta"] == Decimal("2100.00")
    assert r["tva"] == Decimal("364.46")
    assert r["marja_neta"] == Decimal("1735.54")

def test_special_marja_negativa():
    r = m.marja_turism_special(9000, 10000, cota=21)
    assert r["tva"] == Decimal("0.00") and "reporteaza" in r["nota"]

def test_special_split_non_ue():
    r = m.marja_turism_special(13000, 6000, 4000, cota=21)
    assert r["marja_scutita"] == Decimal("1200.00")
    assert r["marja_taxabila"] == Decimal("1800.00")
    assert r["tva"] == Decimal("312.40")
    assert r["marja_neta"] == Decimal("2687.60")

def test_special_integral_non_ue():
    r = m.marja_turism_special(5000, 0, 4000, cota=21)
    assert r["marja_scutita"] == Decimal("1000.00") and r["tva"] == Decimal("0.00")

def test_special_invalid():
    with pytest.raises(ValueError):
        m.marja_turism_special(0, 100, cota=21)

def test_normal_componente():
    r = m.marja_turism_normal([
        {"descriere": "cazare", "baza": 1000, "cota": 11},
        {"descriere": "transport", "baza": 500, "cota": 21},
    ])
    assert r["componente"][0]["tva"] == Decimal("110.00")
    assert r["total_tva"] == Decimal("215.00")
    assert r["total_factura"] == Decimal("1715.00")

def test_normal_gol():
    with pytest.raises(ValueError):
        m.marja_turism_normal([])

def test_intermediar_fara_tva_inclus():
    r = m.comision_intermediar(1000, cota=21)
    assert r["tva"] == Decimal("210.00") and r["total"] == Decimal("1210.00")

def test_intermediar_tva_inclus():
    r = m.comision_intermediar(1210, tva_inclus=True, cota=21)
    assert r["baza"] == Decimal("1000.00") and r["tva"] == Decimal("210.00")
