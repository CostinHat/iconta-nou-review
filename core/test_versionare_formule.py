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
