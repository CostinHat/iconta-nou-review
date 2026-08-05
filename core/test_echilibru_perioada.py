# -*- coding: utf-8 -*-
"""core/test_echilibru_perioada.py — GARD C3 (integritate in timp): partida dubla pe perioada + orfani."""
import ast
import inspect
from decimal import Decimal
from core.echilibru_perioada import echilibru_perioada, orfani
from core import echilibru_perioada as _mod


def test_echilibru_verde_pe_partida_dubla():
    linii = [{"cont_debit": "4111", "cont_credit": "707", "suma": 1000},
             {"cont_debit": "607", "cont_credit": "401", "suma": 600}]
    sd, sc, ok = echilibru_perioada(linii)
    assert ok and sd == sc == Decimal(1600), (sd, sc)


def test_echilibru_prinde_dezechilibru_MUTATIE():
    """MUTATIE: o linie cu cont_credit LIPSA (parte rupta - editare/import stricat) -> suma intra doar pe debit ->
    Sigma debit != Sigma credit. Exact clasa pe care DUK NU o prinde (accepta GL structural valid dar dezechilibrat)."""
    linii = [{"cont_debit": "4111", "cont_credit": "707", "suma": 1000},
             {"cont_debit": "607", "cont_credit": None, "suma": 600}]   # <- credit lipsa
    sd, sc, ok = echilibru_perioada(linii)
    assert not ok, "dezechilibrul (o parte lipsa) trebuie prins"
    assert sd - sc == Decimal(600), (sd, sc)


def test_orfani_prinde_referinta_rupta():
    linii = [{"inregistrare_id": 1, "suma": 10}, {"inregistrare_id": 99, "suma": 20}]
    orf = orfani(linii, {1, 2, 3})
    assert len(orf) == 1 and orf[0]["inregistrare_id"] == 99


def test_echilibru_e_invariant_pur_nu_recalcul_NON_TAUTOLOGIE():
    """[non-tautologie C3] echilibru_perioada/orfani sunt invarianti CONTABILI pe ledger (Sigma debit=Sigma credit,
    referinta), NU recalcul al vreunui generator - nu apeleaza calcul_salariu / genereaza / d1XX. Verificat pe AST.
    E o proba de INTEGRITATE (o proprietate care trebuie sa tina), nu o confruntare generator-vs-el-insusi."""
    interzis = {"calcul_salariu", "taxe_cm", "genereaza", "calcul_d100", "calcul_d112", "pull"}
    for fn in (echilibru_perioada, orfani, _mod.echilibru_perioada_db):
        t = ast.parse(inspect.getsource(fn))
        nume = {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
        attrs = {n.attr for n in ast.walk(t) if isinstance(n, ast.Attribute)}
        assert not (nume | attrs) & interzis, "%s recalculeaza un generator - nu e invariant pur" % fn.__name__
