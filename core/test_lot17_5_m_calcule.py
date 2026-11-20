# -*- coding: utf-8 -*-
"""Lotul 17.5-M — calculele schimbate: AC028 (Cash = debitor minus creditor la 531*/512*) și AC022 (rezumatul Supervizorului, derivat într-un singur loc).
(i) și (ii) pică pe baza lotului (cash fără sf_c; rezumat_din_randuri absentă); (iii) e gardă și trece și pe bază."""
import datetime

from core import cashflow
from core import supervizor as S
from core.kpi_client import kpi_din_balanta
from core.test_supervizor import _FIRME, _cu_plan, _deschide_fals


def _r(cont, **k):
    b = {"cont": cont, "denumire": "", "si_d": 0, "si_c": 0, "prec_d": 0, "prec_c": 0,
         "rul_d": 0, "rul_c": 0, "tot_d": 0, "tot_c": 0, "sf_d": 0, "sf_c": 0}
    b.update(k)
    return b


def test_cash_negativ_cand_trezoreria_e_creditoare():
    """AC028: 5121 cu sold creditor 20.000 și 5311 cu 1.026 dau Cash -21.026 (nu 0); un sold debitor se scade cu cel creditor."""
    assert kpi_din_balanta([_r("5121", sf_c=20000), _r("5311", sf_c=1026)])["cash"] == -21026.0
    assert kpi_din_balanta([_r("5121", sf_d=5000), _r("5311", sf_c=1000)])["cash"] == 4000


def test_rezumat_din_randuri_numara_pe_rezultat():
    """AC022: o cheie pe fiecare rezultat, firme_in_domeniu, de_confirmat și constatari_total, derivate dintr-un singur loc."""
    randuri = [
        {"rezultat": S.CONSTATARI, "constatari": [{}, {}], "de_confirmat": 1},
        {"rezultat": S.FARA_SUBIECT, "constatari": [], "de_confirmat": 0},
        {"rezultat": S.NEVERIFICAT, "constatari": [], "de_confirmat": 0},
    ]
    r = S.rezumat_din_randuri(randuri)
    assert (r[S.CONSTATARI], r[S.FARA_SUBIECT], r[S.NEVERIFICAT]) == (1, 1, 1)
    assert (r["firme_in_domeniu"], r["de_confirmat"], r["constatari_total"]) == (3, 1, 2)


def test_ruleaza_portofoliu_foloseste_acelasi_rezumat(monkeypatch):
    _cu_plan(monkeypatch)
    r = S.ruleaza_portofoliu(2026, 8, firme=_FIRME, deschide=_deschide_fals(("s_rupt",)), domeniu="probă")
    assert r["rezumat"] == S.rezumat_din_randuri(r["firme"])


def test_previziunea_portalului_porneste_si_dintr_un_cash_negativ():
    """Gardă (trece și pe bază): forecast cu start negativ merge fără excepție."""
    rez = cashflow.forecast(-21026.0, [], [], azi=datetime.date(2026, 11, 3), saptamani=1)
    assert len(rez) == 1 and rez[0]["sold"] == -21026.0
