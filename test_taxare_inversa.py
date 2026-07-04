# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import taxare_inversa as m

AZI = date(2026, 7, 4)

def test_deseuri_ok():
    ok, ment = m.se_aplica("deseuri", 1000, True, True, AZI)
    assert ok and "lit. a)" in ment

def test_fara_tva_beneficiar():
    with pytest.raises(ValueError, match="art. 331 al. 1"):
        m.se_aplica("deseuri", 1000, True, False, AZI)

def test_telefoane_sub_prag():
    with pytest.raises(ValueError, match="22500"):
        m.se_aplica("telefoane", 20000, True, True, AZI)

def test_telefoane_peste_prag():
    ok, ment = m.se_aplica("telefoane", 22500, True, True, AZI)
    assert ok and "lit. i)" in ment

def test_cereale_valabil_2026():
    ok, _ = m.se_aplica("cereale", 5000, True, True, AZI)
    assert ok

def test_cereale_expirat_2027():
    with pytest.raises(ValueError, match="expirat"):
        m.se_aplica("cereale", 5000, True, True, date(2027, 1, 5))

def test_cladiri_fara_expirare():
    ok, _ = m.se_aplica("cladiri_terenuri", 500000, True, True, date(2027, 6, 1))
    assert ok

def test_categorie_gresita():
    with pytest.raises(ValueError, match="necunoscuta"):
        m.se_aplica("altceva", 1, True, True, AZI)

def test_tva_beneficiar():
    assert m.tva_beneficiar(10000) == Decimal("2100.00")
    assert m.tva_beneficiar(1234.56, 11) == Decimal("135.80")

def test_tva_invalid():
    with pytest.raises(ValueError):
        m.tva_beneficiar(0)
