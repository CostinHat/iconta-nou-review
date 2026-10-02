# -*- coding: utf-8 -*-
"""GARD — CASS din activități independente sub 6 salarii minime NU e „opțională” (neconformitate reparată 02.10.2026).

Defectul: `d212_engine.calculeaza_cass` întorcea, pentru un venit net între 0 și 6 salarii minime, „neobligatoriu,
CASS 0”, iar fișa RIP de pe ecranele RIP și D212 afișa „neobligatoriu — sub 6 salarii minime”. Un PFA cu 20.000 lei
venit net pe 2025 afla că nu datorează CASS, deși legea cere 2.430 lei (sau 2.000, cu o excepție).

Temei (Codul fiscal, forma consolidată din corpus):
  · CF art.170 alin.(1): CASS „la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual
    realizat” — pe venitul efectiv, fără prag de intrare;
  · CF art.174 alin.(6): când baza „este mai mică decât cea corespunzătoare unei baze de calcul egale cu nivelul de 6
    salarii minime brute pe țară, persoanele fizice datorează contribuția …, respectiv o diferență de contribuție …
    până la nivelul celei corespunzătoare bazei de calcul egale cu 6 salarii minime brute pe țară”;
  · CF art.174 alin.(7)–(8): diferența nu se datorează pentru salarii ≥ 6 sm, venituri lit. c)-h) cu CASS ≥ 6 sm,
    pensii, exceptați art.154 / opțiune art.180 în anul precedent;
  · CF art.118 alin.(2) lit.b): la impozit se deduc CAS și CASS „cu excepția diferenței de contribuție de asigurări
    sociale de sănătate prevăzută la art. 174 alin. (6)”.
"""
import pytest

from core import d212_engine as e

P25 = e.plafoane_an(2025)          # salariul minim reper 4.050 -> 6 sm = 24.300, CASS minimă 2.430


def test_sub_6_sm_baza_e_minimul_legal_nu_zero():
    # CF art.174 alin.(6): diferența până la baza de 6 sm. MUTAȚIE: forma veche (sub prag -> 0) -> pică
    r = e.calculeaza_cass(20000, P25)
    assert (r["obligatoriu"], r["baza"], r["cass"]) == (True, 24300, 2430.0)
    # CF art.118 alin.(2) lit.b): diferența (430) NU e deductibilă; deductibilă e CASS pe venit (2.000)
    assert (r["cass_pe_venit"], r["diferenta_minim"]) == (2000.0, 430.0)


@pytest.mark.parametrize("exceptie", sorted(e.EXCEPTII_MINIM_CASS))
def test_exceptiile_alin_7_8_scot_doar_diferenta(exceptie):
    # CF art.174 alin.(7)-(8): „Diferența … nu se datorează” — CASS pe venit rămâne (art.170 alin.(1))
    r = e.calculeaza_cass(20000, P25, exceptie_minim=exceptie)
    assert (r["baza"], r["cass"], r["diferenta_minim"]) == (20000, 2000.0, 0.0)


def test_exceptie_necunoscuta_refuzata():
    with pytest.raises(ValueError):
        e.calculeaza_cass(20000, P25, exceptie_minim="asigurat")


def test_pierdere_sau_zero_nu_datoreaza():
    # instrucțiunile D212 pct.48 lit.c): pierdere fiscală sau venit net zero -> subsecțiunea nu se completează
    assert e.calculeaza_cass(0, P25)["cass"] == 0.0
    assert e.calculeaza_cass(-500, P25)["cass"] == 0.0


def test_peste_6_sm_liniar_si_plafonat_neschimbat():
    # art.170 alin.(1): baza = venitul net, plafonată la 60 sm (2025) / 72 sm (2026, Legea 239/2025 art.XII pct.19)
    assert e.calculeaza_cass(100000, P25)["cass"] == 10000.0
    assert e.calculeaza_cass(300000, P25)["cass"] == 24300.0
    assert e.calculeaza_cass(400000, e.plafoane_an(2026))["baza"] == 72 * 4050


def test_impozitul_deduce_doar_cass_pe_venit():
    # venit net 20.000: CAS 0 (sub 12 sm, art.148), CASS 2.430 din care 430 diferență nedeductibilă
    # -> baza impozit 20.000 - 2.000 = 18.000, impozit 1.800. MUTAȚIE: deducere CASS întreagă -> 17.570 -> pică
    r = e.calculeaza_d212(30000, 10000, P25)
    assert (r["cass"]["cass"], r["baza_impozit"], r["impozit"]) == (2430.0, 18000.0, 1800.0)
