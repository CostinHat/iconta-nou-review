# -*- coding: utf-8 -*-
"""Teste gardian pentru control_incrucisat.compara_tva (functia PURA).
Principii aparate: trei stari (verde/rosu/gri), remediu executabil DOAR cu cauza
dovedita, NICIODATA sugestie de ajustare a contului ca sa dea verde.
"""
from decimal import Decimal
from core.control_incrucisat import compara_tva, TOLERANTA


def _rulaje(colectata=0, dedusa=0):
    return {"4427": {"credit": Decimal(str(colectata)), "debit": Decimal("0")},
            "4426": {"debit": Decimal(str(dedusa)), "credit": Decimal("0")}}


def test_coerent_da_verde():
    r = compara_tva({"R17_2": 21, "R31_2": 0}, _rulaje(colectata=21))
    assert r[0]["stare"] == "verde"
    assert r[0]["remediu"] is None


def test_toleranta_1_leu_rotunjire_d300():
    # D300 rotunjeste la leu: 95 vs 94.50 contabil = coerent
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=Decimal("94.50")))
    assert r[0]["stare"] == "verde"


def test_divergenta_explicata_de_facturi_necontate_da_remediu_executabil():
    necontate = [
        {"id": 2, "directie": "emisa", "tva": Decimal("21.00")},
        {"id": 3, "directie": "emisa", "tva": Decimal("52.50")},
    ]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["diferenta"] == Decimal("74")
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [2, 3]


def test_divergenta_neexplicata_da_investigatie_nu_ajustare():
    # diferenta NU se explica prin necontate -> investigatie, fara buton
    necontate = [{"id": 2, "directie": "emisa", "tva": Decimal("5.00")}]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "investigatie"
    assert c["remediu"]["facturi"] == []
    # PRINCIPIU: nu propunem ajustarea contului ca sa dea verde
    txt = (c["remediu"]["actiune"] + c["remediu"]["cauza"]).lower()
    assert "ajusteaz" not in txt and "modifica contul" not in txt


def test_fiecare_constatare_isi_declara_temeiul():
    r = compara_tva({"R17_2": 21, "R31_2": 0}, _rulaje(colectata=21))
    for c in r:
        assert c["temei"]
        assert "D300" in c["temei"]


def test_temei_corect_pe_directie():
    r = compara_tva({"R17_2": 0, "R31_2": 0}, _rulaje())
    assert "emise" in r[0]["temei"]      # colectata <- facturi emise
    assert "primite" in r[1]["temei"]    # deductibila <- facturi primite


def test_deductibila_necontata_primite():
    necontate = [{"id": 9, "directie": "primita", "tva": Decimal("10.00")}]
    r = compara_tva({"R17_2": 0, "R31_2": 10}, _rulaje(dedusa=0), necontate)
    c = r[1]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [9]


def test_ciorna_nu_da_verde_asteapta_validare():
    """O nota ciorna e propunere, nu evidenta: constatarea ramane rosie pana la patru-ochi."""
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    assert r[0]["stare"] == "rosu"
    assert r[0]["remediu"]["fel"] == "sugerat"
    assert "ciorn" in r[0]["remediu"]["cauza"]
    assert r[0]["remediu"]["facturi"] == []


def test_mixt_executabil_doar_pe_facturile_fara_nota():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("40"), "are_ciorna": True},
                 {"id": 2, "directie": "emisa", "tva": Decimal("34"), "are_ciorna": False}]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    assert r[0]["remediu"]["fel"] == "executabil"
    assert r[0]["remediu"]["facturi"] == [2]
    assert "ciorn" in r[0]["remediu"]["cauza"]


def test_o_factura_cu_ciorna_nu_intra_niciodata_intr_un_remediu_executabil():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True},
                 {"id": 2, "directie": "primita", "tva": Decimal("10"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R31_2": 10}, _rulaje(colectata=21, dedusa=0), necontate)
    for c in r:
        rem = c.get("remediu") or {}
        if rem.get("fel") == "executabil":
            assert 1 not in rem["facturi"] and 2 not in rem["facturi"]
