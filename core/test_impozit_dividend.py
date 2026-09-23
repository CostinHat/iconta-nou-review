# -*- coding: utf-8 -*-
"""PAS 0 versionare formule: cotele = COTE period-aware, nu petic 'if ref>=2026 else 10'.
DIVIDENDE (art.97 alin.7): 16% de la 01.01.2026 (Legea 141/2025), 10% in 2025, 8% pre-2025.
LICHIDARE (art.97 alin.5) e DISTINCTA: cota FIXA 10%, impozit final, NU regimul dividendelor -
corectat 23.09.2026 (aplicatia folosea gresit cota dividendelor pentru castigul din lichidare)."""
from datetime import date

from core import common as c, decontari_asociati as da, lichidare as li


def test_impozit_dividend_period_aware_din_cote():
    assert c.cota("impozit_dividend", date(2026, 1, 1))[0] == c.Decimal("0.16") if hasattr(c, "Decimal") else True
    from decimal import Decimal
    assert c.cota("impozit_dividend", date(2026, 6, 1))[0] == Decimal("0.16")
    assert c.cota("impozit_dividend", date(2025, 6, 1))[0] == Decimal("0.10")  # OUG 156/2024 (2025, de la 01.01.2025)


def test_cota_dividend_si_lichidare_sursa_din_cote():
    """Ambele functii intorc procentul din common.COTE, nu literal. DIVIDENDELE (decontari_asociati)
    urmeaza art.97 alin.7 (16%/10%); LICHIDAREA (lichidare) e cota FIXA 10% (art.97 alin.5), DISTINCTA."""
    assert int(da.cota_dividend(date(2026, 6, 1))) == 16
    assert int(da.cota_dividend(date(2025, 6, 1))) == 10
    # lichidare = 10% FIX (art.97 alin.5), pe orice an - NU cota dividendelor (16% din 2026)
    assert int(li._cota_lichidare(date(2026, 6, 1))) == 10
    assert int(li._cota_lichidare(date(2024, 6, 1))) == 10


def test_peticul_if_pe_data_a_disparut():
    """Regula 0a: peticul (COTA_2026/COTA_VECHE + if ref>=2026) a fost ELIMINAT, nu comentat."""
    src = open("core/decontari_asociati.py", encoding="utf-8").read()
    assert "COTA_2026" not in src and "COTA_VECHE" not in src
    assert "if ref >= date(2026" not in open("core/lichidare.py", encoding="utf-8").read()
