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
    for c in ("05", "06", "07", "12", "14", "51"):   # 07 carantina 100% (art.20(3), Legea 136/2020)
        assert s.procent_cm(c, 10) == Decimal("1.00"), c

def test_coduri_85():
    assert s.procent_cm("08", 10) == Decimal("0.85")
    assert s.procent_cm("09", 10) == Decimal("0.85")

def test_coduri_75():
    for c in ("13", "15"):   # 07 mutat la 100% (carantina); raman cardiovasculare/risc maternal
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


def test_nc28_exceptii_diminuare():
    # Ordinul 506/1030/2026 MOF 507 - verificat la sursa. Izolare 51: SE DIMINUEAZA (decizie Costin
    # 09.08.2026 - norma nu o excepta; nu mai e in lista de exceptii). d=07.2026 -> exceptiile active.
    from datetime import date as _d
    d=_d(2026,7,2)
    for c in ('02','03','04','08','12','13','14','15','17'):
        assert s.calcul_cm(27000,129,10,cod=c,zile_episod=10,la_data=d)['diminuare']==0, c
    for c in ('01','06','07','09','51'):
        assert s.calcul_cm(27000,129,10,cod=c,zile_episod=10,la_data=d)['diminuare']==1, c
    assert s.calcul_cm(27000,129,10,cod='01',zile_episod=10,la_data=d,spitalizare=True)['diminuare']==0


def test_maternitate_cod08_100pct_fnuass():
    from datetime import date
    r = s.calcul_cm(30000, 126, 10, cod="08", la_data=date(2026, 6, 1))
    assert r["zile_ang"] == 0 and r["brut_ang"] == Decimal("0.00"), "maternitate 100% FNUASS (D_20=0, spec D112)"
    r01 = s.calcul_cm(30000, 126, 10, cod="01", la_data=date(2026, 6, 1))
    assert r01["zile_ang"] == 5, "cod 01 nu e integral FNUASS - primele 5 zile angajator"
