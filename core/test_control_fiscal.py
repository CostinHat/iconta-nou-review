# -*- coding: utf-8 -*-
"""Teste pentru semaforul de conformare fiscala (control_fiscal_api v2).
Apara cele 5 defecte reparate in FAZA 1 (BRIEF_CODE_SEMAFOR):
  D1 sarbatori legale in termen · D2 decembrie an-1 invizibil · D3 NULL -> GRI
  D4 scadentar per declaratie (delegat scadente.py) · D5 cod mort sters.
"""
import datetime
from datetime import date
from core import control_fiscal_api as cf


def _chei(lista):
    return {(d["tip"], d["an"], d["luna"]) for d in lista}


# D1 + D4: termenul tine cont de sarbatori (delegat la scadente.py)
def test_termen_sarbatoare_decembrie():
    # 25.12.2026 = vineri SI Craciun; 26 = sambata SI a 2-a zi de Craciun; 27 = duminica
    # -> prima zi lucratoare = luni 28
    assert cf._termen(2026, 11) == date(2026, 12, 28)


# D2: decembrie an-1 NU mai e invizibil (termen 25 ian an curent)
def test_decembrie_an_precedent_vizibil():
    rez = cf.declaratii_datorate({}, are_salariati=True, azi=date(2026, 2, 1))
    assert ("D112", 2025, 12) in _chei(rez["datorate"])


def test_t4_an_precedent_vizibil_trimestrial():
    vector = {"platitor_tva": True, "tip_decont": "trimestrial"}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    assert ("D300", 2025, 12) in _chei(rez["datorate"])  # T4 2025, termen 25 ian 2026


# D3: atribut de vector lipsa -> GRI cu cauza, NU default tacut
def test_tip_decont_null_da_gri_nu_12_luni():
    vector = {"platitor_tva": True, "tip_decont": None}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    tipuri_datorate = {d["tip"] for d in rez["datorate"]}
    assert "D300" not in tipuri_datorate                      # nu s-au fabricat 12 pozitii lunare
    neclar = {n["tip"]: n["cauza"] for n in rez["neclar"]}
    assert "D300" in neclar and "periodicitatea" in neclar["D300"]


def test_regim_fiscal_null_da_gri_pe_d100_si_d101():
    vector = {"regim_fiscal": None}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    neclar = {n["tip"] for n in rez["neclar"]}
    assert "D100" in neclar and "D101" in neclar


def test_platitor_tva_null_da_gri_d300():
    rez = cf.declaratii_datorate({"platitor_tva": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "D300" in {n["tip"] for n in rez["neclar"]}


def test_operatiuni_ic_null_da_gri_d390():
    rez = cf.declaratii_datorate({"operatiuni_ic": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "D390" in {n["tip"] for n in rez["neclar"]}


# vector complet stiut -> nicio pozitie neclara
def test_vector_complet_fara_neclar():
    vector = {"platitor_tva": True, "tip_decont": "lunar",
              "regim_fiscal": "micro", "operatiuni_ic": False}
    rez = cf.declaratii_datorate(vector, are_salariati=True, azi=date(2026, 6, 1))
    assert rez["neclar"] == []


# verdict: prioritatea rosu > galben > gri > verde
def test_verdict_toate_depuse_verde():
    datorate = [{"tip": "D112", "an": 2026, "luna": 1, "termen": "2026-02-25", "perioada": "ian"}]
    depuse = {("D112", 2026, 1)}
    stare, lipsa, urmarit = cf._verdict(datorate, [], depuse, date(2026, 6, 1))
    assert stare == "verde" and lipsa == [] and urmarit == []


def test_verdict_restanta_rosu():
    datorate = [{"tip": "D112", "an": 2026, "luna": 1, "termen": "2026-02-25", "perioada": "ian"}]
    stare, lipsa, _ = cf._verdict(datorate, [], set(), date(2026, 6, 1))
    assert stare == "rosu" and len(lipsa) == 1


def test_verdict_neclar_fara_restanta_gri_nu_verde():
    # nimic datorat/restant, dar exista o pozitie neclara -> gri, NU verde (fabricat)
    stare, _, _ = cf._verdict([], [{"tip": "D300", "cauza": "x"}], set(), date(2026, 6, 1))
    assert stare == "gri"


# D5: cod mort sters
def test_trimestre_pana_la_sters():
    assert not hasattr(cf, "_trimestre_pana_la")


# FAZA 3 — D394 (doar platitori de TVA, perioada = perioada TVA)
def test_d394_platitor_lunar_datorat():
    vector = {"platitor_tva": True, "tip_decont": "lunar"}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    assert ("D394", 2025, 12) in _chei(rez["datorate"])


def test_d394_neplatitor_absent():
    vector = {"platitor_tva": False}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    assert "D394" not in {d["tip"] for d in rez["datorate"]}
    assert "D394" not in {n["tip"] for n in rez["neclar"]}


def test_d394_platitor_None_gri():
    rez = cf.declaratii_datorate({"platitor_tva": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "D394" in {n["tip"] for n in rez["neclar"]}


# FAZA 3 — D406 SAF-T (platitor: perioada TVA; neplatitor: trimestrial; sursa OPANAF 1783/2021)
def test_d406_platitor_lunar_datorat():
    vector = {"platitor_tva": True, "tip_decont": "lunar"}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    assert ("D406", 2025, 12) in _chei(rez["datorate"])


def test_d406_neplatitor_trimestrial_datorat():
    # neplatitorul NU are perioada fiscala TVA -> D406 TRIMESTRIAL (nu GRI, nu lunar)
    vector = {"platitor_tva": False}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    chei = _chei(rez["datorate"])
    assert ("D406", 2025, 12) in chei                 # T4 2025, termen 31 ian 2026
    assert "D406" not in {n["tip"] for n in rez["neclar"]}


def test_d406_platitor_tip_decont_None_gri():
    # platitor CU periodicitate necunoscuta -> GRI (nu se ghiceste), principiul D3
    vector = {"platitor_tva": True, "tip_decont": None}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    assert "D406" in {n["tip"] for n in rez["neclar"]}


def test_d406_platitor_None_gri():
    rez = cf.declaratii_datorate({"platitor_tva": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "D406" in {n["tip"] for n in rez["neclar"]}
