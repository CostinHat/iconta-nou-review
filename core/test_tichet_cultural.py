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


# ---- Tratament fiscal in calcul_salariu: impozit 10%, FARA CASS (divergenta fata de masa) ----
def test_cultural_impozit_fara_cass():
    from core.salarizare import calcul_salariu
    SEM2 = date(2026, 9, 1)
    r0 = calcul_salariu(6000, la_data=SEM2)                        # fara cultural
    r1 = calcul_salariu(6000, la_data=SEM2, tichet_cultural=200)   # + 200 lei cultural
    assert r1["tichete_cultural"] == Decimal("200.00")
    # CASS pe tichete NU se schimba (culturalul nu intra in CASS - art.157(2), verdict 11)
    assert r1["cass_tichete"] == r0["cass_tichete"]
    assert r1["cass"] == r0["cass"]
    # impozit +20 (10% pe 200 nominal integral, fara cass de dedus)
    assert r1["impozit"] - r0["impozit"] == Decimal("20.00")
    # net scade cu impozitul cultural (nominalul nu e cash)
    assert r0["net"] - r1["net"] == Decimal("20.00")
    # angajatorul suporta valoarea nominala (o cumpara)
    assert r1["cost_angajator"] - r0["cost_angajator"] == Decimal("200.00")


def test_cultural_diferit_de_masa_pe_cass():
    # Etalon: aceeasi suma ca tichet de MASA da CASS; ca tichet CULTURAL nu da CASS.
    from core.salarizare import calcul_salariu
    SEM2 = date(2026, 9, 1)
    masa = calcul_salariu(6000, la_data=SEM2, tichet_valoare=40, tichet_zile=5)   # 5 x 40 = 200 lei masa (sub plafon 45)
    cult = calcul_salariu(6000, la_data=SEM2, tichet_cultural=200)                # 200 lei cultural
    # masa: cass pe 200 = 20; cultural: cass pe 200 = 0
    assert masa["cass_tichete"] == Decimal("20.00")
    assert cult["cass_tichete"] == Decimal("0.00")
