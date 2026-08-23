# -*- coding: utf-8 -*-
"""Garda instrumentului de FAZA 4 (`scripts/scan_instrumente.py`).

Un instrument care masoara calibrarea altor instrumente trebuie sa fie el insusi calibrat, altfel
raportul lui e o opinie. Cele doua cazuri de mai jos sunt CUNOSCUTE inainte de masuratoare:

- `test_graf_temei.py` ARE calibrare, scrisa din 01.08.2026: patru afirmatii pozitive pe spina
  salarizare si una negativa (`_q` nu depinde de `tva_standard`). Prima forma a instrumentului o
  raporta ca ZERO, fiindca cauta cuvantul „calibrare" in docstring - clasa pe care faza 4 o numara.
- `test_vigoare_punct.py` pineaza pct. 9 (ORDIN 4.164/2024) si abrogarea pct. 38/39 (ORDIN
  1.447/2023) - doua cazuri concrete, gasite dupa doua reparatii ale instrumentului.

Si un control NEGATIV: garzile care au anti-vacuu explicit nu au voie sa apara ca vacuabile.
"""
import importlib.util
import pathlib

import pytest

_CALE = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "scan_instrumente.py"
_SPEC = importlib.util.spec_from_file_location("scan_instrumente", _CALE)
si = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(si)


def _calib(nume_fisier, modul):
    p = si.RAD / "core" / nume_fisier
    if not p.exists():
        pytest.skip("lipseste %s" % nume_fisier)
    d = si.analizeaza(p, {modul})
    return sum(v[0] for v in d.values()), sum(v[1] for v in d.values())


def test_vede_calibrarea_grafului():
    """CAZ CUNOSCUT. `graf_temei` are calibrare in AMBELE directii, din 01.08.2026."""
    poz, neg = _calib("test_graf_temei.py", "graf_temei")
    assert poz >= 4, "instrumentul nu vede afirmatiile pozitive ale grafului (%d)" % poz
    assert neg >= 1, "instrumentul nu vede afirmatia NEGATIVA a grafului (%d)" % neg


def test_vede_calibrarea_vigorii_pe_punct():
    """CAZ CUNOSCUT. `vigoare_punct` pineaza pct. 9 si abrogarile 38/39."""
    poz, _neg = _calib("test_vigoare_punct.py", "vigoare_punct")
    assert poz >= 2, "instrumentul nu vede cazurile pinuite de vigoare_punct (%d)" % poz


def test_calibrarea_nu_se_citeste_din_proza():
    """Cuvantul «calibrare» intr-un docstring NU produce o calibrare; un literal pinuit, DA."""
    import ast
    doar_proza = ast.parse('def test_x():\n    """CALIBRARE: caz cunoscut."""\n    assert rez\n')
    fn = doar_proza.body[0]
    assert si._clasifica(fn, True) == (0, 0), "proza a fost luata drept calibrare"
    cu_literal = ast.parse('def test_y():\n    assert "a" in rez\n')
    assert si._clasifica(cu_literal.body[0], True)[0] == 1, "un literal pinuit nu e vazut"


def test_controlul_negativ_al_vacuitatii():
    """Garzile cu anti-vacuu explicit nu au voie sa apara ca vacuabile."""
    cand, tot = si.garzi_vacuabile()
    assert tot > 1000, "denominatorul s-a rupt: doar %d garzi cu aserttiuni" % tot
    s = set(cand)
    for k in (("test_conformitate.py", "test_planul_chiar_se_citeste"),
              ("test_vigoare_punct.py", "test_tiparele_de_numerotare_acopera_ambele_acte")):
        assert k not in s, "fals pozitiv pe o garda cu anti-vacuu explicit: %s" % (k,)


def test_inventarul_instrumentelor_nu_e_gol():
    """ANTI-VACUU pe instrumentul insusi."""
    inv = si.instrumente_si_calibrare()
    assert len(inv) >= 10, "doar %d instrumente gasite - criteriul s-a rupt" % len(inv)
    assert any(n == "graf_temei.py" for n, *_ in inv), "graf_temei lipseste din inventar"
