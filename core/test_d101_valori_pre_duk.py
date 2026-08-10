# -*- coding: utf-8 -*-
"""GARD (TURA 3, 10.08.2026): D101 surfaceaza PRE-DUK, cu motiv EXACT, valorile fiscale invalide
ale contabilului (chei `manual`): non-negativitate (P36<0), rand parinte 'din care' >= suma
sub-randurilor (P8 < P081..), si plafoanele V1-V7 (P421<=P41, P43<=20%*(P41-P42)). Pe HEAD toate
se emit TACIT -> DUK Vn/Rn brut la depunere. Fara DB (profil sintetic + calcul_d101)."""
import pytest
from core import d101

_PROF = {"cui": "19", "nume": "ALFA SRL", "adresa": "Str. Test 1", "caen": "6201"}
_BASE = {"P1": 200000, "P2": 100000, "P4": 0, "P5": 0}   # profit 100000 -> P41 ~ 16000 > 0


def _gen(**manual):
    return d101.calcul_d101(_PROF, 2026, dict(_BASE, **manual))


def test_p36_negativ_raise():
    with pytest.raises(ValueError, match=r"P36 = -5000 < 0"):
        _gen(P36=-5000)


def test_p8_sub_suma_subrandurilor_raise():
    with pytest.raises(ValueError, match="P8.*suma sub-randurilor"):
        _gen(P8=10, P081=100000)


def test_v2_p421_peste_p41_raise():
    with pytest.raises(ValueError, match="V2: P421<=P41"):
        _gen(P421=999999)


def test_v5_p43_peste_plafon_raise():
    with pytest.raises(ValueError, match="V5: P43<=20"):
        _gen(P431=50000)


def test_valori_valide_nu_raise():
    r = _gen(P36=5000, P421=1000, P8=100, P081=50)
    assert r.total_plata_a is not None
