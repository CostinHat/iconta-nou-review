# -*- coding: utf-8 -*-
"""Teste gardian pentru core/salarizare.py.
Cazuri verificate cifra-cu-cifra contra sursei oficiale 2026
(Cod fiscal art.77/146, OUG 89/2025, OUG 158/2005, Ordinul 506/1030/2026).
"""
from decimal import Decimal
from datetime import date
from core.salarizare import (
    calcul_salariu, deducere_personala, taxe_cm, calcul_cm, calcul_cm_cod10, procent_cm,
)

SEM2 = date(2026, 9, 1)   # salariu minim 4325
SEM1 = date(2026, 3, 1)   # salariu minim 4050


def test_brut_6000_fara_dependenti_sem2():
    r = calcul_salariu(6000, la_data=SEM2)
    assert r["facilitate"] == Decimal("0.00")
    assert r["cas"] == Decimal("1500.00")
    assert r["cass"] == Decimal("600.00")
    assert r["deducere"]["total"] == Decimal("151.38")  # FIX3: fara rotunjire (0.035*4325)
    assert r["impozit"] == Decimal("374.86")            # FIX3: 10% pe baza cu ded nerotunjita
    assert r["net"] == Decimal("3525.14")
    assert r["cam"] == Decimal("135.00")
    assert r["cost_angajator"] == Decimal("6135.00")


def test_minim_4325_are_facilitate_sem2():
    r = calcul_salariu(4325, la_data=SEM2)
    assert r["facilitate"] == Decimal("200.00")
    assert r["cas"] == Decimal("1031.25")
    assert r["cass"] == Decimal("412.50")
    assert r["net"] == Decimal("2699.63")               # FIX3: ded de baza 865 (nerotunjit), nu 870


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
    assert deducere_personala(6000, la_data=SEM2)["total"] == Decimal("151.38")  # FIX3: fara rotunjire la 10 lei (0.035*4325=151.375)


def test_deducere_copil_scoala():
    assert deducere_personala(6000, copii_scoala=2, la_data=SEM2)["copii"] == Decimal("200.00")


def test_deducere_zero_fara_functie_baza():
    assert deducere_personala(4325, functie_baza=False, la_data=SEM2)["total"] == Decimal("0.00")


def test_cass_doar_pe_01_07_10():
    for cod in ("01", "07", "10"):
        assert taxe_cm(1000, cod=cod, la_data=SEM2)["cass"] > 0
    for cod in ("08", "15", "17", "09", "06"):
        assert taxe_cm(1000, cod=cod, la_data=SEM2)["cass"] == Decimal("0.00")


def test_cm_cas_25pct_uniform():
    # CAS 25% se retine pe indemnizatia CM, UNIFORM pe toate codurile (CF art.139(1)(o)+140;
    # verificat 31.07: ghid ANAF - si maternitate/copil). Corectat de la cas=0 (era gresit).
    for cod in ("01", "07", "08", "09", "10"):
        assert taxe_cm(1000, cod=cod, la_data=SEM2)["cas"] == Decimal("250.00"), cod


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


# ---- art. 146(5^6): suprataxarea NU depinde de norma (corectie 15.07.2026) ----
def test_norma_intreaga_sub_minim_este_suprataxata():
    """art. 146(5^6): "norma intreaga SAU timp partial" - conditia e venitul sub minim.
    Regresie: conditia cerea not norma_intreaga -> stat plata si D112 divergeau."""
    from datetime import date
    r = calcul_salariu(brut=3000, la_data=date(2026, 6, 1), norma_intreaga=True)
    assert r["cas_suprataxa"] > 0, "norma intreaga sub minim TREBUIE suprataxata"
    assert r["cass_suprataxa"] > 0


def test_part_time_sub_minim_ramane_suprataxat():
    from datetime import date
    r = calcul_salariu(brut=3000, la_data=date(2026, 6, 1), norma_intreaga=False)
    assert r["cas_suprataxa"] > 0


def test_exceptatul_nu_e_suprataxat_indiferent_de_norma():
    """Exceptiile sunt cele de la alin. (5^7), nu norma."""
    from datetime import date
    for norma in (True, False):
        r = calcul_salariu(brut=3000, la_data=date(2026, 6, 1), norma_intreaga=norma,
                           exceptat_suprataxare=True)
        assert r["cas_suprataxa"] == 0 and r["cass_suprataxa"] == 0


def test_peste_minim_nu_se_suprataxeaza():
    from datetime import date
    r = calcul_salariu(brut=5000, la_data=date(2026, 6, 1), norma_intreaga=True)
    assert r["cas_suprataxa"] == 0


def test_facilitatea_ramane_conditionata_de_norma_intreaga():
    """HG 146/2026: facilitatea cere norma intreaga - aici norma CONTEAZA."""
    from datetime import date
    intreg = calcul_salariu(brut=4050, la_data=date(2026, 6, 1), norma_intreaga=True)
    partial = calcul_salariu(brut=4050, la_data=date(2026, 6, 1), norma_intreaga=False)
    assert intreg["facilitate"] > 0
    assert partial["facilitate"] == 0


def test_facilitate_pe_minim_cu_cm_ramane_intreaga():
    """REGRESIE (29.07.2026): salariat pe salariul minim, norma intreaga, cu zile de CM ->
    brut_lucrat < salariu_brut = sm. Facilitatea se judeca pe brutul CONTRACTUAL (OUG 156/2024
    art.LXVI lit.a), nu pe cel lucrat -> ramane INTREAGA (300 in S1 2026), iar baza contributiilor
    = brut_lucrat - 300. Inainte de reparatie egalitatea rula pe brut_lucrat si facilitatea se
    pierdea complet pe orice luna cu CM. la_data EXPLICIT in S1 (sm=4050): in S2 (sm=4325) un
    contract de 4050 da 0 oricum, deci n-ar dovedi nimic."""
    from core.common import _dec, _q, cota
    brut_lucrat = 3497.73                              # 4050 proratat pentru 3 zile de CM
    r = calcul_salariu(brut_lucrat, la_data=SEM1, norma_intreaga=True, venit_brut_total=4050)
    assert r["facilitate"] == Decimal("300.00")        # INTREAGA, nu 0 (bug reparat)
    # baza contributiilor = brut_lucrat - facilitatea intreaga (nu brut_lucrat gol)
    cota_cas, _ = cota("cas", SEM1)
    baza_contrib = _dec(brut_lucrat) - r["facilitate"]
    assert r["cas"] == _q(baza_contrib * cota_cas)


def test_suprataxa_baza_pe_minimul_diminuat_ambele_semestre():
    # baza suprataxarii = (salariu_minim - facilitate - brut) x cota, pe MINIMUL DIMINUAT (OUG 89/2025)
    s1 = calcul_salariu(2000, norma_intreaga=False, venit_brut_total=2000, la_data=SEM1)
    assert s1["cas_suprataxa"] == Decimal("437.50")    # S1 2026 (sm=4050, fac=300): (4050-300-2000)*25% CAS - art.146(5^6) CF
    assert s1["cass_suprataxa"] == Decimal("175.00")   # S1: (4050-300-2000)*10% CASS - OUG 89/2025: baza = sm diminuat cu 300
    s2 = calcul_salariu(2000, norma_intreaga=False, venit_brut_total=2000, la_data=SEM2)
    assert s2["cas_suprataxa"] == Decimal("531.25")    # S2 2026 (sm=4325, fac=200): (4325-200-2000)*25% CAS
    assert s2["cass_suprataxa"] == Decimal("212.50")   # S2: (4325-200-2000)*10% CASS - OUG 89/2025: baza = sm diminuat cu 200


def test_suprataxa_prag_prorata_luna_angajare():
    # Angajare la MIJLOC de luna: nivelul de referinta al suprataxarii se prorateaza pe zilele lucrate
    # din luna. Iunie 2026: 21 zile lucratoare; angajat pe 16 -> 11 zile lucrate (fara sarbatori).
    from datetime import date
    r = calcul_salariu(1000, norma_intreaga=False, venit_brut_total=1000,
                       la_data=date(2026, 6, 1), data_angajare=date(2026, 6, 16))
    assert r["cas_suprataxa"] == Decimal("241.07")    # prag=(4050-300)x11/21=1964.29; (1964.29-1000)x25% - OUG 156/2024 art.LXVI alin.(5) + OMF 1855/2022 pct.2 (interpretare B)
    assert r["cass_suprataxa"] == Decimal("96.43")    # (1964.29-1000)x10% CASS - nivelul DIMINUAT (sm-facilitate) proratat pe zile lucrate
    # contract activ toata luna (fara data_angajare) -> prag INTREG 3750, suprataxare mai mare: proratarea chiar reduce
    r_full = calcul_salariu(1000, norma_intreaga=False, venit_brut_total=1000, la_data=date(2026, 6, 1))
    assert r_full["cas_suprataxa"] == Decimal("687.50")   # (3750-1000)x25% - fara proratare, pe pragul intreg


def test_facilitate_prorata_luna_angajare():
    # OUG 156/2024 art.LXVI alin.(4) lit.b) (TEXT EXPLICIT): facilitatea de 300 lei SE DIMINUEAZA
    # la incadrarea NOUA la nivelul minim. Iunie 2026: angajat pe 16 -> 11/21 zile lucrate.
    from datetime import date
    r = calcul_salariu(4050, la_data=date(2026, 6, 1), data_angajare=date(2026, 6, 16), venit_brut_total=4050)
    assert r["facilitate"] == Decimal("157.14")     # 300 x 11/21 - alin.(4) lit.b) proratare la angajare noua
    r_full = calcul_salariu(4050, la_data=date(2026, 6, 1), venit_brut_total=4050)
    assert r_full["facilitate"] == Decimal("300.00")  # contract activ toata luna -> facilitate nediminuata


def test_suprataxa_si_facilitate_prorata_la_incetare():
    # GARD PERMANENT (mutat din test_datorie dupa modelarea data_incetare, PASUL 1): la INCETAREA
    # contractului la mijloc de luna, ATAT pragul de suprataxare (alin.5) CAT SI facilitatea (alin.4
    # lit.d) se prorateaza pe zilele ACTIVE. Iunie 2026, incetare pe 20 -> 14 zile lucrate din 21.
    from datetime import date
    rf = calcul_salariu(4050, la_data=date(2026, 6, 1), data_incetare=date(2026, 6, 20), venit_brut_total=4050)
    assert rf["facilitate"] == Decimal("200.00")     # 300 x 14/21 - alin.(4) lit.d) proratare facilitate la incetare
    rp = calcul_salariu(1000, norma_intreaga=False, venit_brut_total=1000,
                        la_data=date(2026, 6, 1), data_incetare=date(2026, 6, 20))
    assert rp["cas_suprataxa"] == Decimal("375.00")  # (3750 x 14/21 - 1000) x 25% - alin.(5) prag proratat la incetare


def test_deducere_4plus_persoane_45pct():
    # FIX1 (Cod fiscal art.77 alin.4): 4 SAU MAI MULTE persoane in intretinere -> 45% x salariu
    # minim (nu 40%). brut = salariu minim (fara degresivitate) izoleaza procentul de baza.
    # 0.45 * 4325 = 1946.25.
    assert deducere_personala(4325, persoane=4, la_data=SEM2)["baza"] == Decimal("1946.25")
    assert deducere_personala(4325, persoane=5, la_data=SEM2)["baza"] == Decimal("1946.25")

def test_tanar_sub26_brut_mic_primeste_deducere():
    # FIX2 (Cod fiscal art.77 alin.10 lit.a): tanarul <26 are DOAR limita superioara de venit
    # (brut <= sm+2000); NU exista limita inferioara. brut 1500 (part-time, sub salariul minim)
    # trebuie sa primeasca deducerea suplimentara de 15% x salariu minim. 0.15 * 4325 = 648.75.
    assert deducere_personala(1500, sub_26=True, la_data=SEM2)["tineri"] == Decimal("648.75")


def test_deducere_la_data_obligatoriu():
    # FIX4: la_data (luna de salarizare) e OBLIGATORIU. Un apel fara el trebuie sa dea eroare,
    # nu sa ghiceasca luna curenta - salariul minim depinde de luna de realizare a venitului.
    import pytest
    with pytest.raises((TypeError, ValueError)):
        deducere_personala(6000)


def test_carantina_cod07_este_100pct():
    # Cod 07 (carantina) = 100% din baza de calcul (OUG 158/2005 art.20 alin.(3), majorat permanent
    # prin Legea 136/2020), NU 75%. Confirmat la sursa (concedii medicale runda 2-3).
    assert procent_cm("07", 10) == Decimal("1.00")
    assert procent_cm("07", 3) == Decimal("1.00")   # nu progresiv - mereu 100%


def test_exces_vacanta_intra_in_baza_salariala():
    """[D3 02.08] Excesul de tichete de vacanta peste plafonul anual (6 sm) = venit SALARIAL in baza:
    CAS+CASS+impozit, NU doar CASS+impozit ca tichetul in plafon (DECIZII 31.07 varianta i)."""
    from datetime import date as _d
    dd = _d(2026, 8, 1)
    base = calcul_salariu(5000, la_data=dd)
    exc = calcul_salariu(5000, la_data=dd, tichet_vacanta_exces=4000)
    assert float(exc["cas"]) - float(base["cas"]) == 1000.0     # 4000 x 25% CAS - CF art.138
    assert float(exc["cass"]) - float(base["cass"]) == 400.0    # 4000 x 10% CASS - CF art.156
    assert float(exc["tichete_vacanta_exces"]) == 4000.0
    inpl = calcul_salariu(5000, la_data=dd, tichet_vacanta=4000)
    assert float(inpl["cas"]) == float(base["cas"]), "tichetul IN plafon NU are CAS (doar CASS+impozit)"
