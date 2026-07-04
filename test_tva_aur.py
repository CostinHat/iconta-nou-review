# -*- coding: utf-8 -*-
import pytest
from core import tva_aur as m

def test_lingou_ok():
    assert m.este_aur_investitii("lingou", 995) == (True, None)
    assert m.este_aur_investitii("plancheta", 999.9) == (True, None)

def test_lingou_puritate_mica():
    ok, motiv = m.este_aur_investitii("lingou", 990)
    assert not ok and "995" in motiv

def test_moneda_ok():
    assert m.este_aur_investitii("moneda", 900, 1900, 1000, 600) == (True, None)

def test_moneda_puritate():
    ok, motiv = m.este_aur_investitii("moneda", 850, 1900, 1000, 600)
    assert not ok and "900" in motiv

def test_moneda_an():
    ok, motiv = m.este_aur_investitii("moneda", 916, 1800, 1000, 600)
    assert not ok and "1800" in motiv

def test_moneda_pret_peste_80():
    ok, motiv = m.este_aur_investitii("moneda", 916, 1900, 1100, 600)
    assert not ok and "80%" in motiv

def test_moneda_limita_exacta():
    assert m.este_aur_investitii("moneda", 916, 1900, 1080, 600) == (True, None)

def test_tip_necunoscut():
    ok, motiv = m.este_aur_investitii("inel", 999)
    assert not ok

def test_livrare_scutita():
    assert m.livrare_aur(False, "PF", "Popescu Ion, CNP 1...") == "scutit"
    assert m.livrare_aur(False, "PJ", "SC X SRL, CUI 123") == "scutit"

def test_livrare_taxare_inversa():
    assert m.livrare_aur(True, "PJ", "SC X SRL, CUI 123") == "taxare_inversa"

def test_optiune_catre_pf_interzisa():
    with pytest.raises(ValueError, match="al. 4-5"):
        m.livrare_aur(True, "PF", "Popescu Ion")

def test_client_neidentificat():
    with pytest.raises(ValueError, match="al. 10"):
        m.livrare_aur(False, "PF", "")
