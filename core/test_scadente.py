# -*- coding: utf-8 -*-
"""Teste pentru scadentarul per declaratie (core/scadente.py), sursa unica de termene.
Blocheaza regresia D394-februarie (ziua 30 inexistenta) descoperita la conectarea D394/D406
in semaforul fiscal (BRIEF_CODE_SEMAFOR faza 3)."""
from datetime import date
from core import scadente


def test_d394_februarie_nu_crapa():
    # perioada ianuarie -> termen nominal "30 februarie" inexistent -> ultima zi (28 feb 2026)
    assert scadente._data_nominala("d394", 2026, luna=1) == date(2026, 2, 28)
    scadente.scadenta_data("d394", 2026, luna=1)  # nu trebuie sa ridice ValueError


def test_d394_30_luna_normala():
    # luna cu 31 de zile -> ziua 30 ramane 30
    assert scadente._data_nominala("d394", 2026, luna=2) == date(2026, 3, 30)


def test_d300_25_luna_urmatoare():
    assert scadente._data_nominala("d300", 2026, luna=3) == date(2026, 4, 25)


def test_d101_25_iunie_an_urmator():
    # OUG 153/2020 art.I alin.(13) lit.a (2021-2025); OUG 8/2026 art.6 pct.12 -> art.42(1) CF (2026+)
    assert scadente._data_nominala("d101", 2025) == date(2026, 6, 25)
    assert scadente._data_nominala("d101", 2026) == date(2027, 6, 25)


def test_d406_ultima_zi_luna_urmatoare():
    assert scadente._data_nominala("d406", 2026, luna=1) == date(2026, 2, 28)


def test_scadenta_muta_in_zi_lucratoare():
    # 25.07.2026 = sambata -> 27 luni (prima zi lucratoare >= nominala)
    assert scadente.scadenta_data("d300", 2026, luna=6) == date(2026, 7, 27)


def test_25_decembrie_devine_21_decembrie():
    """[Lot 19 defect 7] Inainte: 25.12.2026 (Craciun) -> 26 -> 27 duminica -> 28.12 — o zi DUPA termenul legal."""
    for tip in ("d300", "d112", "d100", "d301", "d390"):
        # CPF art.155 alin.(2): „scadența și/sau termenul de declarare se împlinesc la 25 decembrie, sunt scadente
        # și/sau se declară până la data de 21 decembrie”
        assert scadente.scadenta_data(tip, 2026, luna=11) == date(2026, 12, 21), tip
    # CPF art.155 alin.(2): „În situația în care data de 21 decembrie, este zi nelucrătoare, ... până în ultima zi
    # lucrătoare anterioară datei de 21 decembrie” — 21.12.2025 duminica, 20 sambata -> 19 vineri
    assert scadente.scadenta_data("d300", 2025, luna=11) == date(2025, 12, 19)
    assert scadente.scadenta("d112", 2031, luna=11) == "19.12.2031"


def test_ce_nu_cade_pe_25_decembrie_nu_se_muta_inapoi():
    assert scadente.scadenta_data("d394", 2026, luna=11) == date(2026, 12, 30)     # ziua 30, nu 25
    assert scadente.scadenta_data("d300", 2026, luna=12) == date(2027, 1, 25)


def test_temeiul_21_decembrie_e_verbatim_in_corpus():
    import os
    act, fisier, citat = scadente.TEMEI_21_DECEMBRIE
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    text = " ".join(open(os.path.join(rad, fisier), encoding="utf-8").read().split())
    assert citat in text, "citatul %s nu mai e verbatim in %s" % (act, fisier)
