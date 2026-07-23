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
    assert ("d112", 2025, 12) in _chei(rez["datorate"])


def test_t4_an_precedent_vizibil_trimestrial():
    vector = {"platitor_tva": True, "tip_decont": "trimestrial"}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    assert ("d300", 2025, 12) in _chei(rez["datorate"])  # T4 2025, termen 25 ian 2026


# D3: atribut de vector lipsa -> GRI cu cauza, NU default tacut
def test_tip_decont_null_da_gri_nu_12_luni():
    vector = {"platitor_tva": True, "tip_decont": None}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    tipuri_datorate = {d["tip"] for d in rez["datorate"]}
    assert "d300" not in tipuri_datorate                      # nu s-au fabricat 12 pozitii lunare
    neclar = {n["tip"]: n["cauza"] for n in rez["neclar"]}
    assert "d300" in neclar and "periodicitatea" in neclar["d300"]


def test_regim_fiscal_null_da_gri_pe_d100_si_d101():
    vector = {"regim_fiscal": None}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    neclar = {n["tip"] for n in rez["neclar"]}
    assert "d100" in neclar and "d101" in neclar


def test_platitor_tva_null_da_gri_d300():
    rez = cf.declaratii_datorate({"platitor_tva": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "d300" in {n["tip"] for n in rez["neclar"]}


def test_operatiuni_ic_null_da_gri_d390():
    rez = cf.declaratii_datorate({"operatiuni_ic": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "d390" in {n["tip"] for n in rez["neclar"]}


# vector complet stiut -> nicio pozitie neclara
def test_vector_complet_fara_neclar():
    vector = {"platitor_tva": True, "tip_decont": "lunar",
              "regim_fiscal": "micro", "operatiuni_ic": False}
    rez = cf.declaratii_datorate(vector, are_salariati=True, azi=date(2026, 6, 1))
    assert rez["neclar"] == []


# clasificare + stare: prioritatea rosu > galben > gri > verde, cu MOTIV pe orice culoare
_D = [{"tip": "d112", "an": 2026, "luna": 1, "termen": "2026-02-25", "perioada": "ian"}]


def test_clasifica_depusa_confirmata_cu_motiv():
    # depusa -> confirmate (verde). [C1] motiv = ADITIV (data + la/dupa termen), NU repeta tip/perioada/termen din antet
    lipsa, urmarit, confirmate = cf._clasifica(_D, {("d112", 2026, 1): date(2026, 2, 20)}, date(2026, 6, 1))
    assert lipsa == [] and urmarit == [] and len(confirmate) == 1
    m = confirmate[0]["motiv"]
    assert "Depus" in m and "la termen" in m and "D112" not in m   # nu duplica antetul


def test_clasifica_restanta_temei_structurat_nu_prose():
    # [C1] restanta: temeiul e STRUCTURAT (perioada + termen din antet); motiv-prose gol la o declaratie simpla
    lipsa, urmarit, _ = cf._clasifica(_D, {}, date(2026, 6, 1))
    assert len(lipsa) == 1 and urmarit == []
    assert lipsa[0].get("perioada") and lipsa[0].get("termen")   # temei structurat prezent
    assert lipsa[0]["motiv"] == ""                                # fara duplicare a antetului


def test_stare_prioritate():
    assert cf._stare([], [], []) == "verde"
    assert cf._stare([], [], [{"tip": "d300", "motiv": "x"}]) == "gri"     # gri nu se ascunde ca verde
    assert cf._stare([], [1], [{"x": 1}]) == "galben"                       # galben > gri
    assert cf._stare([1], [1], [1]) == "rosu"                                # rosu domina


# D5: cod mort sters
def test_trimestre_pana_la_sters():
    assert not hasattr(cf, "_trimestre_pana_la")


# FAZA 3 — D394 (doar platitori de TVA, perioada = perioada TVA)
def test_d394_platitor_lunar_datorat():
    vector = {"platitor_tva": True, "tip_decont": "lunar"}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    assert ("d394", 2025, 12) in _chei(rez["datorate"])


def test_d394_neplatitor_absent():
    vector = {"platitor_tva": False}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    assert "d394" not in {d["tip"] for d in rez["datorate"]}
    assert "d394" not in {n["tip"] for n in rez["neclar"]}


def test_d394_platitor_None_gri():
    rez = cf.declaratii_datorate({"platitor_tva": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "d394" in {n["tip"] for n in rez["neclar"]}


# FAZA 3 — D406 SAF-T (platitor: perioada TVA; neplatitor: trimestrial; sursa OPANAF 1783/2021)
def test_d406_platitor_lunar_datorat():
    vector = {"platitor_tva": True, "tip_decont": "lunar"}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    assert ("d406", 2025, 12) in _chei(rez["datorate"])


def test_d406_neplatitor_trimestrial_datorat():
    # neplatitorul NU are perioada fiscala TVA -> D406 TRIMESTRIAL (nu GRI, nu lunar)
    vector = {"platitor_tva": False}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 2, 1))
    chei = _chei(rez["datorate"])
    assert ("d406", 2025, 12) in chei                 # T4 2025, termen 31 ian 2026
    assert "d406" not in {n["tip"] for n in rez["neclar"]}


def test_d406_platitor_tip_decont_None_gri():
    # platitor CU periodicitate necunoscuta -> GRI (nu se ghiceste), principiul D3
    vector = {"platitor_tva": True, "tip_decont": None}
    rez = cf.declaratii_datorate(vector, are_salariati=False, azi=date(2026, 6, 1))
    assert "d406" in {n["tip"] for n in rez["neclar"]}


def test_d406_platitor_None_gri():
    rez = cf.declaratii_datorate({"platitor_tva": None}, are_salariati=False, azi=date(2026, 6, 1))
    assert "d406" in {n["tip"] for n in rez["neclar"]}


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


# ---- F189+ : ramificare Control fiscal pe tip_firma (partida simpla) ----
def test_pfa_d100_d101_d406_neaplicabile_nu_restante():
    # PFA/persoane fizice: D100/D101 (persoana juridica) si D406 (SAF-T, OPANAF 407/2025 Anexa 5 pct.4 lit.q
    # exclude NECONDITIONAT persoanele fizice) NU se datoreaza -> neaplicabile cu motiv, nu datorate/gri.
    v = {"platitor_tva": False, "regim_fiscal": None, "operatiuni_ic": False, "partida_simpla": True}
    rez = cf.declaratii_datorate(v, are_salariati=False, azi=date(2026, 7, 23))
    dat = {d["tip"] for d in rez["datorate"]}
    neap = {d["tip"]: d["motiv"] for d in rez["neaplicabile"]}
    assert "d406" not in dat                             # NU restanta inventata
    assert {"d100", "d101", "d406"} <= set(neap)
    assert "D212" in neap["d100"] and "D212" in neap["d101"]
    assert "407/2025" in neap["d406"] and "necondiționat" in neap["d406"].lower()

def test_srl_neschimbat_d406_datorat_d100_d101_gri():
    # SRL (partida dubla): NEschimbat - D406 trimestrial datorat, D100/D101 gri pe regim None, nimic neaplicabil.
    v = {"platitor_tva": False, "regim_fiscal": None}   # fara partida_simpla -> juridic
    rez = cf.declaratii_datorate(v, are_salariati=False, azi=date(2026, 7, 23))
    dat = {d["tip"] for d in rez["datorate"]}
    neclar = {d["tip"] for d in rez["neclar"]}
    assert "d406" in dat                                 # SRL neplatitor -> D406 trimestrial
    assert {"d100", "d101"} <= neclar                    # regim None -> gri (neschimbat)
    assert not rez["neaplicabile"]


# ---- primitiva regim_efectiv (partida simpla => None neconditionat; contract strict, fara .get) ----
from core.migrare_api import regim_efectiv as _regim_efectiv
import pytest as _pytest

def test_regim_efectiv_pfa_e_None_neconditionat():
    assert _regim_efectiv({"tip_firma": "pfa", "regim_fiscal": "micro"}) is None   # ignora regim scris
    assert _regim_efectiv({"tip_firma": "pfa", "regim_fiscal": None}) is None

def test_regim_efectiv_srl_intoarce_regimul_sau_None():
    assert _regim_efectiv({"tip_firma": "srl", "regim_fiscal": "micro"}) == "micro"
    assert _regim_efectiv({"tip_firma": "srl", "regim_fiscal": "PROFIT"}) == "profit"
    assert _regim_efectiv({"tip_firma": "srl", "regim_fiscal": None}) is None       # vector necompletat

def test_regim_efectiv_strict_keyerror_pe_cheie_absenta():
    with _pytest.raises(KeyError):
        _regim_efectiv({"regim_fiscal": "micro"})     # tip_firma absent -> KeyError, fara fallback
    with _pytest.raises(KeyError):
        _regim_efectiv({"tip_firma": "srl"})          # regim_fiscal absent -> KeyError


# ---- D390 pe FAPT lunar (semafor, privire inapoi): nicio restanta falsa ----
# obligatii_datorate consulta d390_fapt(an, luna) in loc de bifa statica operatiuni_ic.
# Cost asimetric: o restanta D390 falsa = acuzatie nefondata -> inapoi decidem pe fapt.

def test_semafor_d390_luna_inchisa_fara_operatiuni_nu_e_restanta():
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": True, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23),
                                d390_fapt=lambda a, m: False)   # nicio luna cu operatiuni IC
    assert not any(d["tip"] == "d390" for d in rez["datorate"])          # NICIO restanta falsa
    # confirmare cu temei DOAR pe ultima luna inchisa (iunie), nu tot istoricul
    d390_neaplic = [n for n in rez["neaplicabile"] if n["tip"] == "d390"]
    assert len(d390_neaplic) == 1 and d390_neaplic[0].get("luna") == 6

def test_semafor_d390_luna_cu_operatiuni_ramane_datorata():
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": True, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23),
                                d390_fapt=lambda a, m: True)    # fiecare luna are operatiuni
    assert any(d["tip"] == "d390" for d in rez["datorate"])

def test_semafor_d390_fara_fapt_pastreaza_comportamentul_pe_bifa():
    # d390_fapt=None (matricea de 64) -> bifa decide, D390 lunar ca inainte
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": True, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23))
    assert any(d["tip"] == "d390" for d in rez["datorate"])
    assert not any(n["tip"] == "d390" for n in rez["neaplicabile"])


# ---- D390: faptul PRIMEAZA peste flag; contradictie flag-vs-facturi = semnal (item 1+2, 23.07) ----

def test_semafor_d390_fapt_primeaza_peste_flag_false():
    # d390_fapt=True -> D390 datorat INDIFERENT de operatiuni_ic=False (faptul primeaza)
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23), d390_fapt=lambda a, m: True)
    assert any(d["tip"] == "d390" for d in rez["datorate"])

def test_semafor_d390_contradictie_flag_false_dar_facturi_ic():
    # operatiuni_ic=False dar facturi IC (fapt True) -> semnal gri cu temei (nu blocare)
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23), d390_fapt=lambda a, m: True)
    assert sum(1 for n in rez["neclar"] if n["tip"] == "d390" and "declară FĂRĂ" in n["cauza"]) == 1

def test_semafor_d390_flag_false_fapt_false_nimic():
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23), d390_fapt=lambda a, m: False)
    assert not any(d["tip"] == "d390" for d in rez["datorate"])
    assert not any(n["tip"] == "d390" and "declară FĂRĂ" in n["cauza"] for n in rez["neclar"])

def test_semafor_d390_neplatitor_flag_false_nu_consulta_faptul():
    # POARTA (regresie tenant_001): neplatitor cu flag False -> D390 neaplicabil PRIN FORMA. Faptul NU se consulta
    # (nu atinge DB -> nu crapa pe d301_operatiuni lipsa la scheme vechi de partida simpla). Nimic D390 emis.
    # Rastoarna aserția de la item 2 (neplatitor nu mai fabrica semnal pe facturi IC - obligatia lui e art. 317, nu fapt).
    v = {"platitor_tva": False, "tip_decont": None, "operatiuni_ic": False, "regim_fiscal": "micro"}
    apelat = []
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date(2026, 7, 23),
                                d390_fapt=lambda a, m: apelat.append((a, m)) or True)
    assert apelat == []                                         # faptul NU e consultat la neplatitor
    assert not any(n["tip"] == "d390" for n in rez["neclar"])   # nimic D390 emis (flag False -> nimic)


# ---- G1: neaplicabile_forma = sursa unica excludere prin forma (partida simpla) ----
def test_neaplicabile_forma_pfa_vs_juridic():
    assert set(cf.neaplicabile_forma("pfa")) == {"d100", "d101", "d406"}
    assert "D212" in cf.neaplicabile_forma("pfa")["d101"]
    assert cf.neaplicabile_forma("srl") == {}
    # NOTA (finding, nereparat): regim_contabil trateaza ca 'simpla' DOAR 'pfa'; 'ii'/'if'/'pfl' -> 'dubla'
    # (tip_firma_nrm nu le normalizeaza la pfa). OK daca DB stocheaza 'pfa' pt toate entitatile de partida
    # simpla (selectorul de creare), dar de verificat separat daca II/IF pot ajunge cu tip_firma propriu.
    assert cf.neaplicabile_forma("srl") == cf.neaplicabile_forma(None) == {}   # juridic/necunoscut -> nimic exclus
