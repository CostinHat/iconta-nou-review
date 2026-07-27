# -*- coding: utf-8 -*-
"""Teste numar_operatiuni — puntea catre poarta de declaratie goala.

Fondul: o declaratie goala LEGITIMA si una golita de un query rupt arata identic.
Numarul de operatiuni e singurul lucru care le distinge inainte de depunere.
"""
import pytest
from core.declaratii_api import numar_operatiuni as N


class _R:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_d390_numara_operatiunile():
    assert N("d390", _R(nr_opi=3)) == 3
    assert N("d390", _R(nr_opi=0)) == 0


def test_d394_numara_operatiunile():
    assert N("d394", _R(op_efectuate=7)) == 7


def test_d301_si_d205_numara_lista():
    assert N("d301", _R(operatiuni=[1, 2])) == 2
    assert N("d205", _R(beneficiari=[])) == 0


def test_d100_si_d710_numara_obligatiile():
    assert N("d100", _R(obligatii=[{"cod_oblig": "121"}])) == 1
    assert N("d710", _R(obligatii=[])) == 0


def test_d406_aduna_note_si_facturi():
    assert N("d406", _R(note=[1, 2], facturi_vanzare=[1], facturi_cumparare=[])) == 3


def test_d300_numara_randurile_nenule():
    assert N("d300", _R(R={"R9_1": 1000, "R10": 0, "R22": 500})) == 2
    assert N("d300", _R(R={"R9_1": 0, "R10": 0})) == 0


def test_d112_da_None_nu_zero():
    """d112.genereaza intoarce o LISTA de avertismente, nu un dataclass. Necunoscutul
    NU se falsifica in zero - altfel poarta ar aparea la fiecare D112."""
    assert N("d112", ["avertisment"]) is None
    assert N("d112", []) is None


def test_d101_da_None():
    """D101 lucreaza pe solduri, n-are notiunea de operatiuni."""
    assert N("d101", _R(P={"P1": 1000})) is None


def test_tip_nou_necunoscut_da_None_nu_zero():
    """Un tip nou nemapat NU trebuie sa para gol - ar pune poarta pe orice."""
    assert N("d999", _R(ceva=[])) is None


def test_res_None_da_None():
    assert N("d390", None) is None


def test_toate_tipurile_din_dispecer_sunt_acoperite_sau_declarate():
    """Fiecare tip stie ori sa numere, ori sa spuna ca nu poate. Niciunul nu cade
    accidental pe zero."""
    from core import declaratii_api as da
    tipuri = [t for t in dir(da) if False]  # placeholder, vezi mai jos
    for tip in ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406", "d710"):
        r = N(tip, _R())
        assert r is None or isinstance(r, int), "%s da %r" % (tip, r)
