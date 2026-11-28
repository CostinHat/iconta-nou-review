# -*- coding: utf-8 -*-
"""[17.5-F5, funcția 502] Consultanța fiscală M1–M5: stările exacte, motivele demonstrate, lipsurile cu locul completării, valorile la
limită, regula economiilor compatibile și garda secțiunii «Consultanță» (Cabinet 7). Așteptările economice se calculează din intrările
probei și din parametrii registrului datat (`common.cota`), nu prin funcțiile testate. Fără bază de date: citirile se dau probei."""
import ast
import datetime as dt
import os
import re
from decimal import Decimal, ROUND_HALF_UP
from types import SimpleNamespace

import pytest

from core import common as C
from core import consultanta_fiscala as CF

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LA = dt.date(2026, 11, 3)
MICRO = {"nume": "Micro SRL", "cui": "1", "regim_fiscal": "micro", "tip_firma": "srl"}
PROFIT = {"nume": "Profit SRL", "cui": "2", "regim_fiscal": "profit", "tip_firma": "srl"}


def _q(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def test_ordinea_si_starile_exacte():
    assert [c for c, _ in CF.MASURI] == ["M1", "M2", "M3", "M4", "M5"]
    assert CF.STARI == ("Se aplică", "Nu se aplică", "Lipsesc date", "Lipsesc date — temei neverificat")
    assert CF.FRAZA == "Aplicația semnalează și calculează; decizia și consilierea clientului aparțin contabilului."


# ───────────────────────── M3 ─────────────────────────
def test_m3_micro_din_2024_nu_se_aplica_cu_temeiul():
    m = CF.m3(None, None, "s", MICRO, LA)
    assert m["stare"] == "Nu se aplică" and "art. 56" in m["motiv"] and "OUG 115/2023" in m["motiv"] and "2023" in m["motiv"]
    assert m["suma"] is None


def _m3_profit(monkeypatch, impozit, ca, sp, intreg=True):
    monkeypatch.setattr(CF, "_d101_an", lambda conn, schema, an: (SimpleNamespace(P={"P41": impozit}), None))
    monkeypatch.setattr(CF, "_evidenta_intreaga", lambda cur, schema, an: (intreg, None))
    monkeypatch.setattr(CF, "_rulaj", lambda cur, schema, prefix, parte, an, la: {"70": Decimal(ca), "6582": Decimal(sp)}[prefix])
    return CF.m3(None, None, "s", PROFIT, LA)


def test_m3_standard_plafon_credit_si_disponibil(monkeypatch):
    """CA 1.000.000, impozit 30.000, sponsorizare 2.000: plafon min(7.500; 6.000) = 6.000, credit 2.000, disponibil 4.000."""
    m = _m3_profit(monkeypatch, Decimal("30000"), "1000000", "2000")
    plafon = min(_q(Decimal("1000000") * Decimal("0.0075")), _q(Decimal("30000") * Decimal("0.20")))
    assert plafon == Decimal("6000.00")
    assert m["stare"] == "Se aplică" and m["valori"]["plafon"] == "6000.00" and m["valori"]["credit"] == "2000.00"
    assert m["suma"] == "4000.00" and m["sens"] == CF.SENS_ECONOMIE_FIRMA
    assert any("D177" in c and "zero" not in c or "economie suplimentară de numerar" in c for c in m["conditii"])


def test_m3_fara_impozit_si_plafon_consumat(monkeypatch):
    assert _m3_profit(monkeypatch, Decimal("0"), "1000000", "0")["stare"] == "Nu se aplică"
    m = _m3_profit(monkeypatch, Decimal("30000"), "1000000", "6000")
    assert m["stare"] == "Nu se aplică" and "consumat" in m["motiv"] and m["suma"] == "0.00"


def test_m3_evidenta_incompleta_lipsesc_date_cu_locul(monkeypatch):
    m = _m3_profit(monkeypatch, Decimal("30000"), "1000000", "0", intreg=False)
    assert m["stare"] == "Lipsesc date" and m["lipsuri"] and m["lipsuri"][0]["unde"]


# ───────────────────────── M4 ─────────────────────────
def _m4(monkeypatch, curs, ca, intreg=True, la=LA):
    monkeypatch.setattr(CF, "_curs_eur", lambda cur, zi: curs)
    monkeypatch.setattr(CF, "_evidenta_intreaga", lambda cur, schema, an: (intreg, dt.date(2026, 7, 31)))
    monkeypatch.setattr(CF, "_rulaj", lambda cur, schema, prefix, parte, an, la_: Decimal(ca))
    return CF.m4(None, "s", MICRO, la)


def test_m4_plafonul_in_lei_e_suta_de_mii_de_euro_la_cursul_inchiderii_precedente(monkeypatch):
    eur = C.cota("plafon_micro_eur", dt.date(2026, 1, 1))[0]
    assert eur == Decimal("100000")
    m = _m4(monkeypatch, Decimal("5.0985"), "0", intreg=False)
    assert m["valori"]["plafon_lei"] == str(_q(Decimal("100000") * Decimal("5.0985"))) == "509850.00"
    assert m["perioada"] == "plafonul anului 2026" and re.findall(r"20\d\d", m["perioada"]) == ["2026"]
    assert m["stare"] != "Nu se aplică"


@pytest.mark.parametrize("ca, marja", [("509849.99", "0.01"), ("509850.00", "0.00"), ("509850.01", "-0.01")])
def test_m4_de_o_parte_si_de_alta_a_plafonului_si_la_egalitate(monkeypatch, ca, marja):
    m = _m4(monkeypatch, Decimal("5.0985"), ca)
    assert m["suma"] == marja and m["sens"] == CF.SENS_MARJA
    depasit = Decimal(ca) > Decimal("509850.00")
    assert ("trimestru" in m["valori"]) == depasit, "la egalitate plafonul încă e respectat"
    assert "legate" in m["motiv"], "o entitate legată cu venituri necunoscute nu se presupune zero"


def test_m4_curs_lipsa_si_temei_lipsa(monkeypatch):
    m = _m4(monkeypatch, None, "0")
    assert m["stare"] == "Lipsesc date" and "31.12.2025" in m["motiv"] and m["lipsuri"]
    m = _m4(monkeypatch, Decimal("5"), "0", la=dt.date(2025, 6, 1))
    assert m["stare"] == "Lipsesc date — temei neverificat" and m["suma"] is None and "plafon_lei" not in m["valori"]


def test_m4_profit_nu_se_aplica():
    assert CF.m4(None, "s", PROFIT, LA)["stare"] == "Nu se aplică"


# ───────────────────────── M5 ─────────────────────────
class _Cur:
    def __init__(self, randuri):
        self.r = randuri

    def execute(self, *a):
        pass

    def fetchall(self):
        return self.r


def test_m5_micro_nu_se_aplica():
    assert CF.m5(None, None, "s", MICRO, LA)["stare"] == "Nu se aplică"


def test_m5_fara_activ_eligibil_nu_se_aplica():
    m = CF.m5(None, _Cur([{"denumire": "Mobilier", "cod_catalog": "6.1.1", "valoare": 5000, "data_pif": LA, "cont_imobilizare": "214"}]), "s", PROFIT, LA)
    assert m["stare"] == "Nu se aplică" and "2.1" in m["motiv"]


@pytest.mark.parametrize("profit, investit, asteptat", [("100000", "40000", "40000"), ("10000", "40000", "10000"), ("0", "40000", "0")])
def test_m5_scutirea_limitata_de_profit(monkeypatch, profit, investit, asteptat):
    monkeypatch.setattr(CF, "_d101_an", lambda conn, schema, an: (SimpleNamespace(P={"P38a": Decimal(profit)}), None))
    cur = _Cur([{"denumire": "Strung", "cod_catalog": "2.1.4.1", "valoare": Decimal(investit), "data_pif": LA, "cont_imobilizare": "2131"}])
    m = CF.m5(None, cur, "s", PROFIT, LA)
    cota = C.cota("impozit_profit", LA)[0]
    assert m["suma"] == str(_q(Decimal(asteptat) * cota))
    # [17.5-T] actualizat la decizia lui Costin 28.11.2026, corecția 1 la 17.5-F6 pct.5 (core/consultanta_fiscala.py: m5, SENS_ESTIMARE_M5):
    # M5 nu e «Se aplică»; cu economie pozitivă e «Lipsesc date», iar suma e numai o estimare, cu condiția scrisă (active noi, din lista
    # specială, puse în funcțiune); fără profit rămâne «Nu se aplică»
    estimare = Decimal(asteptat) > 0
    assert m["stare"] == ("Lipsesc date" if estimare else "Nu se aplică")
    assert m["stare"] != "Se aplică"
    if estimare:
        assert m["sens"] == CF.SENS_ESTIMARE_M5 and "estimare" in m["sens"]
        for conditie in ("noi", "lista specială", "puse în funcțiune"):
            assert conditie in m["motiv"] and conditie in m["sens"], (conditie, m)
        assert m["lipsuri"] and m["lipsuri"][0]["unde"].startswith("verificare manuală")
        assert CF.economie_compatibila({"masuri": [m]}) == Decimal("0")   # estimarea nu intră în economia cabinetului
    # [17.5-F6, corecția 1 pct.6, C247] cota impozitului în pași prin funcția de format: „16%”, nu „0.16”
    procent = cota * 100
    text_cota = "%s%%" % (str(int(procent)) if procent == procent.to_integral_value() else str(procent.normalize()).replace(".", ","))
    assert m["pasi"][-1].endswith("× %s." % text_cota), m["pasi"]
    assert str(cota) not in m["pasi"][-1]


# ───────────────────────── M1 ─────────────────────────
def test_m1_fara_asociati_lipsesc_date_cu_locul(monkeypatch):
    monkeypatch.setattr(CF, "_asociati", lambda cur, schema: [])
    m = CF.m1(None, "s", MICRO, LA)
    assert m["stare"] == "Lipsesc date" and m["lipsuri"] == [{"ce": "asociații persoane fizice, cu CNP și cotă", "unde": "Date firmă → Asociați"}]


@pytest.mark.parametrize("asociati", [
    [{"nume": "Ion Test", "cnp": "1850101400017", "cota": Decimal("60")}, {"nume": "Maria Test", "cnp": "2850101400019", "cota": Decimal("40")}],
    [{"nume": "Ion Test", "cnp": "1850101400017", "cota": Decimal("60")}, {"nume": "Proba Holding SRL", "cnp": "14399840", "cota": Decimal("40")}],
    [{"nume": "A", "cnp": "1850101400017", "cota": Decimal("50")}, {"nume": "B", "cnp": "", "cota": Decimal("25")},
     {"nume": "C", "cnp": "2850101400019", "cota": Decimal("25")}]])
def test_f6c_m1_cu_mai_multi_asociati_lipsesc_date_fara_suma_cu_motivul(monkeypatch, asociati):
    """[17.5-F6, corecția 1 pct.4, decizia lui Costin 28.11.2026] Cu mai mulți asociați, M1 e «Lipsesc date», fără sumă, cu motivul (simularea
    e pentru un asociat unic: partea fiecăruia, pragurile CASS / D212 și salariul minim pe lună nu sunt calculate)."""
    monkeypatch.setattr(CF, "_asociati", lambda cur, schema: asociati)
    for profil in (MICRO, PROFIT):
        m = CF.m1(None, "s", profil, LA)
        assert m["stare"] == "Lipsesc date" and m["suma"] is None and m["sens"] is None, m
        assert ("%d asociați" % len(asociati)) in m["motiv"] and "D212" in m["motiv"] and "salariul minim" in m["motiv"], m["motiv"]
        assert m["lipsuri"] and m["lipsuri"][0]["unde"] == "verificare manuală"
        assert m["pasi"] == [] and CF.economie_compatibila({"masuri": [m]}) == Decimal("0")


def test_f6c_m1_asociatul_unic_cota_prin_functia_de_format(monkeypatch):
    """[17.5-F6, corecția 1 pct.6, C246] Asociatul unic (100%): pasul bugetului arată cota „100%”, nu notația științifică „1E+2%”; suma rămâne
    calculată (o singură persoană, «Se aplică»)."""
    from core import hotarare_dividende as HD
    monkeypatch.setattr(CF, "_asociati", lambda cur, schema: [{"nume": "Ion Test", "cnp": "1850101400017", "cota": Decimal("100.00")}])
    monkeypatch.setattr(HD, "profit_disponibil", lambda cur, schema, la: Decimal("14600.00"))
    m = CF.m1(None, "s", PROFIT, LA)
    assert m["stare"] == "Se aplică" and m["suma"] is not None, m
    assert "14.600,00 lei × 100% = 14.600,00 lei" in m["pasi"][0], m["pasi"][0]
    assert not re.search(r"\dE[+-]?\d", m["pasi"][0]), m["pasi"][0]


def test_m1_regim_in_afara_v1_si_tip_necompletat():
    assert CF.m1(None, "s", dict(MICRO, regim_fiscal="pfa"), LA)["stare"] == "Nu se aplică"
    assert CF.m1(None, "s", dict(MICRO, tip_firma=""), LA)["stare"] == "Lipsesc date"
    assert CF.m1(None, "s", dict(MICRO, tip_firma="sa"), LA)["stare"] == "Nu se aplică"


def test_m1_cass_pe_dividende_la_praguri_6_12_24():
    sm = Decimal("4050")
    for k in (6, 12, 24):
        assert CF._cass_dividende(sm * k - Decimal("0.01"), sm)[1] == {6: 0, 12: 6, 24: 12}[k]
        assert CF._cass_dividende(sm * k, sm) == (sm * k, k)
        assert CF._cass_dividende(sm * k + Decimal("0.01"), sm)[1] == k


# ───────────────────────── M2 ─────────────────────────
def test_m2_fara_salariati_nu_se_aplica(monkeypatch):
    monkeypatch.setattr(CF, "_salariati_activi", lambda cur, schema, la: [])
    assert CF.m2(None, "s", MICRO, LA)["stare"] == "Nu se aplică"


def test_m2_tichetele_la_cost_egal_dau_net_mai_mare_decat_majorarea(monkeypatch):
    monkeypatch.setattr(CF, "_salariati_activi", lambda cur, schema, la: [{"id": 1, "nume": "Pop", "prenume": "Ana", "brut": Decimal("5000")}])
    m = CF.m2(None, "s", MICRO, LA)
    from core import scadente
    zile = scadente.zile_lucratoare_luna(2026, 11)
    plafon = C.cota("tichet_masa_plafon", LA)[0]
    assert m["stare"] == "Se aplică" and m["valori"]["zile_lucratoare_luna"] == zile and Decimal(m["valori"]["plafon_tichet"]) == plafon
    assert Decimal(m["suma"]) > 0 and m["sens"] == CF.SENS_NET_SALARIATI
    assert Decimal(m["valori"]["plafon_cadou"]) == Decimal("300")


def test_m2_brut_lipsa_e_lipsa_de_date(monkeypatch):
    monkeypatch.setattr(CF, "_salariati_activi", lambda cur, schema, la: [{"id": 1, "nume": "Pop", "prenume": "Ana", "brut": None}])
    m = CF.m2(None, "s", MICRO, LA)
    assert m["stare"] == "Lipsesc date" and m["lipsuri"][0]["unde"] == "Salarizare → Salariați"


# ───────────────────────── economii compatibile, registru, nicio scriere ─────────────────────────
def test_economia_compatibila_aduna_numai_economiile_de_impozit_ale_firmei():
    rez = {"masuri": [{"stare": "Se aplică", "sens": CF.SENS_ECONOMIE_FIRMA, "suma": "4000.00"},
                      {"stare": "Se aplică", "sens": CF.SENS_NET_SALARIATI, "suma": "9000.00"},
                      {"stare": "Se aplică", "sens": CF.SENS_NET_ASOCIAT, "suma": "500.00"},
                      {"stare": "Lipsesc date", "sens": CF.SENS_MARJA, "suma": "100.00"},
                      {"stare": "Se aplică", "sens": CF.SENS_ECONOMIE_FIRMA, "suma": "640.00"},
                      {"stare": "Lipsesc date", "sens": CF.SENS_ESTIMARE_M5, "suma": "665.60"}]}   # [17.5-F6, corecția 1 pct.5] estimarea M5
    assert CF.economie_compatibila(rez) == Decimal("4640.00")


@pytest.mark.parametrize("cheie, fisier, fragment", [
    ("plafon_micro_eur", "cod_fiscal_227_2015_consolidat.txt", "realizează venituri mai mari de 100.000 euro"),
    ("plafon_cadou_ocazie", "cod_fiscal_227_2015_consolidat.txt", "nu depășește 300 lei")])
def test_valorile_noi_ale_registrului_au_citatul_in_sursa_oficiala(cheie, fisier, fragment):
    intrari = C.COTE[cheie]
    assert len(intrari) == 1
    _din, _val, temei = intrari[0]
    text = open(os.path.join(RAD, "anaf_surse", fisier), encoding="utf-8").read()
    assert fragment in temei.text_citat and temei.text_citat in text


def test_fereastra_nu_scrie_nimic():
    src = open(os.path.join(RAD, "core", "consultanta_fiscala.py"), encoding="utf-8").read()
    assert not re.search(r"\b(INSERT|UPDATE|DELETE)\b|\.commit\(", src)


# ───────────────────────── Cabinet 7: garda secțiunii «Consultanță» (probă pozitivă și negativă) ─────────────────────────
def _reguli_f5():
    """Funcția `reguli_f5` din verificator, fără să ruleze întregul verificator la import (scanează tot depozitul)."""
    src = open(os.path.join(RAD, "verificator_conformitate.py"), encoding="utf-8").read()
    arb = ast.parse(src)
    parti = [ast.get_source_segment(src, n) for n in arb.body
             if (isinstance(n, ast.FunctionDef) and n.name == "reguli_f5")
             or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("_RX_F5_SEMNE", "CHEI_CONSULTANTA") for t in n.targets))]
    ns = {"re": re, "os": os}
    exec("\n".join(parti), ns)
    return ns["reguli_f5"]


def test_cabinet7_cardul_de_consultanta_numai_in_sectiunea_lui():
    r = _reguli_f5()
    bun = 'const CARDURI_SEF = ["activitate", "pachete"];\nconst CARDURI_CONSULTANTA = ["hotarari_aga", "consultanta"];\nlet _consultantaDeschis = false;\n'
    assert r({"cabinet.js": bun}) == []
    rau = 'const CARDURI_SEF = ["activitate", "consultanta"];\n'
    assert [x[2] for x in r({"cabinet.js": rau})] == ["F5-CONSULTANTA"]
    rau2 = 'const CARDURI_SEF = ["activitate"];\nlet _consultantaDeschis = true;\n'
    assert [x[2] for x in r({"cabinet.js": rau2})] == ["F5-CONSULTANTA"]


def test_cabinetul_publicat_nu_are_carduri_de_consultanta_in_grila_sau_la_sef():
    r = _reguli_f5()
    cab = open(os.path.join(RAD, "static", "js", "ecrane", "cabinet.js"), encoding="utf-8").read()
    assert [x for x in r({"cabinet.js": cab}) if x[2] == "F5-CONSULTANTA"] == []


def test_cabinet7_grila_principala_si_sectiunea_desenata_f6():
    """[17.5-F6, Cabinet 7] Proba pozitivă și negativă pe forma reală a paginii: grila principală (`DEF`) refuză un card de consultanță;
    secțiunea desenată (`CARDURI_CONSULTANTA`) are cardul fiecărei funcții și pornește pliată."""
    r = _reguli_f5()
    bun = ('const DEF = [\n  { cheie:"validat", titlu:"De validat" },\n  { cheie:"setari", titlu:"Setări cont" },\n];\n'
           'const CARDURI_SEF = ["activitate"];\nconst CARDURI_CONSULTANTA = [\n  { cheie: "hotarari_aga", titlu: "Hotărâri AGA" },\n'
           '  { cheie: "consultanta", titlu: "Consultanță fiscală" },\n];\nlet _consultantaDeschis = false;\n')
    assert r({"cabinet.js": bun}) == []
    in_grila = bun.replace('{ cheie:"setari", titlu:"Setări cont" },', '{ cheie:"setari", titlu:"Setări cont" },\n  { cheie:"consultanta", titlu:"Consultanță fiscală" },')
    assert [(x[2], "grila principală" in x[3]) for x in r({"cabinet.js": in_grila})] == [("F5-CONSULTANTA", True)]
    lipsa = bun.replace('  { cheie: "hotarari_aga", titlu: "Hotărâri AGA" },\n', "")
    assert [(x[2], "lipsește" in x[3]) for x in r({"cabinet.js": lipsa})] == [("F5-CONSULTANTA", True)]
    deschisa = bun.replace("let _consultantaDeschis = false;", "let _consultantaDeschis = true;")
    assert {x[2] for x in r({"cabinet.js": deschisa})} == {"F5-CONSULTANTA"} and all("pliată" in x[3] for x in r({"cabinet.js": deschisa}))
    cab = open(os.path.join(RAD, "static", "js", "ecrane", "cabinet.js"), encoding="utf-8").read()
    assert "const CARDURI_CONSULTANTA" in cab and "const DEF" in cab   # pagina reală are ambele liste: proba de mai sus le citește pe amândouă
    assert [x for x in r({"cabinet.js": cab}) if x[2] == "F5-CONSULTANTA"] == []
