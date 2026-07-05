# -*- coding: utf-8 -*-
from core.woocommerce import comanda_in_factura


def test_comanda_simpla():
    c = {"number": "13", "date_created": "2026-07-05T08:09:42", "currency": "USD",
         "total": "800.00",
         "billing": {"company": "POPESCU SRL", "first_name": "Ion", "last_name": "Popescu"},
         "line_items": [{"name": "Abonament lunar", "quantity": 1, "total": "500.00"},
                        {"name": "Consultanta ora", "quantity": 2, "total": "300.00"}]}
    f = comanda_in_factura(c)
    assert f["sursa_numar"] == "13" and f["data"] == "2026-07-05"
    assert f["tert_nume"] == "POPESCU SRL"
    assert f["linii"][0]["pret_unitar"] == 500.0
    assert f["linii"][1]["pret_unitar"] == 150.0


def test_fara_companie():
    c = {"id": 5, "billing": {"first_name": "Ana", "last_name": "Pop"},
         "line_items": [{"name": "x", "quantity": 1, "total": "10"}]}
    f = comanda_in_factura(c)
    assert f["tert_nume"] == "Ana Pop" and f["sursa_numar"] == "5"
