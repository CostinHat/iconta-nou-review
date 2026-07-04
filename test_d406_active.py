# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import d406_active as m

MF = {"id": 1, "cod": "MF001", "denumire": "Laptop", "cont_imobilizare": "2131",
      "cont_amortizare": "2813", "valoare": 12000, "rezidual": 0, "dnf_luni": 24,
      "data_pif": date(2025, 3, 15), "metoda": "liniara", "activ": True}

def test_an_achizitie():
    v = m.calc_asset(MF, 2025)
    assert v["addition"] == Decimal("12000.00")
    assert v["cost_begin"] == Decimal("0.00")
    assert v["depr_period"] == Decimal("4500.00")
    assert v["book_end"] == Decimal("7500.00")

def test_an_urmator():
    v = m.calc_asset(MF, 2026)
    assert v["cost_begin"] == Decimal("12000.00")
    assert v["addition"] == Decimal("0.00")
    assert v["book_begin"] == Decimal("7500.00")
    assert v["depr_period"] == Decimal("6000.00")
    assert v["accum_depr"] == Decimal("10500.00")
    assert v["book_end"] == Decimal("1500.00")

def test_an_finalizare():
    v = m.calc_asset(MF, 2027)
    assert v["depr_period"] == Decimal("1500.00")
    assert v["accum_depr"] == Decimal("12000.00")
    assert v["book_end"] == Decimal("0.00")

def test_dupa_finalizare():
    v = m.calc_asset(MF, 2028)
    assert v["depr_period"] == Decimal("0.00")
    assert v["book_end"] == Decimal("0.00")

def test_rezidual():
    mf = dict(MF, rezidual=2000)
    v = m.calc_asset(mf, 2027)
    assert v["accum_depr"] == Decimal("10000.00")
    assert v["book_end"] == Decimal("2000.00")

def test_procent():
    v = m.calc_asset(MF, 2025)
    assert v["procent_anual"] == Decimal("50.00")

def test_invalid():
    with pytest.raises(ValueError):
        m.calc_asset(dict(MF, dnf_luni=0), 2025)

def test_xml_structura():
    x = m.xml_asset(MF, 2026)
    for tag in ("AssetID", "AccountID", "AcquisitionAndProductionCostsBegin",
                "AssetLifeMonth", "BookValueEnd", "ExtraordinaryDepreciationsForPeriod"):
        assert f"<nsSAFT:{tag}>" in x
    assert "<nsSAFT:AssetLifeMonth>24</nsSAFT:AssetLifeMonth>" in x

def test_xml_escape():
    mf = dict(MF, denumire="Strung <auto> & co")
    assert "&amp;" in m.xml_asset(mf, 2026) and "&lt;auto&gt;" in m.xml_asset(mf, 2026)
