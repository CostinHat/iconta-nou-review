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
    # 25.12.2026 = vineri + Craciun; 26 sambata + a 2-a zi Craciun; 27 duminica -> 28 luni
    assert scadente.scadenta_data("d300", 2026, luna=11) == date(2026, 12, 28)
