# -*- coding: utf-8 -*-
"""Teste D212 (PFA/II/IF sistem real) — praguri CAS/CASS/impozit din Codul fiscal.

Gasit prin retestarea sistematica a fluxurilor P1-P5 (16.07.2026): core/d212_engine.py
avea teste corecte, dar intr-o functie _test() apelata DOAR din __main__ - deci NU
rulau sub pytest, nu erau in plasa de regresie. Aduse aici ca teste reale.

Sursa praguri (obiectiva, lege): Cod fiscal art.148-149 (CAS), 154/170 (CASS), 68-69
(venit net). salariu_minim reper 2025/2026 = 4050 lei (HG 1506/2024; fix pe an,
instructiuni formular 212). CAS 25% in trepte 12/24 sm; CASS 10% liniar 6..60 sm
(72 sm pentru venituri 2026, Legea 141/2025); impozit 10%.
"""
from core.d212_engine import (
    calculeaza_cas, calculeaza_cass, calculeaza_d212,
    PLAFOANE_VENIT_2025, PLAFOANE_VENIT_2026,
)

P = PLAFOANE_VENIT_2025  # sm=4050: 6sm=24300, 12sm=48600, 24sm=97200, 60sm=243000


# ---- CAS 25% in trepte (art. 148-149) ----
def test_cas_sub_12sm_neobligatoriu():
    assert calculeaza_cas(40000, P) == {"obligatoriu": False, "baza": 0, "cas": 0.0}

def test_cas_intre_12_si_24sm_baza_12sm():
    r = calculeaza_cas(70000, P)
    assert r["obligatoriu"] and r["baza"] == 48600 and r["cas"] == 12150.0

def test_cas_peste_24sm_plafonat():
    r = calculeaza_cas(150000, P)
    assert r["baza"] == 97200 and r["cas"] == 24300.0

def test_cas_optional_sub_prag_cu_optiune():
    r = calculeaza_cas(40000, P, optiune_cas=True)
    assert r["baza"] == 48600 and r["cas"] == 12150.0


# ---- CASS 10% liniar (art. 154/170) ----
def test_cass_sub_6sm_neobligatoriu():
    assert calculeaza_cass(20000, P) == {"obligatoriu": False, "baza": 0, "cass": 0.0}

def test_cass_la_6sm_minim():
    assert calculeaza_cass(24300, P)["cass"] == 2430.0

def test_cass_liniar_in_interval():
    assert calculeaza_cass(100000, P)["cass"] == 10000.0

def test_cass_peste_60sm_plafonat_2025():
    r = calculeaza_cass(300000, P)
    assert r["baza"] == 243000 and r["cass"] == 24300.0

def test_cass_plafon_2026_urcat_la_72sm():
    # Legea 141/2025: plafon CASS 72 sm pt venituri 2026 (72*4050=291600)
    r = calculeaza_cass(300000, PLAFOANE_VENIT_2026)
    assert r["baza"] == 291600 and r["cass"] == 29160.0


# ---- Calcul complet (art. 68) ----
def test_d212_complet_venit_mare():
    r = calculeaza_d212(150000, 30000, P)      # net 120000
    assert r["venit_net"] == 120000
    assert r["cas"]["cas"] == 24300.0          # peste 24 sm -> plafon
    assert r["cass"]["cass"] == 12000.0        # 120000 x 10%
    assert r["baza_impozit"] == 120000 - 24300 - 12000
    assert r["impozit"] == round(r["baza_impozit"] * 0.10, 2)
    assert r["total_datorat"] == round(24300.0 + 12000.0 + r["impozit"], 2)

def test_d212_venit_mic_doar_impozit():
    r = calculeaza_d212(30000, 12000, P)       # net 18000 (< 6 sm)
    assert r["venit_net"] == 18000
    assert r["cas"]["cas"] == 0.0 and r["cass"]["cass"] == 0.0
    assert r["impozit"] == 1800.0              # 18000 x 10%

def test_d212_cheltuieli_peste_venit_net_zero():
    r = calculeaza_d212(10000, 15000, P)
    assert r["venit_net"] == 0.0 and r["total_datorat"] == 0.0
