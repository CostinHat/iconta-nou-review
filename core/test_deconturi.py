# -*- coding: utf-8 -*-
"""Gard pe plafonul neimpozabil al diurnei (motor pur core/deconturi.py).

TEMEI: CF art.76 alin.(2) lit.k + alin.(4^1) - diurna neimpozabila = min(2,5 x diurna bugetara
stabilita prin HG pt institutii publice; 3 x salariu de baza / zile lucratoare din luna) x zile
deplasare; excedentul = venit salarial. Calculul PENTRU PERIOADA CURENTA (2023+) e conform;
period-awareness istorica (pre-2023) e datorie (vezi test_datorie), blocata pe valorile HG diurna
care nu sunt in surse.
"""
from decimal import Decimal
from datetime import date
from core.deconturi import plafon_diurna


def test_plafon_diurna_curent_conform_art76():
    # 2026: diurna bugetara 23 lei -> limita 2,5x = 57,50 lei/zi (art.76 alin.4^1).
    # salariu 6000, 21 zile lucratoare, 3 zile deplasare, diurna acordata 100/zi.
    # p2 = 3*6000/21 = 857,14/zi (nerestrictiv aici); plafon_zi = min(57,50; 857,14) = 57,50.
    r = plafon_diurna(100, 3, 6000, 21, la_data=date(2026, 6, 1))
    assert r["limita_2_5x"] == Decimal("57.50"), r
    assert r["plafon_zi"] == Decimal("57.50"), r
    assert r["neimpozabil"] == Decimal("172.50"), r      # 57,50 * 3
    assert r["impozabil"] == Decimal("127.50"), r        # (100-57,50)*3


def test_plafon_diurna_capul_3_salarii_musca_pe_salariu_mic():
    # Salariu mic -> capul "3 salarii/zile lucratoare" devine restrictiv (< 2,5x).
    # salariu 1500, 21 zile: p2 = 3*1500/21 = 214,29/zi; inca > 57,50, deci 2,5x castiga.
    # salariu 400, 21 zile: p2 = 3*400/21 = 57,14 < 57,50 -> capul 3-salarii musca.
    r = plafon_diurna(100, 2, 400, 21, la_data=date(2026, 6, 1))
    assert r["limita_3_salarii"] == Decimal("57.14"), r
    assert r["plafon_zi"] == Decimal("57.14"), r         # min(57,50; 57,14)
