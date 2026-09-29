# -*- coding: utf-8 -*-
"""GARD [3i, CF art. 282 alin. (9)]: storno-ul unei facturi cu cota 19% (emisa inainte de 01.08.2025)
valideaza COTA pe data operatiunii de baza, nu pe data storno-ului. Fara asta, storno-ul era RESPINS
(19% nu exista in cotele de azi {0,11,21}).
"""
import io
import os
import re
from datetime import date
from core import facturi_api as fa

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_cota_19_valida_la_data_bazei_invalida_azi():
    # invariantul de fond: 19% e valida pe data operatiunii de baza (2025-03-15) si INVALIDA azi.
    linii = [{"cota_tva": 19}]
    assert fa._cota_necunoscuta(linii, date(2025, 3, 15)) is None, "19% era valida inainte de 01.08.2025"
    assert fa._cota_necunoscuta(linii, date.today()) is not None, "19% NU mai e valida azi (motivul patch-ului)"


def test_storneaza_paseaza_cota_la_data_bazei():
    # cablare: storneaza trece cota_la_data=orig.get("data_emitere") -> verificarea cotei pe data de
    # baza. MUTATIE: scoate `cota_la_data=orig.get("data_emitere")` -> assert pica.
    s = io.open(os.path.join(RAD, "core", "facturi_api.py"), encoding="utf-8").read()
    assert re.search(r'cota_la_data=orig\.get\("data_emitere"\)', s), \
        "storneaza nu mai paseaza cota_la_data=data_emitere (art.282(9) necablat)"
    assert re.search(r"def creeaza_factura\(.*cota_la_data=None", s, re.S), \
        "creeaza_factura nu mai accepta cota_la_data"
