# -*- coding: utf-8 -*-
from core.kpi_client import kpi_din_balanta


def _r(cont, **k):
    b = {"cont": cont, "denumire": "", "si_d": 0, "si_c": 0,
         "rul_d": 0, "rul_c": 0, "sf_d": 0, "sf_c": 0}
    b.update(k)
    return b


def test_pl_simplu():
    bal = [_r("704", rul_c=1000), _r("628", rul_d=400)]
    k = kpi_din_balanta(bal)
    assert k["venituri"] == 1000
    assert k["cheltuieli"] == 400
    assert k["profit"] == 600


def test_storno_venit():
    bal = [_r("704", rul_c=1000, rul_d=100), _r("601", rul_d=300)]
    k = kpi_din_balanta(bal)
    assert k["venituri"] == 900
    assert k["profit"] == 600


def test_cash_creante_datorii():
    bal = [_r("5121", sf_d=5000), _r("5311", sf_d=800),
           _r("4111", sf_d=2500), _r("401", sf_c=1200)]
    k = kpi_din_balanta(bal)
    assert k["cash"] == 5800
    assert k["de_incasat"] == 2500
    assert k["de_platit"] == 1200


def test_gol():
    k = kpi_din_balanta([])
    assert k["profit"] == 0 and k["cash"] == 0
