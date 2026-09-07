# -*- coding: utf-8 -*-
import datetime
from core.cashflow import aloca_sold, forecast

AZI = datetime.date(2026, 7, 6)


def test_aloca_noi_intai():
    f = [{"data_scadenta": "2026-01-15", "total": 100},
         {"data_scadenta": "2026-06-15", "total": 200}]
    d = aloca_sold(f, 200)
    assert len(d) == 1 and d[0]["suma"] == 200 and d[0]["data_scadenta"] == "2026-06-15"


def test_aloca_partial():
    f = [{"data_scadenta": "2026-01-15", "total": 100},
         {"data_scadenta": "2026-06-15", "total": 200}]
    d = aloca_sold(f, 250)
    assert d[0]["suma"] == 200 and d[1]["suma"] == 50


def test_aloca_zero():
    assert aloca_sold([{"data_scadenta": "2026-06-15", "total": 100}], 0) == []


def test_forecast_scadenta_trecuta_in_s1():
    emise = [{"data_scadenta": "2026-06-01", "suma": 500}]
    r = forecast(1000, emise, [], azi=AZI, saptamani=2)
    assert r[0]["incasari"] == 500 and r[0]["sold"] == 1500
    assert r[1]["incasari"] == 0 and r[1]["sold"] == 1500


def test_forecast_plati():
    primite = [{"data_scadenta": "2026-07-10", "suma": 300}]
    r = forecast(1000, [], primite, azi=AZI, saptamani=2)
    assert r[0]["plati"] == 300 and r[0]["sold"] == 700


def test_forecast_saptamana_viitoare():
    emise = [{"data_scadenta": "2026-07-15", "suma": 400}]
    r = forecast(0, emise, [], azi=AZI, saptamani=3)
    assert r[0]["incasari"] == 0 and r[1]["incasari"] == 400 and r[2]["sold"] == 400


def _rb(cont, **k):
    b = {"cont": cont, "denumire": "", "si_d": 0, "si_c": 0,
         "rul_d": 0, "rul_c": 0, "sf_d": 0, "sf_c": 0}
    b.update(k)
    return b


def test_obligatii():
    from core.cashflow import obligatii_din_balanta
    bal = [_rb("4423", sf_c=1000), _rb("4315", sf_c=500), _rb("421", sf_c=3000), _rb("401", sf_c=999)]
    o = obligatii_din_balanta(bal)
    assert o["fiscale"] == 1500 and o["salarii_nete"] == 3000


def test_cheltuieli_cash_exclude_amortizare():
    from core.cashflow import cheltuieli_lunare_cash
    bal = [_rb("628", rul_d=6000), _rb("6811", rul_d=1200), _rb("641", rul_d=9000)]
    assert cheltuieli_lunare_cash(bal, 6) == 1000


def test_plati_estimate_scadente():
    from core.cashflow import plati_estimate
    p = plati_estimate({"fiscale": 1500, "salarii_nete": 3000}, 1000, azi=AZI, saptamani=8)
    assert p[0]["suma"] == 3000 and p[0]["data_scadenta"] == "2026-07-06"
    assert p[1]["suma"] == 1500 and p[1]["data_scadenta"] == "2026-07-25"
    assert any(x["suma"] == 1000 for x in p)
