# -*- coding: utf-8 -*-
import datetime
from core.cashflow import din_facturi, forecast

AZI = datetime.date(2026, 7, 6)


# [lotul 13, 553 + 559] `aloca_sold` (soldul balanței împărțit pe facturi „de la cele mai noi”) s-a înlocuit cu `din_facturi`: facturile
# deschise cu restul lor în lei, fiecare la scadența ei, iar ce arată balanța peste ele intră o dată, numit
def test_din_facturi_fiecare_la_scadenta_ei():
    f = [{"data_scadenta": "2026-01-15", "rest_lei": 100}, {"data_scadenta": "2026-06-15", "rest_lei": 200}]
    d = din_facturi(f, 300, "facturi", "fără factură", AZI)
    assert [(x["data_scadenta"], x["suma"], x["ce"]) for x in d] == [("2026-01-15", 100, "facturi"), ("2026-06-15", 200, "facturi")]


def test_din_facturi_soldul_peste_facturi_intra_o_data_numit():
    d = din_facturi([{"data_scadenta": None, "data_emitere": "2026-06-01", "rest_lei": 100}], 250, "facturi", "fără factură", AZI)
    assert [(x["data_scadenta"], x["suma"], x["ce"]) for x in d] == [("2026-06-01", 100, "facturi"), ("2026-07-06", 150, "fără factură")]


def test_din_facturi_fara_sold_in_plus():
    assert din_facturi([], 0, "facturi", "fără factură", AZI) == []


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
    b = {"cont": cont, "denumire": "", "si_d": 0, "si_c": 0, "prec_d": 0, "prec_c": 0,
         "rul_d": 0, "rul_c": 0, "tot_d": 0, "tot_c": 0, "sf_d": 0, "sf_c": 0}
    b.update(k)
    return b


def test_obligatii():
    from core.cashflow import obligatii_din_balanta
    bal = [_rb("4423", sf_c=1000), _rb("4315", sf_c=500), _rb("421", sf_c=3000), _rb("401", sf_c=999)]
    o = obligatii_din_balanta(bal)
    assert o["fiscale"] == 1500 and o["salarii_nete"] == 3000


def test_cheltuieli_cash_exclude_amortizare():
    """[lotul 13, 553] salariile (641) intră în medie — 421 / 431 din balanță acoperă numai luna trecută; amortizarea (6811) nu."""
    from core.cashflow import cheltuieli_lunare_cash
    bal = [_rb("628", rul_d=6000), _rb("6811", rul_d=1200), _rb("641", rul_d=9000)]
    assert cheltuieli_lunare_cash(bal, 6) == 2500


def test_plati_estimate_scadente():
    from core.cashflow import plati_estimate
    p = plati_estimate({"fiscale": 1500, "salarii_nete": 3000}, 1000, azi=AZI, saptamani=8)
    assert p[0]["suma"] == 3000 and p[0]["data_scadenta"] == "2026-07-06"
    # 25.07.2026 e sambata -> termenul e luni 27 (scadente.termen_legal), nu sambata
    assert p[1]["suma"] == 1500 and p[1]["data_scadenta"] == "2026-07-27"
    assert any(x["suma"] == 1000 for x in p)


def test_plati_estimate_decembrie_pe_21():
    from core.cashflow import plati_estimate
    # CPF art.155 alin.(2): ce se împlinește la 25 decembrie „se declară până la data de 21 decembrie”
    p = plati_estimate({"fiscale": 1500}, 0, azi=datetime.date(2026, 12, 10))
    assert p[0]["data_scadenta"] == "2026-12-21"
    p = plati_estimate({"fiscale": 1500}, 0, azi=datetime.date(2026, 12, 22))
    assert p[0]["data_scadenta"] == "2027-01-25"
