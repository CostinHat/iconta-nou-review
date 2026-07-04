# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from stocuri import nir_gv, coeficient_k, descarcare_gv

D = Decimal

# --- NIR ---
def test_nir_o_linie_21():
    # cost 100, vanzare cu TVA 181.50 (150 fara TVA + 21%): adaos 50, 4428 = 31.50
    r = nir_gv([{"denumire": "x", "cantitate": 1,
                 "pret_achizitie": "100", "pret_vanzare": "181.50", "cota_tva": 21}])
    assert r["cost_total"] == D("100.00")
    assert r["tva_neexigibila"] == D("31.50")
    assert r["adaos_total"] == D("50.00")
    assert r["valoare_vanzare"] == D("181.50")
    assert r["tva_deductibila"] == D("21.00")
    assert [(n["debit"], n["credit"], n["suma"]) for n in r["note"]] == [
        ("371", "401", D("100.00")), ("4426", "401", D("21.00")),
        ("371", "378", D("50.00")), ("371", "4428", D("31.50"))]

def test_nir_cantitati_si_cote():
    # 10 buc, cost 4, raft 6.05 (5 + 21%) -> cost 40, vanz 60.50, tva 10.50, adaos 10
    r = nir_gv([{"denumire": "a", "cantitate": 10,
                 "pret_achizitie": "4", "pret_vanzare": "6.05"}])
    assert r["adaos_total"] == D("10.00")
    assert r["tva_neexigibila"] == D("10.50")

def test_nir_cota_11():
    # HoReCa alimente: cota 11
    r = nir_gv([{"denumire": "paine", "cantitate": 1,
                 "pret_achizitie": "2", "pret_vanzare": "3.33", "cota_tva": 11}])
    assert r["tva_neexigibila"] == D("0.33")
    assert r["adaos_total"] == D("1.00")

def test_nir_pret_sub_cost():
    with pytest.raises(ValueError):
        nir_gv([{"denumire": "x", "cantitate": 1,
                 "pret_achizitie": "10", "pret_vanzare": "5"}])

def test_nir_cantitate_zero():
    with pytest.raises(ValueError):
        nir_gv([{"denumire": "x", "cantitate": 0,
                 "pret_achizitie": "1", "pret_vanzare": "2"}])

# --- K ---
def test_k_simplu():
    # adaos 500 la stoc 371=1785 cu 4428=285 -> K = 500/1500
    k = coeficient_k("0", "500", "0", "1785", "0", "285")
    assert k == D("500") / D("1500")

def test_k_numitor_invalid():
    with pytest.raises(ValueError):
        coeficient_k("0", "100", "0", "100", "0", "200")

# --- descarcare: exemplul clasic (forum SAGA / didactic) ---
def test_descarcare_exemplu_clasic():
    # stoc: 371=1785 (incl. TVA 19% vechi=285), adaos 500, cost 1000; se vinde tot
    # incasari 1785, TVA colectata 285, rc707 = 1500
    r = descarcare_gv(rc_707="1500", tva_vanzari="285",
                      si_378="0", rc_378="500", si_371="0", rd_371="1785",
                      si_4428="0", rc_4428="285")
    assert r["adaos"] == D("500.00")
    assert r["cmv"] == D("1000.00")
    assert r["tva"] == D("285.00")
    assert r["total_371"] == D("1785.00")   # 371 se goleste complet
    assert [(n["debit"], n["credit"]) for n in r["note"]] == [
        ("607", "371"), ("378", "371"), ("4428", "371")]

def test_descarcare_partiala():
    # se vinde jumatate: rc707=750, tva=142.50
    r = descarcare_gv("750", "142.50", "0", "500", "0", "1785", "0", "285")
    assert r["adaos"] == D("250.00")
    assert r["cmv"] == D("500.00")
    assert r["total_371"] == D("892.50")

def test_descarcare_fara_vanzari():
    r = descarcare_gv("0", "0", "0", "500", "0", "1785", "0", "285")
    assert r["note"] == [] and r["cmv"] == D("0.00")

def test_descarcare_cu_solduri_initiale():
    # cumulat: Si378=200, Rc378=300; Si371=1000, Rd371=1420; Si4428=190, Rc4428=230
    # numitor = 2420-420 = 2000; K = 500/2000 = 0.25; rc707=400 -> adaos 100, cmv 300
    r = descarcare_gv("400", "76", "200", "300", "1000", "1420", "190", "230")
    assert r["adaos"] == D("100.00")
    assert r["cmv"] == D("300.00")

def test_nota_urma():
    r = nir_gv([{"denumire": "x", "cantitate": 1,
                 "pret_achizitie": "100", "pret_vanzare": "181.50"}])
    assert all(n["temei"].startswith("OMFP 1802") for n in r["note"])
