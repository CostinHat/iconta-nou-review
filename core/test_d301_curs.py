# -*- coding: utf-8 -*-
"""
Gard anti-fabricare a cursului de schimb in D301 (cluster "baza = val x curs").

TEMEI: CF art.290 alin.(2) — pentru o operatiune (alta decat importul) cu elemente
exprimate in valuta, cursul aplicat este ultimul curs BNR / BCE ori cel al bancii de
decontare, VALABIL LA DATA EXIGIBILITATII. Cursul e un NUMAR REAL > 0; pentru RON e 1
(RON->RON), dar pentru valuta trebuie completat de contabil (§8 CLAUDE.md).

DEFECT reparat: calc_baza primea 'curs or 1' din generator (d301.py) si din reader
(d301_operatiuni_api.lista). Un curs absent/0 pe o operatiune in EUR (moneda default)
devenea tacit curs=1 -> baza = valoarea in valuta, SUBEVALUATA, trimisa la ANAF fara
nicio eroare (clasa 'valoare gresita tacuta'). calc_baza refuza acum curs None/<=0.
"""
import pytest
from core import d301
from core.d301 import calc_baza
from core.common import Perioada


def test_calc_baza_refuza_curs_absent_sau_nul():
    # CF art.290 alin.(2): cursul e un numar real > 0. Absent/0/negativ = eroare, nu 1.
    for rau in (None, 0, 0.0, "", -1):
        with pytest.raises(ValueError):
            calc_baza(1000, rau)


def test_calc_baza_corect_pe_curs_valid():
    # 1000 EUR x 4.9770 = 4977.0 -> 4977 lei (ROUND_HALF_UP la leu intreg).
    assert calc_baza(1000, "4.9770") == 4977
    # RON: cursul e 1 (dat ca data), baza = valoarea.
    assert calc_baza(1234, 1) == 1234


def test_generator_d301_refuza_curs_lipsa_pe_valuta():
    # Operatiune in EUR fara curs: INAINTE producea baza=1000 tacut; ACUM ridica.
    PROF = {"nume": "T SRL", "cui": "14399840", "banca": "BCR", "iban": "RO49AAAA1B31007593840000"}
    op = {"tip": 1, "nr_doc": "F1", "data_doc": "10.06.2026",
          "val_valuta": 1000, "tip_valuta": "EUR", "curs": None, "tva": 210}
    with pytest.raises(ValueError):
        d301.calcul_d301(PROF, Perioada(2026, luna=6), [op])


class _FakeCur:
    def __init__(self, rows): self._rows = rows
    def execute(self, *a, **k): pass
    def fetchall(self): return self._rows
    def __enter__(self): return self
    def __exit__(self, *a): return False


class _FakeConn:
    def __init__(self, rows): self._rows = rows
    def cursor(self, **k): return _FakeCur(self._rows)


def test_lista_api_refuza_curs_nul_nu_fabrica_1():
    # Reader-ul grilei: o linie cu curs NULL nu se mai afiseaza cu baza fabricata (curs=1).
    from core import d301_operatiuni_api as api
    rand = {"id": 1, "tip": 1, "nr_doc": "F1", "data_doc": "10.06.2026",
            "val_valuta": 1000, "tip_valuta": "EUR", "curs": None, "tva": 210}
    with pytest.raises(ValueError):
        api.lista(_FakeConn([rand]), "public", 2026, 6)
