# -*- coding: utf-8 -*-
"""[deficiența 389, retestul Costin 19.10.2026] „Istoric declarații: perioada apare 03/2026 și 06/2026 în loc de T1/2026, T2/2026.” Perioada
se scrie cum o scrie formularul, după profilul firmei: D100 la profit / micro e trimestrial (CF art.41 alin.(1): „[...] trimestrial,
până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III”; CF art.56 alin.(1): micro, „trimestrial”), D300 la
decontul trimestrial (CF art.322 alin.(2): „perioada fiscală este trimestrul calendaristic pentru persoana impozabilă care [...]”)."""
from core import istoric_declaratii_import_api as ist


def _p(tip, luna, profil, an=2026, anuala=False):
    return ist.cu_perioada([{"tip": tip, "luna": luna, "an": an, "anuala": anuala}], profil)[0]["perioada"]


def test_d100_la_profit_e_trimestrial():
    assert [_p("D100", 3, {"regim_fiscal": "profit"}), _p("D100", 6, {"regim_fiscal": "micro"})] == ["T1/2026", "T2/2026"]


def test_d300_dupa_decont():
    assert _p("D300", 9, {"tip_decont": "trimestrial"}) == "T3/2026"
    assert _p("D300", 9, {"tip_decont": "lunar"}) == "09/2026"


def test_luna_care_nu_incheie_trimestrul_ramane_lunara():
    assert _p("D100", 2, {"regim_fiscal": "profit"}) == "02/2026"


def test_d112_si_anualele():
    assert _p("D112", 3, {"regim_fiscal": "profit", "tip_decont": "trimestrial"}) == "03/2026"
    assert _p("D101", 12, {"regim_fiscal": "profit"}, anuala=True) == "anuală 2026"
