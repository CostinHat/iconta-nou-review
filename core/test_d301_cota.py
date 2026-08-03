# -*- coding: utf-8 -*-
"""
Gard period-aware pe cota de TVA oferita la introducerea operatiunilor D301.

TEMEI: CF art.291 — cota standard alin.(1) = 21% (de la 01.08.2025, Legea 141/2025;
19% intre 2017 si 31.07.2025); cota redusa alin.(2) = 11% (de la 01.08.2025). INAINTE de
01.08.2025 reducerile erau 9% si 5% (comasate in 11% de Legea 141/2025, pct.42-43).
art.291 alin.(8): cota achizitiei intracomunitare = cota livrarii interne a aceluiasi bun,
deci cota redusa CHIAR se poate aplica in D301.

DEFECT reparat: cote_perioada oferea cota redusa ca literal fix 11, indiferent de perioada,
in timp ce standardul era period-aware. Pentru o luna D301 dinainte de 08.2025 (rectificativa)
optiunea '11% redusa' era gresita legal. Fix: redusa din common.cota('tva_redusa', data);
daca nu e configurata pt perioada -> se omite (nu se ofera un 11% fals). Cele doua cote reduse
istorice coexistente (9%/5%) cer remodelare COTE = decizie de produs (nesolutionata aici).
"""
from core import d301_operatiuni_api as api


def test_cote_2026_standard_21_redusa_11_scutit_0():
    # Perioada curenta (post Legea 141/2025): 21% standard, 11% redusa, 0% scutit. NESCHIMBAT.
    vals = [c["val"] for c in api.cote_perioada(2026, 8)]
    assert vals == [21, 11, 0], vals


def test_cote_redusa_period_aware_nu_ofera_11_pe_perioada_veche():
    # 2025-06: standardul e 19%, iar reducerile de ATUNCI erau 9%/5% - NU 11%.
    # cote_perioada nu trebuie sa ofere '11% redusa' pt o luna dinainte de 01.08.2025.
    vals = [c["val"] for c in api.cote_perioada(2025, 6)]
    assert 19 in vals, "standardul 2025-06 trebuie sa fie 19%%: %r" % (vals,)
    assert 11 not in vals, "ofera 11%% redusa gresit pt 2025-06 (atunci: 9%%/5%%): %r" % (vals,)
    assert 0 in vals, "scutit 0%% trebuie sa ramana: %r" % (vals,)


def test_adauga_respinge_cota_11_pe_perioada_veche():
    # Consecinta de poarta: o cota 11% pe o luna pre-08.2025 e respinsa (nu se persista un tva gresit).
    class _Cur:
        def __enter__(self): return self
        def __exit__(self,*a): return False
        def execute(self,*a,**k): pass
        def fetchone(self): return [1]
    class _Conn:
        def cursor(self,*a,**k): return _Cur()
        def commit(self): pass
    r = api.adauga(_Conn(), "public", 2025, 6,
                   {"tip":1,"tip_valuta":"EUR","val_valuta":"100","curs":"4.97",
                    "cota":11,"nr_doc":"F1","data_doc":"10.06.2025"})
    assert "eroare" in r and "cota" in r["eroare"].lower(), r


# --- DECIZIE PRODUS (Costin 03.08): cote reduse istorice 9%/5% ca doua chei cu temei propriu ---
from datetime import date as _date
from decimal import Decimal as _D
from core.common import cota as _cota, PerioadaIndisponibila as _PI
import pytest as _pytest


def test_cote_perioada_veche_ofera_9_si_5_coexistente():
    # Pre-01.08.2025 existau DOUA cote reduse coexistente: 9% (CF art.291 alin.2) si 5% (alin.3).
    vals = [c["val"] for c in api.cote_perioada(2020, 3)]
    assert 19 in vals and 9 in vals and 5 in vals and 0 in vals, vals
    assert 11 not in vals, vals


def test_cota_reduse_istorice_9_si_5_din_registru_comasate_in_11():
    # 9%/5% valabile in era 19%; comasate in 11% de la 01.08.2025 (Legea 141/2025).
    assert _cota("tva_redusa_9", _date(2020, 3, 1))[0] == _D("0.09")
    assert _cota("tva_redusa_5", _date(2020, 3, 1))[0] == _D("0.05")
    assert _cota("tva_redusa_9", _date(2026, 1, 1))[0] == _D("0.11")   # comasat
    assert _cota("tva_redusa_5", _date(2026, 1, 1))[0] == _D("0.11")   # comasat


def test_cota_reduse_istorice_indisponibile_inainte_de_ancora_2017():
    # Inainte de ancora (2017-01-01, era standard 19%) nu avem valoare verificata -> refuz, nu presupunere.
    for cheie in ("tva_redusa_9", "tva_redusa_5"):
        with _pytest.raises(_PI):
            _cota(cheie, _date(2015, 6, 1))
