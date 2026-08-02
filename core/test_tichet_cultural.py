# -*- coding: utf-8 -*-
"""Tichete culturale (Legea 165/2018 cap.V). Temeiuri VERDE: anaf_surse/RAPORT_verificare_temeiuri.md.
Tratament fiscal DIFERIT de tichetul de masa: impozit 10% pe valoarea nominala, FARA CAS/CASS/CAM
(CASS: art.157(2) excepteaza NUMAI masa+vacanta -> culturalul NU intra in CASS, verdict 11)."""
from decimal import Decimal
from datetime import date
import pytest
from core import common


# ---- Plafon semestrial: ferestre confirmate + blocaj GRI (verdict 16) ----
def test_plafon_cultural_ferestre_confirmate():
    assert common.plafon_cultural(date(2025, 5, 1))[0] == Decimal("220")                 # lunar apr-sep 2025
    assert common.plafon_cultural(date(2025, 5, 1), ocazional=True)[0] == Decimal("450")  # eveniment
    assert common.plafon_cultural(date(2026, 6, 1))[0] == Decimal("250")                 # lunar apr-sep 2026
    assert common.plafon_cultural(date(2026, 8, 1), ocazional=True)[0] == Decimal("490")  # eveniment


def test_plafon_cultural_fereastra_gri_blocheaza():
    # oct 2025 - mar 2026 = GRI (ordin mijloc stub) -> BLOCAJ, nu 240/470 tacit.
    for m in (date(2025, 10, 1), date(2025, 12, 1), date(2026, 3, 1)):
        with pytest.raises(common.PlafonCulturalIndisponibil) as ei:
            common.plafon_cultural(m)
        assert "PERIOADA_BLOCATA:" in str(ei.value)
        assert "GRI" in str(ei.value)


def test_plafon_cultural_semestru_fara_ordin_blocheaza():
    # inainte de apr 2025 si dupa sep 2026 (fara ordin descarcat) -> blocaj motivat.
    for m in (date(2025, 1, 1), date(2026, 11, 1)):
        with pytest.raises(common.PlafonCulturalIndisponibil):
            common.plafon_cultural(m)
