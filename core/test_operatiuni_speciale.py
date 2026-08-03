# -*- coding: utf-8 -*-
"""Teste gardian pentru operatiuni speciale P2.7 (leasing, avansuri,
sponsorizari, provizioane). Valori verificate contra sursei oficiale:
art. 25(4)i / art. 26 CF, OMFP 1802/2014, Legea 32/1994, Ordin ANAF 3562/2024.
"""
from decimal import Decimal
from core import sponsorizari as sp, avansuri as av, leasing as le, provizioane as pr


# ---------- sponsorizari (art. 25(4)i) ----------

def test_plafon_dublu_min_ca_impozit():
    p = sp.plafon_credit(1000000, 50000)
    assert p["limita_ca"] == Decimal("7500.00")       # 0,75% CA
    assert p["limita_impozit"] == Decimal("10000.00") # 20% impozit
    assert p["plafon"] == Decimal("7500.00")          # min


def test_credit_sub_plafon_lasa_redirectionabil():
    r = sp.credit_sponsorizare(1000000, 50000, 5000)
    assert r["credit"] == Decimal("5000.00")
    assert r["redirectionabil_d177"] == Decimal("2500.00")  # 7500 - 5000


def test_micro_fara_credit():
    assert sp.credit_sponsorizare(1000000, 50000, 5000, tip_impozit="micro")["credit"] == Decimal("0.00")


def test_beneficiar_neinscris_fara_credit():
    assert sp.credit_sponsorizare(1000000, 50000, 5000, beneficiar_in_registru=False)["credit"] == Decimal("0.00")


# ---------- avansuri (art. 282 al.2 lit.b) ----------

def test_avans_platit_tva_deductibil():
    r = av.nota_avans_platit(1000, 21)
    assert r["tva"] == Decimal("210.00")
    assert ("4091", "401", Decimal("1000.00")) in r["linii"]
    assert ("4426", "401", Decimal("210.00")) in r["linii"]


# ---------- leasing financiar (OMFP 1802 pct.212-217) ----------

def test_leasing_rata_capital_dobanda_tva():
    r = le.nota_rata_financiar(500, dobanda=50)
    assert r["tva"] == Decimal("115.50")  # 21% x (500+50)
    assert ("167", "404", Decimal("500.00")) in r["linii"]  # capital
    assert ("666", "404", Decimal("50.00")) in r["linii"]   # dobanda pe cheltuiala


# ---------- provizioane (art. 26 CF) ----------

def test_provizion_30pct_peste_270_zile():
    pct, _ = pr.deductibilitate_creanta(300, False, False)
    assert pct == 30


def test_provizion_afiliata_nedeductibil():
    pct, _ = pr.deductibilitate_creanta(300, False, True)
    assert pct == 0


def test_provizion_garantata_nedeductibil():
    pct, _ = pr.deductibilitate_creanta(300, True, False)
    assert pct == 0



def test_rezerva_legala_5pct_plafon_20pct_capital():
    """Rezerva legala CONTABILA (Legea 31/1990 art.183, OMFP 1802/2014 pct.421): 5%% din profit,
    plafonata cumulat la 20%% din capital social minus rezerva deja existenta. NOTA: deductibilitatea
    FISCALA (CF art.26 alin.(1) lit.a, cu add-back-ul cheltuielii cu impozitul pe profit) NU e
    implementata nicaieri - decizie de produs (DECIZII 03.08)."""
    from core.motor import rezerva_legala
    from datetime import date
    la = date(2026, 1, 1)
    assert rezerva_legala(100000, 200000, 0, la_data=la)["suma"] == Decimal("5000.00")    # 5%% din profit
    assert rezerva_legala(100000, 200000, 40000, la_data=la)["suma"] == Decimal("0.00")   # plafon 20%% atins
    assert rezerva_legala(100000, 200000, 37000, la_data=la)["suma"] == Decimal("3000.00")# plafon musca (spatiu 3000)
    assert rezerva_legala(-500, 200000, 0, la_data=la)["suma"] == Decimal("0.00")         # profit negativ
