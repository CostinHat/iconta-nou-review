# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import import_export as m

def test_baza():
    assert m.baza_tva_import(10000, 500, 0, 800) == Decimal("11300.00")

def test_baza_invalida():
    with pytest.raises(ValueError):
        m.baza_tva_import(0)

def test_import_cu_certificat():
    r = m.calcul_import(10000, 5, 0, 800, 21, certificat_amanare=True)
    assert r["taxa_vamala"] == Decimal("500.00")
    assert r["baza_tva"] == Decimal("11300.00")
    assert r["tva"] == Decimal("2373.00")
    assert r["mod_tva"] == "decont"

def test_import_fara_certificat():
    r = m.calcul_import(10000, 5, 0, 800)
    assert r["mod_tva"] == "vama"

def test_import_neplatitor():
    r = m.calcul_import(10000, 0, 0, 0, platitor_tva=False)
    assert r["mod_tva"] == "cost"

def test_certificat_neplatitor():
    with pytest.raises(ValueError, match="316"):
        m.calcul_import(10000, 0, certificat_amanare=True, platitor_tva=False)

def test_export_ok():
    ok, ment = m.valideaza_export("Serbia", True)
    assert ok and "294" in ment

def test_export_fara_dve():
    with pytest.raises(ValueError, match="DVE"):
        m.valideaza_export("Serbia", False)
