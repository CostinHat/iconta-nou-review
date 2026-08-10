# -*- coding: utf-8 -*-
"""TURA 3 / T2: valideaza(res) era COD MORT. genereaza() chema doar erori_generare(prof),
deci corelatia tip_decont <-> luna (DUK regula R18) ajungea la contabil ca eroare BRUTA a
validatorului la upload, nu ca motiv exact pre-DUK. Aici probam ca genereaza() cableaza
verificarile: blocantele -> ValueError cu motiv exact; marja +-1% -> avertisment, nu blocaj.

Pe HEAD (8b74ccb): _blocante_pre_duk / _avertismente_marja nu exista si genereaza() nu
ridica Valuevalue cu motivul tip_decont -> testele PICA. Dupa cablare -> TREC.
"""
import pytest
from core import d300
from core.common import Perioada

VALID = {"cui": "14399840", "nume": "PROBA SRL", "caen": "6202",
         "banca": "ING Bank", "iban": "RO49AAAA1B31007593840000"}


def test_helperii_de_rutare_exista():
    """Cablarea presupune cele doua functii de rutare pe severitate."""
    assert hasattr(d300, "_blocante_pre_duk"), "lipseste _blocante_pre_duk (T2 necablat)"
    assert hasattr(d300, "_avertismente_marja"), "lipseste _avertismente_marja (T2 necablat)"


def test_tip_decont_A_la_luna_8_e_blocant():
    r = d300.Rezultat(an=2026, luna=8, prof={"tip_decont": "anual"})
    b = d300._blocante_pre_duk(r)
    assert any("tip_decont=A" in m for m in b), b


def test_genereaza_blocheaza_tip_decont_gresit_pre_duk(monkeypatch):
    """genereaza() trebuie sa dea ValueError cu MOTIVUL EXACT (nu R18 brut de la DUK)."""
    prof = dict(VALID, tip_decont="anual")   # anual cere luna=12; cerem luna=8
    monkeypatch.setattr(d300, "pull", lambda conn, schema, perioada: (prof, []))
    with pytest.raises(ValueError) as ei:
        d300.genereaza(None, "tenant_013", Perioada(2026, luna=8))
    assert "tip_decont=A" in str(ei.value), str(ei.value)


def test_marja_e_avertisment_nu_blocaj():
    """O TVA in afara marjei ±1% pe un rand pe cota = avertisment (DUK doar atentioneaza),
    NU blocant. _blocante_pre_duk nu o vede; _avertismente_marja da."""
    res = d300.Rezultat(an=2026, luna=8, prof={"tip_decont": "lunar"},
                        R={"R9_1": 1000, "R9_2": 500})   # 21% din 1000 = 210, nu 500
    assert d300._blocante_pre_duk(res) == []
    av = d300._avertismente_marja(res)
    assert any("R9_2" in m for m in av), av


def test_marja_in_interval_nu_avertizeaza():
    res = d300.Rezultat(an=2026, luna=8, prof={"tip_decont": "lunar"},
                        R={"R9_1": 1000, "R9_2": 210})   # exact 21%
    assert d300._avertismente_marja(res) == []
