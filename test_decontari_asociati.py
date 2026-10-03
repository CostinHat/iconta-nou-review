# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import decontari_asociati as m

def test_cota():
    assert m.cota_dividend(date(2025, 12, 31)) == Decimal("10")   # OUG 156/2024 (2025, de la 01.01.2025)
    assert m.cota_dividend(date(2026, 1, 1)) == Decimal("16")

def test_anual():
    r = m.nota_dividend(120000, date(2026, 7, 4))
    assert ("1171", "457", Decimal("120000.00")) in r["linii"]
    assert ("457", "446", Decimal("19200.00")) in r["linii"]
    assert ("457", "5121", Decimal("100800.00")) in r["linii"]

def test_interimar_fara_plata():
    r = m.nota_dividend(50000, date(2026, 7, 4), interimar=True, cu_plata=False)
    assert ("463", "456", Decimal("50000.00")) in r["linii"]
    assert ("456", "446", Decimal("8000.00")) in r["linii"]
    assert len(r["linii"]) == 2

def test_regularizare_normala():
    r = m.nota_regularizare_interimar(50000, 80000)
    assert ("1171", "457", Decimal("80000.00")) in r["linii"]
    assert ("457", "463", Decimal("50000.00")) in r["linii"]
    assert r["exces_de_restituit"] == Decimal("0.00")

def test_regularizare_exces():
    # GARD [28.09.2026]: restituirea excesului de dividende interimare crediteaza contul 463
    # (OMFP 3067/2018: creditul 463 = «sumele incasate reprezentand restituiri de dividende ... (512, 531)»),
    # NU contul 456 (dividende de plata, deja soldat). MUTATIE: 463->456 face aserția sa pice.
    # [lot 19 d9, 03.10.2026] regularizarea NU mai poarta restituirea (era 5121=463 la brut, datata la aprobare):
    # restituirea se inregistreaza la INCASARE, cu suma incasata (nota_restituire_dividend)
    r = m.nota_regularizare_interimar(150000, 140000, impozit_interimar=15000)
    assert ("457", "463", Decimal("140000.00")) in r["linii"]
    assert not any(d == "5121" for d, c, _ in r["linii"]), "regularizarea nu inregistreaza incasari"
    assert (r["net_de_restituit"], r["impozit_de_recuperat"]) == (Decimal("9000.00"), Decimal("1000.00"))
    rest = [m.nota_restituire_dividend(r["net_de_restituit"]), m.nota_restituire_dividend(r["impozit_de_recuperat"])]
    linii = r["linii"] + [l for x in rest for l in x["linii"]]
    assert not any(d == "5121" and c == "456" for d, c, _ in linii), "restituirea NU se crediteaza in 456"
    # invariant: 463 debitat la distribuire (150000) se inchide prin creditele 463 (compensare 457=463 + cele doua
    # incasari 5121=463 — de la asociat netul, de la buget impozitul)
    credit_463 = sum(v for d, c, v in linii if c == "463")
    assert credit_463 == Decimal("150000.00"), "creditul total 463 (compensare + restituiri) inchide interimarul"

def test_imprumut():
    assert m.nota_imprumut_asociat(20000)["linii"] == [("5121", "4551", Decimal("20000.00"))]
    r = m.nota_imprumut_asociat(20000, "restituire", dobanda=1000)
    assert ("4551", "5121", Decimal("20000.00")) in r["linii"]
    assert ("666", "4551", Decimal("1000.00")) in r["linii"]
    assert ("4551", "446", Decimal("100.00")) in r["linii"]
    assert ("4551", "5121", Decimal("900.00")) in r["linii"]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota_dividend(0)
