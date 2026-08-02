# -*- coding: utf-8 -*-
"""Tichete de cresa (Legea 165/2018 art.19). Tratament fiscal IDENTIC cu tichetul cultural: impozit 10% pe
valoarea nominala, FARA CAS/CASS/CAM (cresa in CF art.142 lit.r; exceptata din CASS art.157(2) care lasa doar
masa+vacanta). Plafon: 450/luna/copil (art.19(1)), baza confirmata; indexarea (740) e GRI (verdict 17), neaplicata."""
from decimal import Decimal
from datetime import date
import pytest
from core import common
from core.salarizare import calcul_salariu


def test_plafon_cresa_450_per_copil():
    assert common.plafon_cresa(date(2026, 5, 1))[0] == Decimal("450")        # 1 copil (default)
    assert common.plafon_cresa(date(2026, 5, 1), nr_copii=2)[0] == Decimal("900")
    assert common.plafon_cresa(date(2026, 5, 1), nr_copii=3)[0] == Decimal("1350")


def test_cresa_impozit_fara_cass():
    SEM2 = date(2026, 9, 1)
    r0 = calcul_salariu(6000, la_data=SEM2)
    r1 = calcul_salariu(6000, la_data=SEM2, tichet_cresa=400)
    assert r1["tichete_cresa"] == Decimal("400.00")
    assert r1["cass_tichete"] == r0["cass_tichete"]        # cresa NU adauga cass (art.157(2))
    assert r1["cass"] == r0["cass"]
    assert r1["impozit"] - r0["impozit"] == Decimal("40.00")   # 10% pe 400
    assert r0["net"] - r1["net"] == Decimal("40.00")
    assert r1["cost_angajator"] - r0["cost_angajator"] == Decimal("400.00")


def test_cresa_in_registru_fara_cass():
    from core import salarizare
    reg = salarizare.BILETE_VALOARE_TRATAMENT
    assert reg["cresa"]["cass"] is False                   # ca cultural, spre deosebire de masa/vacanta
    assert reg["cresa"]["impozit"].startswith("10%")
