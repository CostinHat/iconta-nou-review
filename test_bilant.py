# -*- coding: utf-8 -*-
"""Teste motor S1005 (mapare F10/F20)."""
from decimal import Decimal
import bilant

def s(**kw):
    return {k: (Decimal(str(v[0])), Decimal(str(v[1]))) for k, v in kw.items()}

def test_f10_activ_simplu():
    sold = {"212": (100000, 0), "2812": (0, 20000), "371": (5000, 0), "378": (0, 1000),
            "4428": (0, 800), "4111": (3000, 0), "5121": (7000, 0), "5311": (500, 0)}
    r = bilant.f10_din_balanta(sold)
    assert r[2] == 80000
    assert r[4] == 80000
    assert r[5] == 5000 - 1000 - 800
    assert r[6] == 3000
    assert r[8] == 7500
    assert r[9] == r[5] + r[6] + r[8]

def test_f10_pasiv_si_capitaluri():
    sold = {"401": (0, 4000), "421": (0, 2000), "1012": (0, 200), "121": (0, 15000),
            "117": (0, 5000), "5121": (26200, 0)}
    r = bilant.f10_din_balanta(sold)
    assert r[13] == 6000
    assert r[29] == 200
    assert r[41] == 5000
    assert r[43] == 15000
    assert r[46] == 200 + 5000 + 15000
    assert r[49] == r[46]
    # ecuatia bilantiera: F(rd15) = capitaluri+provizioane+ven avans>1an... aici simplu:
    assert r[14] == r[9] - r[13]
    assert r[15] == r[14]

def test_f10_bifunctionale():
    # 431 cu sold creditor -> datorie, nu creanta; 473 debitor -> creanta
    sold = {"431": (0, 900), "473": (150, 0)}
    r = bilant.f10_din_balanta(sold)
    assert r[6] == 150
    assert r[13] == 900

def test_f20_micro():
    rl = {"707": (0, 50000), "709": (500, 0), "607": (30000, 0), "641": (8000, 0),
          "646": (180, 0), "681": (1200, 0), "691": (1600, 0), "765": (0, 300)}
    r = bilant.f20_din_rulaje(rl)
    assert r[1] == 49500
    assert r[2] == 300
    assert r[3] == 30000
    assert r[4] == 8180
    assert r[5] == 1200
    assert r[7] == 1600
    total_v = 49500 + 300
    total_c = 30000 + 8180 + 1200 + 1600 + r[6]
    assert r[8] == total_v - total_c
    assert r[9] == 0

def test_f20_pierdere():
    rl = {"707": (0, 1000), "607": (5000, 0)}
    r = bilant.f20_din_rulaje(rl)
    assert r[8] == 0 and r[9] == 4000

def test_xml_are_antet_si_valori():
    prof = {"cui_numeric": "12345678", "nume": "TEST SRL", "reg_com": "J40/1/2020",
            "caen": "6920", "cod_judet": 40, "declarant_nume": "POPESCU ION"}
    x = bilant.xml_s1005(prof, 2025, {}, {2: 80000, 4: 80000}, {}, {1: 49500, 8: 9000})
    assert 'xmlns="mfp:anaf:dgti:s1005:declaratie:v14"' in x
    assert 'F10_0022="80000"' in x
    assert 'F20_0012="49500"' in x
    assert 'totalPlata_A=' in x
