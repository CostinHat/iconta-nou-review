# -*- coding: utf-8 -*-
"""[deficiența 395, retestul Costin 19.10.2026] „D300 «Din ce e făcută declarația»: rândurile vin în ordinea 9, 10, 3, 3.1, 19, nu în
ordinea formularului.” Rândurile formularului (D300, D101) se arată în ordinea formularului (rând, subrând, coloana Valoare înaintea
coloanei TVA), oricare ar fi ordinea dicționarului motorului."""
from types import SimpleNamespace

from core import declaratii_componente as dc


def _randuri(tip, d):
    return [r["rând"] for r in dc.componente(tip, SimpleNamespace(**d))["sectiuni"][0]["randuri"]]


def test_d300_in_ordinea_formularului():
    R = {"R9_1": 1000, "R9_2": 210, "R10_1": 500, "R10_2": 55, "R3_1": 300, "R3_1_1": 100, "R17_2": 265}
    assert _randuri("d300", {"R": R}) == [
        "rândul 3, coloana Valoare", "rândul 3.1, coloana Valoare", "rândul 9, coloana Valoare", "rândul 9, coloana TVA",
        "rândul 10, coloana Valoare", "rândul 10, coloana TVA", "rândul 19, coloana TVA"]


def test_d101_in_ordinea_formularului():
    P = {"P40": 4600, "P25": 100, "P081": 5, "P1": 4600, "P38a": 7}
    assert _randuri("d101", {"P": P}) == ["rândul 1", "rândul 8.1", "rândul 25", "rândul 38^1", "rândul 40"]
