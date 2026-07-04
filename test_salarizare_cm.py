# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
import pytest
from core import salarizare as s

def test_cod01_progresiv():
    assert s.procent_cm("01", 5) == Decimal("0.55")
    assert s.procent_cm("01", 10) == Decimal("0.65")
    assert s.procent_cm("01", 20) == Decimal("0.75")

def test_coduri_100():
    for c in ("05", "06", "12", "14", "51"):
        assert s.procent_cm(c, 10) == Decimal("1.00"), c

def test_coduri_85():
    assert s.procent_cm("08", 10) == Decimal("0.85")
    assert s.procent_cm("09", 10) == Decimal("0.85")

def test_coduri_75():
    for c in ("07", "13", "15"):
        assert s.procent_cm(c, 10) == Decimal("0.75"), c

def test_accident_param():
    assert s.procent_cm("03", 10) == Decimal("1.00")
    assert s.procent_cm("03", 10, procent_accident=80) == Decimal("0.80")

def test_cod10_refuza_procent():
    with pytest.raises(ValueError, match="art. 19"):
        s.procent_cm("10", 10)

def test_cod10_formula():
    # baza 5000, venit realizat 4200 -> dif 800, plafon 1250 -> 800
    assert s.calcul_cm_cod10(5000, 4200) == Decimal("800.00")
    # dif 2000 > plafon 1250 -> 1250
    assert s.calcul_cm_cod10(5000, 3000) == Decimal("1250.00")

def test_prima_zi_exceptii():
    # cod 08 maternitate: FARA diminuare (Legea 64/2026)
    r = s.calcul_cm(27000, 129, 10, cod="08", zile_episod=10,
                    la_data=date(2026, 7, 2))
    assert r["diminuare"] == 0
    # cod 15 risc maternal: FARA diminuare
    r = s.calcul_cm(27000, 129, 10, cod="15", zile_episod=10,
                    la_data=date(2026, 7, 2))
    assert r["diminuare"] == 0
    # cod 01: CU diminuare
    r = s.calcul_cm(27000, 129, 10, cod="01", zile_episod=10,
                    la_data=date(2026, 7, 2))
    assert r["diminuare"] == 1
    # cod 01 dar exceptat (cronic/program national): FARA
    r = s.calcul_cm(27000, 129, 10, cod="01", zile_episod=10,
                    la_data=date(2026, 7, 2), exceptat_prima_zi=True)
    assert r["diminuare"] == 0
