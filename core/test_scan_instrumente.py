# -*- coding: utf-8 -*-
"""Garda instrumentului de FAZA 4 (`scripts/scan_instrumente.py`).

Un instrument care masoara calibrarea altor instrumente trebuie sa fie el insusi calibrat, altfel
raportul lui e o opinie. Cazurile de mai jos sunt CUNOSCUTE inainte de masuratoare, si fiecare
corespunde unei forme GRESITE prin care a trecut instrumentul asta intr-o singura zi:

  1. `test_graf_temei.py` ARE calibrare din 01.08.2026 - patru afirmatii pozitive si una negativa.
     Forma 1 a instrumentului o raporta ca ZERO, fiindca cauta cuvantul „calibrare" in docstring.
  2. `scan_ancore` ARE garda din 21.08.2026, dar se numeste `core/test_ancore_in_cod.py`. Forma 2 il
     raporta „fara test propriu", fiindca cauta `core/test_<modul>.py` - o conventie de nume.
  3. Testele lui `graf_temei` importa numele DIRECT si cheama `depinde_de(...)` fara prefix de modul.
     Forma 3 le raporta ca „nu ating instrumentul", fiindca cauta pomenirea numelui de modul.

Toate trei sunt aceeasi familie: o forma de suprafata luata drept fapt. De aceea garda pineaza CAZURI,
nu proprietati.
"""
import ast
import importlib.util
import pathlib

import pytest

_CALE = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "scan_instrumente.py"
_SPEC = importlib.util.spec_from_file_location("scan_instrumente", _CALE)
si = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(si)


def _linie(nume_instrument):
    for n, fis, nt, poz, neg in si.instrumente_si_calibrare():
        if n == nume_instrument:
            return fis, nt, poz, neg
    pytest.fail("instrumentul %s lipseste din inventar" % nume_instrument)


def test_vede_calibrarea_grafului():
    """CAZ 1. `graf_temei` are calibrare in AMBELE directii, din 01.08.2026."""
    fis, nt, poz, neg = _linie("graf_temei.py")
    assert "test_graf_temei.py" in fis, "fisierul de garda al grafului nu e vazut: %s" % fis
    assert poz >= 4, "afirmatiile pozitive ale grafului nu sunt vazute (%d)" % poz
    assert neg >= 1, "afirmatia NEGATIVA a grafului nu e vazuta (%d)" % neg


def test_garda_se_gaseste_si_cand_nu_respecta_conventia_de_nume():
    """CAZ 2. Garda lui `scan_ancore` se numeste `test_ancore_in_cod.py`, nu `test_scan_ancore.py`."""
    fis, nt, poz, neg = _linie("scan_ancore.py")
    assert "test_ancore_in_cod.py" in fis, (
        "garda lui scan_ancore nu e gasita - criteriul s-a intors la numele fisierului: %s" % fis)
    assert neg >= 1, "scan_ancore are calibrare negativa; nu e vazuta"


def test_atingerea_se_vede_si_la_import_direct_de_nume():
    """CAZ 3. `from core.graf_temei import depinde_de` apoi `depinde_de(...)`, fara prefix."""
    src = "from core.graf_temei import depinde_de\n\n\ndef test_x():\n    assert 'a' in depinde_de('c')\n"
    arb = ast.parse(src)
    nume = si.nume_aduse(_FisierFals(src), "graf_temei")
    assert "depinde_de" in nume, "numele importat direct nu e adunat: %s" % nume
    fn = [n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)][0]
    assert si._atinge(fn, nume), "atingerea prin nume importat direct nu e vazuta"


class _FisierFals:
    """Un fisier de test sintetic, ca sa nu depindem de un fisier real pentru cazul 3."""

    def __init__(self, text):
        self._t = text

    def read_text(self, **_k):
        return self._t


def test_calibrarea_nu_se_citeste_din_proza():
    """Cuvantul «calibrare» intr-un docstring NU produce o calibrare; un literal pinuit, DA."""
    doar_proza = ast.parse('def test_x():\n    """CALIBRARE: caz cunoscut."""\n    assert rez\n')
    assert si._clasifica(doar_proza.body[0]) == (0, 0), "proza a fost luata drept calibrare"
    cu_literal = ast.parse('def test_y():\n    assert "a" in rez\n')
    assert si._clasifica(cu_literal.body[0])[0] == 1, "un literal pinuit nu e vazut"


def test_axa_vidului_delega_nu_reimplementeaza():
    """NU exista doua masuratori ale aceleiasi clase - vezi docstringul lui `garzi_vacuabile`."""
    import inspect
    assert "scan_garzi" in inspect.getsource(si.garzi_vacuabile), (
        "axa vidului nu mai deleaga - a reaparut logica paralela")
    rele, tot, culeg, ctrl = si.garzi_vacuabile()
    assert tot > 1000, "denominatorul s-a rupt: doar %d garzi cu asertiuni" % tot
    assert 0 < culeg < tot, "culegatoarele nu se mai disting: %d din %d" % (culeg, tot)
    assert 0 < len(rele) < culeg, "vidul posibil e degenerat: %d din %d" % (len(rele), culeg)
    assert ctrl > 0, "atenuarea prin control pozitiv in modul a disparut"


def test_inventarul_nu_e_gol():
    """ANTI-VACUU pe instrumentul insusi."""
    inv = si.instrumente_si_calibrare()
    assert len(inv) >= 10, "doar %d instrumente gasite - criteriul s-a rupt" % len(inv)
    cu_garzi = [n for n, fis, *_ in inv if fis]
    assert len(cu_garzi) >= 8, "doar %d instrumente au garzi - legatura s-a rupt" % len(cu_garzi)
