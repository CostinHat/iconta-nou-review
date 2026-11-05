# -*- coding: utf-8 -*-
"""GARD (comanda 16.5, C223) — măsura „valoare” a oracolului (scripts/verifica_pas.py): un câmp de formular se judecă prin valoare, nu prin text. Test pur, fără Chromium:
sentinela întoarsă de măsură pentru un element fără valoare sau un selector fără element dă „pică” cu motivul ei pentru orice operator (inclusiv „lipseste”), iar valorile obișnuite
se compară ca până acum. Citirea propriu-zisă din pagină se calibrează în scripts/calibreaza_16_5.py (cere Chromium)."""
import os
import sys

import pytest

_SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")


@pytest.fixture
def VP(monkeypatch):
    monkeypatch.syspath_prepend(_SCRIPTS)
    import verifica_pas
    return verifica_pas


def test_valoare_este_o_masura_cunoscuta(VP):
    assert "valoare" in VP.MASURI


@pytest.mark.parametrize("operator", ["egal", "contine", "lipseste", "text_contine", "nr_randuri", "activ", "interval_px"])
@pytest.mark.parametrize("motiv", ["elementul nu are valoare", "niciun element pentru selector"])
def test_sentinela_pica_cu_motivul_ei_pentru_orice_operator(VP, operator, motiv):
    verdict, text = VP.compara_asertiune(operator, "" if operator in ("egal", "contine", "lipseste") else "1", {VP.CHEIE_FARA_VALOARE: motiv})
    assert verdict == "pica" and text == motiv


def test_alt_dict_nu_e_sentinela(VP):
    assert VP.compara_asertiune("nr_randuri", "1", {"a": 1})[0] == "trece"


def test_valori_obisnuite_se_compara_ca_inainte(VP):
    assert VP.compara_asertiune("egal", "2026-11-03", "2026-11-03")[0] == "trece"
    verdict, motiv = VP.compara_asertiune("egal", "2026-11-04", "2026-11-03")
    assert verdict == "pica" and "2026-11-03" in motiv
    assert VP.compara_asertiune("egal", "", "")[0] == "trece"
    assert VP.compara_asertiune("contine", "b", "a,b")[0] == "trece"
