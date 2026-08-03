# -*- coding: utf-8 -*-
"""Versionarea formulelor pe la_data (PAS 1 tipar). Cotele sunt period-aware (cota); formulele devin
period-aware prin alege_varianta (tiparul cota() pe cod). O schimbare de regula = varianta datata noua,
nu 'if data' - trecutul ramane calculabil (adeverinte/rectificative pe o luna trecuta)."""
from datetime import date

import pytest

from core import common as c, salarizare as sz


def test_alege_varianta_pe_data():
    """MECANISMUL de versionare: 2 variante datate, dispecerul alege dupa la_data. Varianta 2099 e
    IPOTETICA (nu exista schimbare reala de scara in istoricul deducerii) - testeaza infrastructura, NU o
    valoare fiscala. Doua functii-marker (100 vs 999): la_data 2026 -> 2018; la_data 2099 -> 2099."""
    v2018 = lambda brut, **k: {"total": 100}
    v2099 = lambda brut, **k: {"total": 999}
    reg = [("2018-01-01", v2018, c.Temei("CF", art="77")),
           ("2099-01-01", v2099, c.Temei("Legea", 1, 2099))]
    fn, _ = c.alege_varianta(reg, date(2026, 1, 1))
    assert fn(1000)["total"] == 100
    fn2, t2 = c.alege_varianta(reg, date(2099, 6, 1))
    assert fn2(1000)["total"] == 999 and t2.an == 2099


def test_alege_varianta_ridica_pe_gol():
    with pytest.raises(ValueError):
        c.alege_varianta([("2018-01-01", lambda **k: 1, c.Temei("CF"))], date(2000, 1, 1))


def test_deducere_personala_dispecer_pastreaza_comportament():
    """Dispecerul da acelasi rezultat ca varianta directa (refactor fara schimbare de comportament)."""
    d = date(2026, 7, 1)
    assert sz.deducere_personala(3000, persoane=2, la_data=d) == sz._deducere_personala_2018(3000, persoane=2, la_data=d)
    assert len(sz._VARIANTE_DEDUCERE) == 1 and sz._VARIANTE_DEDUCERE[0][1] is sz._deducere_personala_2018


def test_calcul_cm_diminuare_versionata_pe_fereastra():
    """PAS 2c: diminuarea de 1 zi (Ordinul 506/1030/2026) e versionata pe fereastra 01.02.2026-31.12.2027.
    In fereastra -> diminuare 1; inainte (2025) sau dupa expirare (2028) -> 0. Fara 'if pe data' in corp."""
    from core.salarizare import calcul_cm
    assert calcul_cm(30000, 120, 10, cod="01", la_data=date(2026, 6, 1))["diminuare"] == 1
    assert calcul_cm(30000, 120, 10, cod="01", la_data=date(2025, 6, 1))["diminuare"] == 0
    assert calcul_cm(30000, 120, 10, cod="01", la_data=date(2028, 6, 1))["diminuare"] == 0


# ============================================================
#  PAS 3 - salarizare.py (procent_cm, taxe_cm, calcul_cm_cod10, calcul_salariu)
#  Fiecare: dispecerul pastreaza comportamentul variantei datate + e period-aware
#  (data inainte de prima varianta ridica - formula NU mai ignora la_data).
# ============================================================
def test_procent_cm_dispecer_versionat():
    from core import salarizare as sz
    assert sz.procent_cm("01", 10, la_data=date(2026, 6, 1)) == sz._procent_cm_l141_2025("01", 10)
    assert sz._VARIANTE_PROCENT_CM[0][1] is sz._procent_cm_l141_2025
    with pytest.raises(ValueError):
        sz.procent_cm("01", 10, la_data=date(2000, 1, 1))


def test_calcul_cm_cod10_dispecer_versionat():
    from core import salarizare as sz
    assert sz.calcul_cm_cod10(3000, 1000, la_data=date(2026, 6, 1)) == sz._calcul_cm_cod10_2018(3000, 1000)
    assert sz._VARIANTE_CALCUL_CM_COD10[0][1] is sz._calcul_cm_cod10_2018
    with pytest.raises(ValueError):
        sz.calcul_cm_cod10(3000, 1000, la_data=date(2000, 1, 1))


def test_taxe_cm_dispecer_versionat():
    from core import salarizare as sz
    d = date(2026, 6, 1)
    assert sz.taxe_cm(2000, cod="01", la_data=d) == sz._taxe_cm_2018(2000, cod="01", la_data=d)
    assert sz._VARIANTE_TAXE_CM[0][1] is sz._taxe_cm_2018
    with pytest.raises(ValueError):
        sz.taxe_cm(2000, cod="01", la_data=date(2000, 1, 1))


def test_calcul_salariu_dispecer_versionat():
    from core import salarizare as sz
    d = date(2026, 6, 1)
    assert sz.calcul_salariu(4000, persoane=1, la_data=d) == sz._calcul_salariu_2018(4000, persoane=1, la_data=d)
    assert sz._VARIANTE_CALCUL_SALARIU[0][1] is sz._calcul_salariu_2018
    with pytest.raises(ValueError):
        sz.calcul_salariu(4000, la_data=date(2000, 1, 1))


# ---- PAS 3 modul 2: deconturi.plafon_diurna ----
def test_plafon_diurna_dispecer_versionat():
    from core import deconturi as dc
    args = (30, 5, 4000, 21)  # diurna_pe_zi, zile, salariu_baza, zile_lucratoare_luna
    # 2026 -> varianta 23 lei (Ordin MF 1235/2023); dispecerul == functia cu default curent (23)
    assert dc.plafon_diurna(*args, la_data=date(2026, 6, 1)) == dc._plafon_diurna(*args)
    # PERIOD-AWARE: diurna bugetara 20 lei in 2020 (HG 714/2018) < 23 lei in 2026 -> plafoane 2,5x diferite
    assert (dc.plafon_diurna(*args, la_data=date(2020, 6, 1))["limita_2_5x"]
            < dc.plafon_diurna(*args, la_data=date(2026, 6, 1))["limita_2_5x"])
    with pytest.raises(ValueError):
        dc.plafon_diurna(*args, la_data=date(2000, 1, 1))


# ---- PAS 3 modul 3: sponsorizari.plafon_credit + credit_sponsorizare ----
def test_plafon_credit_dispecer_versionat():
    from core import sponsorizari as sp
    args = (1000000, 50000)  # cifra_afaceri, impozit_profit
    assert sp.plafon_credit(*args, la_data=date(2026, 6, 1)) == sp._plafon_credit_2018(*args)
    assert sp._VARIANTE_PLAFON_CREDIT[0][1] is sp._plafon_credit_2018
    with pytest.raises(ValueError):
        sp.plafon_credit(*args, la_data=date(2000, 1, 1))


def test_credit_sponsorizare_dispecer_versionat():
    from core import sponsorizari as sp
    args = (1000000, 50000, 5000)  # cifra_afaceri, impozit_profit, sponsorizari_efectuate
    assert sp.credit_sponsorizare(*args, la_data=date(2026, 6, 1)) == sp._credit_sponsorizare_2018(*args)
    assert sp._VARIANTE_CREDIT_SPONSORIZARE[0][1] is sp._credit_sponsorizare_2018
    with pytest.raises(ValueError):
        sp.credit_sponsorizare(*args, la_data=date(2000, 1, 1))


# ---- PAS 3 modul 4: motor.rezerva_legala ----
def test_rezerva_legala_dispecer_versionat():
    from core import motor as mo
    args = (100000, 50000)  # profit, capital_social
    assert mo.rezerva_legala(*args, la_data=date(2026, 6, 1)) == mo._rezerva_legala_2018(*args)
    assert mo._VARIANTE_REZERVA_LEGALA[0][1] is mo._rezerva_legala_2018
    with pytest.raises(ValueError):
        mo.rezerva_legala(*args, la_data=date(2000, 1, 1))


# ---- PAS 3 modul 5: contracte_speciale.calcul_zilier ----
def test_calcul_zilier_dispecer_versionat():
    from core import contracte_speciale as cs
    # 2026 -> varianta cu CAS (de la 01.05.2019)
    assert cs.calcul_zilier(200, la_data=date(2026, 6, 1)) == cs._calcul_zilier_2019(200)
    # PERIOD-AWARE: pana la 01.05.2019 zilierii NU datorau CAS (doar impozit 10% pe brut)
    r18 = cs.calcul_zilier(100, la_data=date(2018, 6, 1))
    assert r18["cas"] == 0 and r18["impozit"] == 10 and r18["net"] == 90, r18
    r19 = cs.calcul_zilier(100, la_data=date(2019, 6, 1))
    assert r19["cas"] == 25, r19
    with pytest.raises(ValueError):
        cs.calcul_zilier(200, la_data=date(2000, 1, 1))


# ---- PAS 3 modul 6: tva_marja.vanzare_marja ----
def test_tva_marja_formula_suta_marita_art312():
    """TVA pe marja second-hand = marja x cota/(100+cota) - suta MARITA (TVA INCLUS in marja, se
    extrage), conform CF art.312 alin.(4): baza = marja profitului EXCLUSIV valoarea taxei aferente.
    NU cota/100. Marja negativa/zero -> TVA 0 (se reporteaza, nu se restituie)."""
    from core.tva_marja import vanzare_marja
    from decimal import Decimal as _D
    r = vanzare_marja(1000, 600, cota=21, la_data=date(2026, 6, 1))    # marja 400
    assert r["tva"] == _D("69.42"), r            # 400*21/121 (NU 84 = 400*0.21)
    assert r["marja_neta"] == _D("330.58"), r
    rn = vanzare_marja(600, 1000, cota=21, la_data=date(2026, 6, 1))   # marja negativa
    assert rn["tva"] == _D("0.00"), rn
    r19 = vanzare_marja(1000, 600, cota=19, la_data=date(2026, 6, 1))  # cota epoca 19%
    assert r19["tva"] == _D("63.87"), r19


def test_vanzare_marja_dispecer_versionat():
    from core import tva_marja as tm
    assert tm.vanzare_marja(1000, 600, la_data=date(2026, 6, 1)) == tm._vanzare_marja_2018(1000, 600)
    assert tm._VARIANTE_VANZARE_MARJA[0][1] is tm._vanzare_marja_2018
    with pytest.raises(ValueError):
        tm.vanzare_marja(1000, 600, la_data=date(2000, 1, 1))


# ---- PAS 3 modul 7: tva_marja_turism.marja_turism_special ----
def test_marja_turism_formula_suta_marita_si_scutire_non_ue_art311():
    """TVA pe marja de turism (CF art.311): suta MARITA marja x cota/(100+cota) pe partea TAXABILA;
    scutire PROPORTIONALA alin.(5) pentru partea serviciilor prestate in afara UE. Marja negativa -> 0."""
    from core.tva_marja_turism import marja_turism_special
    from decimal import Decimal as _D
    # tot UE: marja 400, cota 21 -> TVA 400*21/121 = 69,42 (ca art.312), fara scutire
    r = marja_turism_special(1000, 600, 0, cota=21, la_data=date(2026, 6, 1))
    assert r["tva"] == _D("69.42") and r["marja_scutita"] == _D("0.00"), r
    # 50%% non-UE: cost 300 UE + 300 non-UE, marja 400 -> scutita 200, taxabila 200 -> TVA 200*21/121 = 34,71
    rn = marja_turism_special(1000, 300, 300, cota=21, la_data=date(2026, 6, 1))
    assert rn["marja_scutita"] == _D("200.00") and rn["tva"] == _D("34.71"), rn
    # marja negativa -> TVA 0
    rneg = marja_turism_special(500, 600, 0, cota=21, la_data=date(2026, 6, 1))
    assert rneg["tva"] == _D("0.00"), rneg


def test_marja_turism_special_dispecer_versionat():
    from core import tva_marja_turism as tt
    a = (10000, 6000, 1000)  # incasat, cost_ue, cost_non_ue
    assert tt.marja_turism_special(*a, la_data=date(2026, 6, 1)) == tt._marja_turism_special_2018(*a)
    assert tt._VARIANTE_MARJA_TURISM[0][1] is tt._marja_turism_special_2018
    with pytest.raises(ValueError):
        tt.marja_turism_special(*a, la_data=date(2000, 1, 1))
