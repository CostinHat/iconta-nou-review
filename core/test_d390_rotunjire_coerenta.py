# -*- coding: utf-8 -*-
"""Gard D390 (10.08.2026): rezumatul (bazaL..bazaR, total_baza) trebuie sa fie suma bazelor
ROTUNJITE PE OPERATIE — exact valorile intregi emise in <operatie baza=...> — NU rotunjirea
sumei brute in Decimal.

Temei OFICIAL (structura_D390_2020_180320, OPANAF 705/2020): total_baza = Sum(operatie(baza)) si
bazaL = Sum(operatie(baza)) pt tip=L. Validatorul ANAF D390_11 impune structural DUK regula R16:
`bazaL = Suma(baza pt. tip = L)` peste operatiile (deja intregi) din XML.

Bug prins: la baze fractionare, codul rotunjea individual fiecare <operatie> DAR calcula rezumatul
prin rotunjirea sumei brute Decimal -> divergenta. Ex.: 2 operatori DISTINCTI, baza 1000.50 fiecare:
  operatie: _int(1000.50)=1001, 1001  -> Sum = 2002
  bazaL vechi: _int(1000.50+1000.50)=_int(2001.00)=2001  -> R16 respins de DUK
Probat DUK pre-fix: "R16: bazaL ('2001') = Suma(baza pt. tip = L) ('2002')".
"""
from core import d390

_PROF = {"cui": "304444002", "nume": "TEST SRL"}


def _res_doi_operatori_fractionari():
    facturi = [
        {"cui": "DE136695976", "nume": "PARTNER EINS GMBH", "directie": "emisa", "total": 1000.50, "tva": 0},
        {"cui": "DE811193231", "nume": "PARTNER ZWEI GMBH", "directie": "emisa", "total": 1000.50, "tva": 0},
    ]
    return d390.calcul_d390(_PROF, 2026, 8, facturi)


def test_bazaL_egal_cu_suma_bazelor_emise_pe_operatie():
    res = _res_doi_operatori_fractionari()
    suma_op_L = sum(b for (tip, _, _, _), b in res.ops.items() if tip == "L")
    # pe codul vechi: bazaL=2001, suma_op_L=2002 -> AssertionError (R16 ar fi respins de ANAF)
    assert res.rezumat["L"] == suma_op_L
    assert res.rezumat["L"] == 2002


def test_total_baza_egal_cu_suma_tuturor_operatiilor():
    res = _res_doi_operatori_fractionari()
    assert res.total_baza == sum(res.ops.values())
    assert res.total_baza == res.rezumat["L"] + res.rezumat["T"] + res.rezumat["A"] \
        + res.rezumat["P"] + res.rezumat["S"] + res.rezumat["R"]
    assert res.total_baza == 2002


def test_totalPlata_A_pe_rezumatul_coerent():
    res = _res_doi_operatori_fractionari()
    assert res.total_plata_a == res.nr_opi + res.rezumat["L"] + res.rezumat["T"] \
        + res.rezumat["A"] + res.rezumat["P"] + res.rezumat["S"] + res.rezumat["R"]
    assert res.total_plata_a == 2004
