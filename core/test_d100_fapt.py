# -*- coding: utf-8 -*-
"""[Regula 13 + Regula 6] GARDA: D100 micro pe FAPT (baza de venituri), simetric cu d390_fapt/d112_fapt.

Bug (audit tenant_006, 18.08.2026): semaforul arata D100 micro RESTANTA pe orice trimestru inchis, pe baza
regim+existenta, IGNORAND daca exista baza de venituri. Dar D100 pe zero e STRUCTURAL invalid la DUKIntegrator
(sectiunea <obligatie> obligatorie >=1, anaf_surse/d100_struct_anaf.txt; d100.genereaza REFUZA "pe zero"). Deci un
trimestru inchis fara venituri NU are D100 de depus -> restanta falsa (o obligatie care dovedit nu poate exista).
d100_fapt gateaza: True=are baza -> restanta; False=inchis fara venituri -> neaplic cu temei; None=nu se poate sti.
Fara callback (matrice de 64) -> comportament vechi neschimbat.
"""
from datetime import date
from core import control_fiscal_api as cf

AZI = date(2026, 8, 18)
V_MICRO = {"regim_fiscal": "micro", "platitor_tva": False, "operatiuni_ic": False,
           "partida_simpla": False, "tip_decont": None, "tva_data_inceput": None}


def _restante_d100(rez):
    return [(d["an"], d["luna"]) for d in rez["datorate"]
            if d["tip"] == "d100" and date.fromisoformat(d["termen"]) < AZI and not d.get("incert")]


def _neaplic_d100(rez):
    return [(n.get("an"), n.get("luna")) for n in rez["neaplicabile"] if n["tip"] == "d100"]


def test_compat_fara_callback_micro_arata_d100_restante():
    """Fara d100_fapt (matrice/teste): micro arata D100 restante pe trimestrele inchise — NESCHIMBAT."""
    rez = cf.obligatii_datorate(V_MICRO, are_salariati=False, azi=AZI)
    assert _restante_d100(rez), "compat: micro trebuie sa emita D100 restante (comportament vechi, matrice de 64)"


def test_d100_fapt_fara_venituri_suprima_restanta():
    """d100_fapt=False (trimestru inchis fara venituri): restantele D100 NU apar in datorate, ci in neaplicabile."""
    rez = cf.obligatii_datorate(V_MICRO, are_salariati=False, azi=AZI, d100_fapt=lambda a, l: False)
    assert not _restante_d100(rez), "d100_fapt False trebuie sa suprime restantele D100 (nil-ul D100 e invalid la DUK)"
    assert _neaplic_d100(rez), "D100 fara venituri -> neaplicabil cu temei (nu disparut tacit)"


def test_d100_fapt_cu_venituri_pastreaza_restanta():
    """d100_fapt=True (are baza de venituri): restantele D100 raman datorate."""
    rez = cf.obligatii_datorate(V_MICRO, are_salariati=False, azi=AZI, d100_fapt=lambda a, l: True)
    assert _restante_d100(rez), "d100_fapt True -> restantele D100 raman (are obligatie)"


def test_d100_fapt_none_emite_reminder():
    """d100_fapt=None-return (nu se poate sti, ex. facturi necontabilizate): D100 se emite (reminder, nu suprima)."""
    rez = cf.obligatii_datorate(V_MICRO, are_salariati=False, azi=AZI, d100_fapt=lambda a, l: None)
    assert _restante_d100(rez), "d100_fapt None -> emite D100 (nu suprima cand nu se poate sti)"


def test_d100_fapt_nu_atinge_obligatia_curenta_in_fereastra():
    """Obligatia D100 cu termen IN fereastra (termen>=azi) se emite INDIFERENT de d100_fapt (poarta doar pe
    restante). AZI 20.07.2026: T2 (termen 27.07) e obligatie curenta, nu restanta -> emisa desi d100_fapt=False."""
    azi2 = date(2026, 7, 20)
    rez = cf.obligatii_datorate(V_MICRO, are_salariati=False, azi=azi2, d100_fapt=lambda a, l: False)
    curent = [(d["an"], d["luna"]) for d in rez["datorate"]
              if d["tip"] == "d100" and date.fromisoformat(d["termen"]) >= azi2]
    assert curent, "obligatia D100 in fereastra (termen>=azi) nu trebuie gateata de d100_fapt (poarta doar pe restante)"
