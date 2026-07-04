# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import subventii as m

def test_exploatare():
    assert m.nota_subventie_exploatare(50000)["linii"] == [("445", "741", Decimal("50000.00"))]
    assert m.nota_subventie_exploatare(50000, "incasare")["linii"] == [("5121", "445", Decimal("50000.00"))]

def test_investitii():
    assert m.nota_subventie_investitii(200000)["linii"] == [("445", "4751", Decimal("200000.00"))]

def test_reluare():
    r = m.reluare_lunara_investitii(400000, 200000, 5000)
    assert r["linii"] == [("4751", "7584", Decimal("2500.00"))]
    assert r["procent_subventionat"] == "50.00"

def test_subventie_peste_activ():
    with pytest.raises(ValueError, match="depasi"):
        m.reluare_lunara_investitii(100000, 150000, 1000)

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_subventie_exploatare(0)
