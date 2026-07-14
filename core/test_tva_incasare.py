# -*- coding: utf-8 -*-
"""Teste gardian pentru core/tva_incasare.py (art. 282 CF, OUG 8/2026).
Suta marita: TVA exigibil = suma x cota/(100+cota). Verificat contra sursei.
"""
from decimal import Decimal
from core.tva_incasare import tva_din_incasare, tva_exigibil_alocari, plafon_la


def test_incasare_partiala_proportional():
    # factura 1210 (1000+210), incasare 605 -> jumatate din TVA
    assert tva_din_incasare(605, 21) == Decimal("105.00")


def test_incasare_totala_tot_tva():
    assert tva_din_incasare(1210, 21) == Decimal("210.00")


def test_cota_redusa_11():
    assert tva_din_incasare(555, 11) == Decimal("55.00")


def test_suma_negativa_ridica_eroare():
    import pytest
    with pytest.raises(ValueError):
        tva_din_incasare(0, 21)


def test_alocari_mixte_pe_cote():
    r = tva_exigibil_alocari([{"suma": 605, "cota_tva": 21},
                              {"suma": 555, "cota_tva": 11}])
    assert r["total"] == Decimal("160.00")
    assert {l["cota"]: l["tva"] for l in r["linii"]} == {"21": "105.00", "11": "55.00"}


def test_plafon_pe_data():
    assert plafon_la("2026-02-01") == Decimal("4500000")
    assert plafon_la("2026-06-01") == Decimal("5000000")
    assert plafon_la("2027-01-01") == Decimal("5500000")
