# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E3 — scenariile de server ale numerelor: 681.2 (căutarea pe sens, tot catalogul de ecrane), 724.2 / 734 (datele), 728.1 / 735 (acțiunea și
textul din aceeași intrare de catalog)."""
import datetime
import os
import re

import pytest

from core import cautare as C, luna_preluare as LP

FIRMA = {"tenant_id": 1, "tip_firma": "srl"}
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _titluri(q, firma=FIRMA, n=5):
    return [r["titlu"] for r in C.cauta(q, firma)[:n]]


def test_681_2_stat_duce_la_statul_de_plata_nu_la_d100():
    assert _titluri("stat")[0] == "Stat de plată"
    assert _titluri("stat de plată")[0] == "Stat de plată"


@pytest.mark.parametrize("q,asteptat", [("povestea", "Pachete lunare — povestea lunii"), ("audit", "Audit de preluare"), ("tipare", "Tipare de erori"),
                                        ("istoric", "Istoric facturi")])
def test_681_2_catalogul_cuprinde_ecranele_cu_titlul_si_cuvintele_lor(q, asteptat):
    assert _titluri(q)[0] == asteptat


def test_681_2_reg_duce_la_registre():
    srl = _titluri("reg", FIRMA, 2)
    assert srl == ["Registru jurnal", "Registrul-inventar"], srl
    pfa = _titluri("reg", dict(FIRMA, tip_firma="pfa"), 1)
    assert pfa == ["Registru încasări/plăți"], pfa


def test_681_2_fiecare_ecran_din_catalog_are_pasii_lui():
    e = C.ecrane_catalog()
    assert len(e) >= 35 and all(x["pasi"] and x["titlu"] for x in e), len(e)
    ist = next(x for x in e if x["titlu"] == "Istoric facturi")
    assert ist["pasi"][-1]["click"] == "#fac-istoric" and ist["firma"] is True
    ecr_cab = next(x for x in e if x["titlu"] == "Tipare de erori")
    assert ecr_cab["firma"] is False


def test_724_2_luna_preluarii_nu_e_inaintea_infiintarii():
    # F2: înființată 15.03.2026, adăugată în iConta 21.09.2026, prima notă din 12/2025 — textul spunea 12/2025
    luna = LP.efectiva(None, datetime.date(2026, 9, 21), None, datetime.date(2025, 12, 31), datetime.date(2026, 3, 15))
    assert luna == (2026, 3)
    fapte = {"salvata": None, "creat_la": datetime.date(2026, 9, 21), "data_solduri": None, "prima_nota": datetime.date(2025, 12, 31), "infiintare": datetime.date(2026, 3, 15)}
    assert LP.din_fapte(fapte) == (2026, 3) and "înființării" in LP.de_unde_fapte(fapte)
    assert LP.eroare(datetime.date(2026, 1, 1), None, datetime.date(2026, 3, 15)), "o lună salvată înaintea înființării se refuză lângă câmp"
    # fără data înființării regula nu se aplică (comportamentul de până acum)
    assert LP.efectiva(None, datetime.date(2026, 9, 21), None, datetime.date(2025, 12, 31), None) == (2025, 12)


def test_734_nicio_verificare_nu_se_raporteaza_la_o_data_din_viitor():
    """Coerența TVA din balanță se judecă la sfârșitul ultimei luni ÎNCHEIATE: azi 02.11.2026 -> 31.10.2026, niciodată 30.11.2026."""
    from core import control_fiscal_api, uc_comun
    an_c, luna_c = control_fiscal_api.luna_confruntata(2026, 11)
    tva = {"suma": 0}
    uc_comun._tva_cu_perioada(tva, {}, an_c, luna_c)
    assert tva["la_data"] == "2026-10-31", tva


def test_728_1_orice_cod_de_actiune_al_serverului_are_intrare_in_catalogul_ecranului():
    """Textul și butonul vin din aceeași intrare: codurile `cod` emise de server pe remedii (control_incrucisat, audit_preluare) există toate în ACTIUNI_REMEDIU."""
    js = open(os.path.join(_RAD, "static", "js", "ecrane", "control_verdict.js"), encoding="utf-8").read()
    bloc = js[js.index("export const ACTIUNI_REMEDIU = {"):js.index("};", js.index("export const ACTIUNI_REMEDIU = {"))]
    chei = set(re.findall(r"^\s{2}(\w+): \{", bloc, re.M))
    emise = set()
    for f in ("control_incrucisat.py", "audit_preluare.py"):
        emise |= set(re.findall(r'"cod": "(\w+)"', open(os.path.join(_RAD, "core", f), encoding="utf-8").read()))
    assert emise and emise <= chei, (emise, chei)
    # fiecare intrare spune și „ce e de făcut” și eticheta butonului: aceeași intrare, deci nu pot diferi
    for k in emise:
        assert re.search(k + r": \{[^}]*deFacut: \"[^\"]+\"[^}]*eticheta: \"[^\"]+\"", bloc) or re.search(k + r": \{[^}]*eticheta: \"[^\"]+\"[^}]*deFacut", bloc), k
