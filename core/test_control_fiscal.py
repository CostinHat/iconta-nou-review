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


# clasificare + stare: prioritatea rosu > galben > gri > verde, cu MOTIV pe orice culoare
_D = [{"tip": "D112", "an": 2026, "luna": 1, "termen": "2026-02-25", "perioada": "ian"}]


def test_clasifica_depusa_confirmata_cu_motiv():
    # depusa -> confirmate (verde) cu motiv, inclusiv data si "la termen"
    lipsa, urmarit, confirmate = cf._clasifica(_D, {("D112", 2026, 1): date(2026, 2, 20)}, date(2026, 6, 1))
    assert lipsa == [] and urmarit == [] and len(confirmate) == 1
    m = confirmate[0]["motiv"]
    assert "D112" in m and "depus" in m and "la termen" in m


def test_clasifica_restanta_cu_motiv():
    lipsa, urmarit, _ = cf._clasifica(_D, {}, date(2026, 6, 1))
    assert len(lipsa) == 1 and urmarit == []
    assert "nedepus" in lipsa[0]["motiv"] and "depășit" in lipsa[0]["motiv"]


def test_stare_prioritate():
    assert cf._stare([], [], []) == "verde"
    assert cf._stare([], [], [{"tip": "D300", "motiv": "x"}]) == "gri"     # gri nu se ascunde ca verde
    assert cf._stare([], [1], [{"x": 1}]) == "galben"                       # galben > gri
    assert cf._stare([1], [1], [1]) == "rosu"                                # rosu domina


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


# [F180] constatare_regim_tva: platitor_tva local vs snapshot ANAF
def test_constatare_regim_tva_divergenta_rosu_cu_remediu():
    c = cf.constatare_regim_tva(local=True, anaf=False, data=date(2026, 7, 22))
    assert c["stare"] == "rosu"
    assert c["eticheta"] == "Regim TVA vs ANAF"
    assert c["remediu"]["fel"] == "investigatie"          # NICIODATA buton auto pe regim
    assert "SPV" in c["remediu"]["actiune"]
    assert "2026-07-22" in c["limita"]                    # data snapshot in limita


def test_constatare_regim_tva_coincid_verde():
    c = cf.constatare_regim_tva(local=True, anaf=True, data=date(2026, 7, 22))
    assert c["stare"] == "verde"
    assert "remediu" not in c                             # verde nu propune actiune


def test_constatare_regim_tva_fara_snapshot_gri():
    c = cf.constatare_regim_tva(local=True, anaf=None, data=None)
    assert c["stare"] == "gri"
    assert "fără snapshot" in c["mesaj"] or "snapshot" in c["limita"]
