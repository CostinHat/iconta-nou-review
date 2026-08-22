# -*- coding: utf-8 -*-
"""d100: rata default micro(1%)/profit(16%) vine din cota (impozit_micro/impozit_profit), NU din literalul
hardcodat 1/16 (dependenta ascunsa V2). Rata data explicit de contabil (manual) ramane prioritara.
Helper cu nume UNIC (_rata_impozit_default) ca dependenta sa fie vizibila in graf (genereaza se ciocneste
pe nume cu alte module)."""

# [R17 23.08.2026] Cheile grafului sunt CALIFICATE ("fisier.py::nume") de cand `graf_temei` nu mai
# conflateaza functii omonime din fisiere diferite. Afirmatiile de mai jos numesc acum si FISIERUL:
# inainte treceau daca ORICE functie din core/ cu numele cerut aparea in graf.
import ast
import pathlib
from datetime import date

from core import common as c
from core.graf_temei import depinde_de


def test_cotele_micro_profit_in_registru():
    assert float(c.cota("impozit_micro", date(2026, 6, 1))[0]) == 0.01     # micro 1% standard (CF art.51)
    assert float(c.cota("impozit_profit", date(2026, 6, 1))[0]) == 0.16    # profit 16% (CF art.17)


def test_d100_rata_default_prin_helper_nu_literal():
    """Derivarea obligatiilor traieste in deriva_obligatii (sursa unica genereaza + thunk reconciliere)
    si deleaga rata default catre _rata_impozit_default (nu literal 1/16); genereaza ruteaza prin ea."""
    src = pathlib.Path("core/d100.py").read_text(encoding="utf-8")
    fdefs = {n.name: n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}
    calls_deriva = [(getattr(x.func, "attr", None) or getattr(x.func, "id", None))
                    for x in ast.walk(fdefs["deriva_obligatii"]) if isinstance(x, ast.Call)]
    assert "_rata_impozit_default" in calls_deriva, "deriva_obligatii nu deleaga rata default catre helper"
    calls_gen = [(getattr(x.func, "attr", None) or getattr(x.func, "id", None))
                 for x in ast.walk(fdefs["genereaza"]) if isinstance(x, ast.Call)]
    assert "deriva_obligatii" in calls_gen, "genereaza nu ruteaza derivarea obligatiilor prin deriva_obligatii"


def test_d100_apare_in_graful_impozit():
    """Dupa reroute: graful vede d100 depinzand de impozit_micro/profit (V2 blind-spot inchis)."""
    assert "d100.py::_rata_impozit_default" in depinde_de("impozit_profit")
    assert "d100.py::_rata_impozit_default" in depinde_de("impozit_micro")
