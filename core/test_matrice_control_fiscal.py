# -*- coding: utf-8 -*-
"""Matrice de stari pe logica de DECIZIE a control fiscal (declaratii_datorate + declaratii_fapt), PURA.
Aserții pe FORMĂ, nu pe valori. NU testeaza UI, NU repara nimic - doar constata.
Dimensiuni: tip_firma x platitor_tva x salariati x perioada(azi) x D205. operatiuni_ic tinut FALSE
(nu e in matricea ceruta -> D390/D301 nu se exercita; vezi raport). Verde/confirmate NU se produc pe
calea pura (cer `depuse`/DB) -> in afara acoperirii; aici doar restante(datorate)/neaplicabile/neclar.
"""
import pytest
from datetime import date
from core import control_fiscal_api as cf
from core import control_incrucisat as ci
from core.migrare_api import regim_contabil

TVA_ONLY = {"d300", "d394"}          # depind de platitor_tva
JURIDIC_ONLY = {"d100", "d101", "d406"}   # persoana juridica / partida dubla


def _combinat(tip_firma, platitor_tva, salariati, azi, d205_note, monkeypatch):
    partida_simpla = regim_contabil(tip_firma) == "simpla"
    vector = {
        "tip_firma": tip_firma,
        "regim_fiscal": None if partida_simpla else "profit",
        "platitor_tva": platitor_tva,
        "tip_decont": "lunar" if platitor_tva else None,
        "operatiuni_ic": False,
        "partida_simpla": partida_simpla,
    }
    rez = cf.declaratii_datorate(vector, are_salariati=(salariati > 0), azi=azi)
    # D205/D301 pe fapt: mock-uim cei doi helperi DB (conn ignorat)
    monkeypatch.setattr(ci, "dividende_distribuite",
                        lambda *a, **k: ((5000, True) if d205_note else (0, False)))
    monkeypatch.setattr(ci, "d301_luni_operatiuni", lambda *a, **k: set())
    fapt = cf.declaratii_fapt(None, "x", vector, azi)
    datorate = rez["datorate"] + fapt["datorate"]
    neaplicabile = rez["neaplicabile"] + fapt["neaplicabile"]
    neclar = rez["neclar"] + fapt["neclar"]
    return partida_simpla, datorate, neaplicabile, neclar


@pytest.mark.parametrize("tip_firma", ["srl", "pfa"])
@pytest.mark.parametrize("platitor_tva", [True, False])
@pytest.mark.parametrize("salariati", [0, 3])
@pytest.mark.parametrize("azi", [date(2026, 7, 23), date(2026, 2, 15)])   # perioada (proxy pe azi)
@pytest.mark.parametrize("d205_note", [False, True])
def test_matrice_forma(tip_firma, platitor_tva, salariati, azi, d205_note, monkeypatch):
    partida_simpla, datorate, neaplicabile, neclar = _combinat(
        tip_firma, platitor_tva, salariati, azi, d205_note, monkeypatch)
    dat = {d["tip"] for d in datorate}
    neap = {d["tip"] for d in neaplicabile}
    rupt = []

    # A2: nicio declaratie simultan datorate(restante) SI neaplicabile
    if dat & neap:
        rupt.append("A2 dublu datorate+neaplicabile: %s" % sorted(dat & neap))

    # A1/A3: fiecare verdict are temei explicit; gri fara temei = fail
    for d in neclar:                       # gri
        if not (d.get("cauza") or d.get("motiv")):
            rupt.append("A3 gri fara temei: %s" % d.get("tip"))
    for d in neaplicabile:                 # nu se datoreaza
        if not d.get("motiv"):
            rupt.append("A1 neaplicabil fara temei: %s" % d.get("tip"))
    for d in datorate:                     # restanta
        if not (d.get("perioada") and d.get("termen")):
            rupt.append("A1 datorat fara perioada/termen: %s" % d.get("tip"))

    # A4: pfa => zero D100/D101/D406 in datorate (trebuie neaplicabile)
    if partida_simpla and (JURIDIC_ONLY & dat):
        rupt.append("A4 pfa cu D100/D101/D406 datorate: %s" % sorted(JURIDIC_ONLY & dat))

    # A5: neplatitor TVA => zero D300/D394 (D390 tinut in afara: operatiuni_ic=False)
    if not platitor_tva and (TVA_ONLY & dat):
        rupt.append("A5 neplatitor cu D300/D394 datorate: %s" % sorted(TVA_ONLY & dat))

    # A6: zero salariati => zero D112
    if salariati == 0 and "d112" in dat:
        rupt.append("A6 zero salariati cu D112 datorat")

    if rupt:
        pytest.fail("[%s tva=%s sal=%s azi=%s d205=%s] " % (
            tip_firma, platitor_tva, salariati, azi, d205_note) + " | ".join(rupt))
