# -*- coding: utf-8 -*-
"""GARD — D300 rd.34 (R31_2) acceptă ajustările introduse de contabil, iar rândurile manuale nu pot purta o coloană
inexistentă în structura ANAF (lot 19, defectul 10, 03.10.2026).

Înainte: R31_2 se calcula DOAR din pro-rata; ajustarea pentru bunuri de capital (CF art.305) nu putea intra în decont
(„rânduri 'manual' neacceptate: ['R31_2']”). Separat, ecranul cerea bază la R29/R35/R36/R38/R39/R43/R44, care n-au
coloana 1 — DUK: „eroare atribut: R29_1: atribut necunoscut”.
"""
import os
import re

import pytest

from core import d300, d300_manual_api
from core.common import Perioada

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {"declarant_functie": "ADMINISTRATOR", "cui": "14399840", "nume": "PROBA SRL", "banca": "BCR",
     "iban": "RO49AAAA1B31007593840000", "cont": "RO49AAAA1B31007593840000", "caen": "4711", "tip_decont": "L",
     "pro_rata": 100, "declarant_nume": "POPESCU", "declarant_prenume": "ION"}


def _calc(manual, facturi=(), **prof):
    return d300.calcul_d300(dict(P, **prof), Perioada(2026, luna=8), list(facturi), manual=manual)


def test_coloanele_sunt_cele_din_structura_anaf():
    t = open(os.path.join(RAD, "anaf_surse/d300_struct_anaf.txt"), encoding="utf-8").read()
    for cod in d300_manual_api.ALLOW:
        are1, are2 = bool(re.search(r"\b%s_1\b" % cod, t)), bool(re.search(r"\b%s_2\b" % cod, t))
        assert (cod in d300.RANDURI_FARA_COL1) == (not are1), cod
        assert (cod in d300.RANDURI_FARA_COL2) == (not are2), cod


def test_ajustarea_art305_intra_in_rd34():
    # OPANAF 174/2026, rd.34: „diferenţele de taxă ... rezultate ca urmare a ajustării taxei deductibile, cu semnul
    # plus sau minus, după caz”
    r = _calc({"R31_2": -3000})
    assert r.R["R31_2"] == -3000 and r.R["R32_2"] == -3000


def test_ajustarea_se_aduna_la_pro_rata_calculata():
    fact = [{"directie": "primita", "linii": [(1, 10000, 21, "mixt")]}]
    fara = _calc({}, fact, pro_rata=80).R.get("R31_2", 0)
    assert fara == -420          # CF art.300 alin.(5)/(11): 2.100 TVA pe achiziția mixtă x (100-80)% -> ajustare -420
    cu = _calc({"R31_2": -500}, fact, pro_rata=80).R["R31_2"]
    assert cu == fara - 500


def test_coloana_inexistenta_e_refuzata_vizibil():
    with pytest.raises(ValueError, match="coloane care nu există"):
        _calc({"R29_1": 1000, "R29_2": 210})
    with pytest.raises(ValueError, match="coloane care nu există"):
        _calc({"R14_2": 100})


def test_ecranul_ofera_r31_fara_baza():
    assert "R31" in d300_manual_api.ALLOW
    # ecranul primește `cu_baza` din aceeași sursă unică pe care o folosește motorul (identitate, nu copie)
    assert d300_manual_api._FARA_BAZA is d300.RANDURI_FARA_COL1 and d300_manual_api._FARA_TVA is d300.RANDURI_FARA_COL2


def test_coloanele_inexistente_sunt_respinse_de_duk():
    """Ancora seturilor RANDURI_FARA_COL1/2 pe validatorul INSTALAT: fiecare coloană declarată inexistentă, pusă în XML
    (ocolind garda din calcul_d300), e respinsă de DUK ca „atribut necunoscut”."""
    from core import duk
    r = _calc({})
    for cod in d300.RANDURI_FARA_COL1:
        r.R[cod + "_1"] = 100
    for cod in d300.RANDURI_FARA_COL2:
        r.R[cod + "_2"] = 21
    erori = duk.valideaza(d300.build_xml(r), "d300", an=2026, luna=8, timeout=110).get("erori") or ""
    nerespinse = sorted(c for c in ([x + "_1" for x in d300.RANDURI_FARA_COL1] + [x + "_2" for x in d300.RANDURI_FARA_COL2])
                        if "atribut necunoscut ('%s')" % c not in erori)
    assert nerespinse == [], "coloane declarate inexistente pe care DUK le acceptă: %s" % nerespinse


def test_r31_manual_valid_pe_duk():
    from core import duk
    r = _calc({"R31_2": -3000, "R18_1": 10000, "R18_2": 2100, "R5_1": 10000, "R5_2": 2100})
    rez = duk.valideaza(d300.build_xml(r), "d300", an=2026, luna=8, timeout=110)
    assert rez["stare"] == "valid", rez.get("erori")
