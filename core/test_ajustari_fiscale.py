# -*- coding: utf-8 -*-
"""Ajustările fiscale ale rezultatului (Registrul de evidență fiscală) — deficiența 378, comanda Costin 8.2: „D100 trimestrial pornește de la
rezultatul fiscal cumulat din Registrul de evidență fiscală [...] recuperarea pierderii fiscale din anii anteriori în limitele legale.”"""
from decimal import Decimal

import pytest

from core import ajustari_fiscale as af


def test_recuperarea_pierderii_e_plafonata_la_70_la_suta():
    # CF art.31 alin.(1) (Legea 296/2023, de la 01.01.2024): „se recuperează din profiturile impozabile realizate, în limita a 70% inclusiv”
    assert af.PRAG_RECUPERARE_PIERDERE == Decimal("70")
    assert af.recuperare_pierdere(100000, 10000) == Decimal("7000")       # 70% din profitul de 10.000
    assert af.recuperare_pierdere(3000, 10000) == Decimal("3000")         # cel mult pierderea de recuperat
    # „în limita a 70% inclusiv”: plafonul nu se depășește nici prin rotunjire — 70% din 10.001 = 7.000,70 -> 7.000 (în jos, la leu)
    assert af.recuperare_pierdere(100000, 10001) == Decimal("7000")
    assert af.recuperare_pierdere(100000, 0) == Decimal(0) and af.recuperare_pierdere(100000, -500) == Decimal(0)
    assert af.recuperare_pierdere(0, 10000) == Decimal(0)


@pytest.mark.parametrize("an, trim, rand, suma, parte", [
    (2026, 3, "P7", 100, "nu e o ajustare fiscală acceptată"),        # rd.7 vine din contabilitate, nu se scrie aici
    (2026, None, "P33", 100, "Alege trimestrul"),
    (2026, 3, "P39", 100, "nu se scrie pe trimestru"),                # pierderea din anii anteriori e o cifră a anului
    (2026, 3, "P33", 0, "mai mare ca 0"),
    (2026, 3, "P33", "x", "un număr"),
    (1999, 3, "P33", 10, "nu e plauzibil"),
])
def test_ajustarea_gresita_e_refuzata_numit(an, trim, rand, suma, parte):
    """MUTAȚIA: ramura `rand in ANUALE` scoasă din `valideaza` -> ROȘU (P39 pe trimestru acceptat)."""
    m = af.valideaza(an, trim, rand, suma)
    assert m and parte in m, m


def test_ajustarea_buna_trece():
    assert af.valideaza(2026, 3, "P33", "1000.50") is None
    assert af.valideaza(2026, None, "P39", 5000) is None
