# -*- coding: utf-8 -*-
"""Teste gardian pentru core/salarizare.py.
Cazuri verificate cifra-cu-cifra contra sursei oficiale 2026
(Cod fiscal art.77/146, OUG 89/2025, OUG 158/2005, Ordinul 506/1030/2026).
"""
from decimal import Decimal
from datetime import date
from core.salarizare import (
    calcul_salariu, deducere_personala, taxe_cm, calcul_cm, calcul_cm_cod10,
)

SEM2 = date(2026, 9, 1)   # salariu minim 4325
SEM1 = date(2026, 3, 1)   # salariu minim 4050


def test_brut_6000_fara_dependenti_sem2():
    r = calcul_salariu(6000, la_data=SEM2)
    assert r["facilitate"] == Decimal("0.00")
    assert r["cas"] == Decimal("1500.00")
    assert r["cass"] == Decimal("600.00")
    assert r["deducere"]["total"] == Decimal("160.00")
    assert r["impozit"] == Decimal("374.00")
    assert r["net"] == Decimal("3526.00")
    assert r["cam"] == Decimal("135.00")
    assert r["cost_angajator"] == Decimal("6135.00")


def test_minim_4325_are_facilitate_sem2():
    r = calcul_salariu(4325, la_data=SEM2)
    assert r["facilitate"] == Decimal("200.00")
    assert r["cas"] == Decimal("1031.25")
    assert r["cass"] == Decimal("412.50")
    assert r["net"] == Decimal("2700.13")


def test_peste_plafon_deducere_zero():
    assert calcul_salariu(7000, la_data=SEM2)["deducere"]["total"] == Decimal("0.00")


def test_part_time_2000_suprataxa_pe_angajator():
    r = calcul_salariu(2000, norma_intreaga=False, venit_brut_total=2000, la_data=SEM2)
    assert r["cas"] == Decimal("500.00")
    assert r["cass"] == Decimal("200.00")
    assert r["cas_suprataxa"] == Decimal("531.25")
    assert r["cass_suprataxa"] == Decimal("212.50")
    assert r["cost_angajator"] == Decimal("2788.75")


def test_part_time_exceptat_fara_suprataxa():
    r = calcul_salariu(2000, norma_intreaga=False, venit_brut_total=2000,
                       exceptat_suprataxare=True, la_data=SEM2)
    assert r["cas_suprataxa"] == Decimal("0.00")
    assert r["cass_suprataxa"] == Decimal("0.00")


def test_minim_difera_pe_semestru():
    assert calcul_salariu(4050, la_data=SEM1)["facilitate"] > 0
    assert calcul_salariu(4050, la_data=SEM2)["facilitate"] == 0


def test_deducere_degresiva_pe_trepte():
    assert deducere_personala(6000, la_data=SEM2)["total"] == Decimal("160.00")


def test_deducere_copil_scoala():
    assert deducere_personala(6000, copii_scoala=2, la_data=SEM2)["copii"] == Decimal("200.00")


def test_deducere_zero_fara_functie_baza():
    assert deducere_personala(4325, functie_baza=False, la_data=SEM2)["total"] == Decimal("0.00")


def test_cass_doar_pe_01_07_10():
    for cod in ("01", "07", "10"):
        assert taxe_cm(1000, cod=cod, la_data=SEM2)["cass"] > 0
    for cod in ("08", "15", "17", "09", "06"):
        assert taxe_cm(1000, cod=cod, la_data=SEM2)["cass"] == Decimal("0.00")


def test_cm_cas_mereu_zero():
    assert taxe_cm(1000, cod="01", la_data=SEM2)["cas"] == Decimal("0.00")


def test_cm_prima_zi_diminuata_boala():
    r = calcul_cm(venituri_6_luni=Decimal("30000"), zile_lucratoare_6_luni=126,
                  zile_lucratoare_cm=10, cod="01", prima_zi_din_episod=True, la_data=SEM2)
    assert r["diminuare"] == 1
    assert r["zile_platite"] == 9


def test_cm_maternitate_fara_diminuare():
    r = calcul_cm(venituri_6_luni=Decimal("30000"), zile_lucratoare_6_luni=126,
                  zile_lucratoare_cm=10, cod="08", prima_zi_din_episod=True, la_data=SEM2)
    assert r["diminuare"] == 0
    assert r["zile_platite"] == 10


def test_cm_split_angajator_max_5():
    r = calcul_cm(venituri_6_luni=Decimal("30000"), zile_lucratoare_6_luni=126,
                  zile_lucratoare_cm=10, cod="01", prima_zi_din_episod=True, la_data=SEM2)
    assert r["zile_ang"] == 5
    assert r["zile_fnuass"] == 4


def test_cm_cod10_plafonat_25pct():
    assert calcul_cm_cod10(4000, 3000) == Decimal("1000.00")
    assert calcul_cm_cod10(4000, 2000) == Decimal("1000.00")
