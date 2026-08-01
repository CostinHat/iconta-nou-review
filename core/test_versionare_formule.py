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
    assert sz.procent_cm("01", 10, la_data=date(2026, 6, 1)) == sz._procent_cm_2018("01", 10)
    assert sz._VARIANTE_PROCENT_CM[0][1] is sz._procent_cm_2018
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
    assert dc.plafon_diurna(*args, la_data=date(2026, 6, 1)) == dc._plafon_diurna_2018(*args)
    assert dc._VARIANTE_PLAFON_DIURNA[0][1] is dc._plafon_diurna_2018
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
