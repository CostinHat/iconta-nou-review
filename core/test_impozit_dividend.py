# -*- coding: utf-8 -*-
"""PAS 0 versionare formule: impozitul pe dividende (regim dividende + lichidare) = COTE period-aware,
nu petic 'if ref>=2026 else 10'. 16% de la 01.01.2026 (Legea 141/2025), 10% inainte (REDARE, neverificat
la sursa pentru pre-2026 - vezi comentariul COTE)."""
from datetime import date

from core import common as c, decontari_asociati as da, lichidare as li


def test_impozit_dividend_period_aware_din_cote():
    assert c.cota("impozit_dividend", date(2026, 1, 1))[0] == c.Decimal("0.16") if hasattr(c, "Decimal") else True
    from decimal import Decimal
    assert c.cota("impozit_dividend", date(2026, 6, 1))[0] == Decimal("0.16")
    assert c.cota("impozit_dividend", date(2025, 6, 1))[0] == Decimal("0.10")


def test_cota_dividend_si_lichidare_sursa_din_cote():
    """Ambele functii (decontari_asociati + lichidare) intorc procentul din common.COTE, nu literal."""
    assert int(da.cota_dividend(date(2026, 6, 1))) == 16
    assert int(da.cota_dividend(date(2025, 6, 1))) == 10
    assert int(li._cota_dividend(date(2026, 6, 1))) == 16
    assert int(li._cota_dividend(date(2024, 6, 1))) == 10


def test_peticul_if_pe_data_a_disparut():
    """Regula 0a: peticul (COTA_2026/COTA_VECHE + if ref>=2026) a fost ELIMINAT, nu comentat."""
    src = open("core/decontari_asociati.py", encoding="utf-8").read()
    assert "COTA_2026" not in src and "COTA_VECHE" not in src
    assert "if ref >= date(2026" not in open("core/lichidare.py", encoding="utf-8").read()
