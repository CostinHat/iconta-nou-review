# -*- coding: utf-8 -*-
"""Matrice de stari pe control fiscal - PURA, aserții pe FORMĂ (nu valori). NU testeaza UI, NU repara.
Dimensiuni (6): tip_firma x platitor_tva x salariati x operatiuni_ic x D205 x depuse = 64 config.
Acopera calea VERDE (confirmate) prin _clasifica cu `depuse` (fapt de depunere) - temeiul verde inclus.
declaratii_datorate + declaratii_fapt (helperi D205/D301 mock-uiti) + _clasifica (lipsa/urmarit/confirmate).
"""
import pytest
from datetime import date
from core import control_fiscal_api as cf
from core import control_incrucisat as ci
from core.migrare_api import regim_contabil

TVA_ONLY = {"d300", "d394"}
JURIDIC_ONLY = {"d100", "d101", "d406"}
AZI = date(2026, 7, 23)


def _stari(tip_firma, platitor_tva, salariati, operatiuni_ic, d205_note, depuse_toate, monkeypatch):
    partida_simpla = regim_contabil(tip_firma) == "simpla"
    vector = {
        "tip_firma": tip_firma,
        "regim_fiscal": None if partida_simpla else "profit",
        "platitor_tva": platitor_tva,
        "tip_decont": "lunar" if platitor_tva else None,
        "operatiuni_ic": operatiuni_ic,
        "partida_simpla": partida_simpla,
        "tva_data_inceput": None,
    }
    rez = cf.declaratii_datorate(vector, are_salariati=(salariati > 0), azi=AZI)
    monkeypatch.setattr(ci, "dividende_distribuite",
                        lambda *a, **k: ((5000, True) if d205_note else (0, False)))
    monkeypatch.setattr(ci, "d301_luni_operatiuni", lambda *a, **k: set())
    fapt = cf.declaratii_fapt(None, "x", vector, AZI)
    datorate = rez["datorate"] + fapt["datorate"]
    neaplicabile = rez["neaplicabile"] + fapt["neaplicabile"]
    neclar = rez["neclar"] + fapt["neclar"]
    # depuse: fapt de depunere -> calea VERDE (confirmate). "toate" = tot ce e datorat a fost depus.
    depuse = {(d["tip"], d["an"], d["luna"]): AZI for d in datorate} if depuse_toate else {}
    lipsa, urmarit, confirmate = cf._clasifica(datorate, depuse, AZI)
    return partida_simpla, datorate, lipsa, urmarit, confirmate, neaplicabile, neclar


@pytest.mark.parametrize("tip_firma", ["srl", "pfa"])
@pytest.mark.parametrize("platitor_tva", [True, False])
@pytest.mark.parametrize("salariati", [0, 3])
@pytest.mark.parametrize("operatiuni_ic", [False, True])
@pytest.mark.parametrize("d205_note", [False, True])
@pytest.mark.parametrize("depuse_toate", [False, True])
def test_matrice_forma(tip_firma, platitor_tva, salariati, operatiuni_ic, d205_note, depuse_toate, monkeypatch):
    partida_simpla, datorate, lipsa, urmarit, confirmate, neaplicabile, neclar = _stari(
        tip_firma, platitor_tva, salariati, operatiuni_ic, d205_note, depuse_toate, monkeypatch)
    dat = {d["tip"] for d in datorate}
    neap = {d["tip"] for d in neaplicabile}
    rupt = []

    # A2: nicio declaratie simultan datorate(restante) SI neaplicabile
    if dat & neap:
        rupt.append("A2 dublu datorate+neaplicabile: %s" % sorted(dat & neap))

    # A1/A3: FIECARE verdict are temei explicit — inclusiv VERDE (confirmate) si GRI (neclar)
    for d in confirmate:                       # VERDE: motiv = "Depusă ..." (info noua, nu duplica antetul)
        if not d.get("motiv"):
            rupt.append("A1 verde fara temei: %s" % d.get("tip"))
    for d in lipsa + urmarit:                  # rosu/galben: temei STRUCTURAT (antet: perioada + termen), C1
        if not (d.get("perioada") and d.get("termen")):
            rupt.append("A1 restanta/urmarit fara perioada/termen: %s" % d.get("tip"))
    for d in neclar:                           # GRI
        if not (d.get("cauza") or d.get("motiv")):
            rupt.append("A3 gri fara temei: %s" % d.get("tip"))
    for d in neaplicabile:                     # nu se datoreaza
        if not d.get("motiv"):
            rupt.append("A1 neaplicabil fara temei: %s" % d.get("tip"))

    # A4: pfa => zero D100/D101/D406 in datorate (trebuie neaplicabile)
    if partida_simpla and (JURIDIC_ONLY & dat):
        rupt.append("A4 pfa cu D100/D101/D406 datorate: %s" % sorted(JURIDIC_ONLY & dat))

    # A5: neplatitor TVA => zero D300/D394 (D390 RETRAS din aserție — vezi B2/A7)
    if not platitor_tva and (TVA_ONLY & dat):
        rupt.append("A5 neplatitor cu D300/D394 datorate: %s" % sorted(TVA_ONLY & dat))

    # A6: zero salariati => zero D112
    if salariati == 0 and "d112" in dat:
        rupt.append("A6 zero salariati cu D112 datorat")

    # A7 [B2]: neplatitor + operatiuni IC => D390 NU e datorat tacit, e GRI cu temei (art.316/317 necunoscut)
    if not platitor_tva and operatiuni_ic:
        if "d390" in dat:
            rupt.append("A7 D390 datorat tacit la neplatitor")
        gri_d390 = [d for d in neclar if d["tip"] == "d390"]
        if not (gri_d390 and (gri_d390[0].get("cauza") or gri_d390[0].get("motiv"))):
            rupt.append("A7 D390 neemis fara gri/temei la neplatitor cu IC")

    if rupt:
        pytest.fail("[%s tva=%s sal=%s ic=%s d205=%s dep=%s] " % (
            tip_firma, platitor_tva, salariati, operatiuni_ic, d205_note, depuse_toate) + " | ".join(rupt))


# ---- REGRESIE tenant_001 (UndefinedTable in termene): faptul D390 doar la platitor ----
@pytest.mark.parametrize("tip_firma", ["srl", "pfa"])
@pytest.mark.parametrize("platitor_tva", [True, False, None])
@pytest.mark.parametrize("operatiuni_ic", [True, False, None])
def test_d390_fapt_consultat_doar_la_platitor(tip_firma, platitor_tva, operatiuni_ic):
    """Faptul D390 (d390_fapt -> DB per luna) se consulta DOAR la platitori (art. 316). Un neplatitor nu are
    D390 pe fapt (obligatia depinde de art. 317, nu de facturi). Altfel o schema incompleta (ex. d301_operatiuni
    lipsa la un tenant vechi de partida simpla) rupe evaluarea -> firma cade in neevaluate. Poarta = platitor_tva.
    Aserția care ar fi prins regresia din 01b353b (bucla neplatitor apela faptul)."""
    partida_simpla = regim_contabil(tip_firma) == "simpla"
    vector = {"tip_firma": tip_firma, "regim_fiscal": None if partida_simpla else "profit",
              "platitor_tva": platitor_tva, "tip_decont": "lunar" if platitor_tva else None,
              "operatiuni_ic": operatiuni_ic, "partida_simpla": partida_simpla, "tva_data_inceput": None}
    apeluri = []
    def fapt(a, m):
        apeluri.append((a, m)); return None
    cf.obligatii_datorate(vector, are_salariati=False, azi=AZI, d390_fapt=fapt)
    if platitor_tva is not True:
        assert apeluri == [], "d390_fapt apelat la non-platitor (platitor=%r): %s" % (platitor_tva, apeluri[:3])
