# -*- coding: utf-8 -*-
from decimal import Decimal
from core.reconciliere import potriveste_linie, potriveste_extras, facturi_partener

def F(id, cui, sold, directie="emisa", data="2026-06-01"):
    return {"id": id, "tert_cui": cui, "directie": directie,
            "data_emitere": data, "sold": Decimal(str(sold))}

def L(suma, cui, tip="incasare"):
    return {"suma": Decimal(str(suma)), "tip": tip, "cui": cui,
            "descriere": "", "data": "2026-07-01"}

FACTURI = [
    F(1, "12345678", "1000.00", data="2026-05-01"),
    F(2, "12345678", "250.50",  data="2026-05-10"),
    F(3, "12345678", "749.50",  data="2026-05-20"),
    F(4, "99999999", "500.00"),
    F(5, "12345678", "300.00", directie="primita"),
]

# --- rosu ---
def test_fara_cui():
    r = potriveste_linie(L("100", None), FACTURI)
    assert r["status"] == "rosu" and r["alocari"] == []

def test_cui_necunoscut():
    r = potriveste_linie(L("100", "11111111"), FACTURI)
    assert r["status"] == "rosu"

def test_directie_gresita():
    # incasare nu se potriveste pe facturi primite
    r = potriveste_linie(L("300", "12345678"), [F(5, "12345678", "300.00", directie="primita")])
    assert r["status"] == "rosu"

# --- verde ---
def test_exact_o_factura():
    r = potriveste_linie(L("1000.00", "12345678"), FACTURI)
    assert r["status"] == "verde"
    assert r["alocari"] == [{"factura_id": 1, "suma": Decimal("1000.00")}]

def test_exact_cu_prefix_ro():
    r = potriveste_linie(L("1000.00", "RO12345678"), FACTURI)
    assert r["status"] == "verde" and r["alocari"][0]["factura_id"] == 1

def test_combo_doua_facturi():
    r = potriveste_linie(L("1000.00", "12345678"),
                         [F(2, "12345678", "250.50"), F(3, "12345678", "749.50")])
    assert r["status"] == "verde"
    assert {a["factura_id"] for a in r["alocari"]} == {2, 3}

def test_plata_furnizor():
    r = potriveste_linie(L("300.00", "12345678", tip="plata"), FACTURI)
    assert r["status"] == "verde" and r["alocari"][0]["factura_id"] == 5

def test_toleranta_un_ban():
    r = potriveste_linie(L("1000.01", "12345678"), [F(1, "12345678", "1000.00")])
    assert r["status"] == "verde"

# --- galben ---
def test_partial_fifo_cea_mai_veche():
    r = potriveste_linie(L("400.00", "12345678"), FACTURI)
    assert r["status"] == "galben"
    assert r["alocari"] == [{"factura_id": 1, "suma": Decimal("400.00")}]

def test_fifo_peste_doua_facturi():
    r = potriveste_linie(L("1100.00", "12345678"),
                         [F(1, "12345678", "1000.00", data="2026-05-01"),
                          F(2, "12345678", "250.50", data="2026-05-10")])
    assert r["status"] == "galben"
    assert r["alocari"][0] == {"factura_id": 1, "suma": Decimal("1000.00")}
    assert r["alocari"][1] == {"factura_id": 2, "suma": Decimal("100.00")}

def test_suma_peste_sold_total():
    r = potriveste_linie(L("5000.00", "99999999"), FACTURI)
    assert r["status"] == "galben" and "rest nealocat" in r["motiv"]
    assert r["alocari"] == [{"factura_id": 4, "suma": Decimal("500.00")}]

# --- secvential ---
def test_extras_consuma_soldurile():
    linii = [L("1000.00", "12345678"), L("1000.00", "12345678")]
    r = potriveste_extras(linii, FACTURI)
    assert r[0]["status"] == "verde" and r[0]["alocari"][0]["factura_id"] == 1
    # factura 1 consumata; a doua linie -> combo 2+3
    assert r[1]["status"] == "verde"
    assert {a["factura_id"] for a in r[1]["alocari"]} == {2, 3}

def test_facturi_partener_fifo():
    f = facturi_partener(FACTURI, "12345678", "incasare")
    assert [x["id"] for x in f] == [1, 2, 3]
