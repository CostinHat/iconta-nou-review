# -*- coding: utf-8 -*-
"""GARD D101 (16.08.2026, campanie rețeta D300, pas 6/8) — sponsorizare: limita 0.75% cifra de afaceri.

Creditul de sponsorizare (CF art.25 alin.(4) lit.i, cod_fiscal l.1975) = limita DUBLA:
min(0.75% x cifra de afaceri; 20% x impozit pe profit). DUK verifica DOAR partea de 20% (V5:
rd.43 <= 20% x (rd.41-rd.42)). Limita 0.75% cifra de afaceri LIPSEA complet (grep 0.75 = 0) -> o
firma cu impozit mare dar cifra mica putea deduce peste 0.75% CA fara ca app sau DUK s-o opreasca
(Costin: 'limita DUBLA').

FIX: gard V5-bis in _erori_valori_p: P43 <= 0.75% x cifra_afaceri. CA = SUM(cont 70x) = cifra de
afaceri neta (>= CA reala, care scade reducerile 709) -> gard SOLID (fara fals-pozitive). Activ doar
cand CA e cunoscuta din balanta (calea pull); apelantii puri fara CA (None) -> gard sarit.

Aserturi ASCII.
"""
from core.d101 import _erori_valori_p, calcul_d101


def _g(d=None):
    d = d or {}
    return lambda k: int(d.get(k, 0))


def _P(P43):
    return {"P41": 10000, "P42": 0, "P43": P43, "P422": 0, "P423": 0}


def test_v5bis_sponsorizare_peste_075_ca_eroare():
    """P43=1000 > 0.75% x CA(100000)=750, dar sub 20% x impozit (2000) -> V5-bis prinde ce DUK V5 rateaza."""
    erori = _erori_valori_p(_g(), _P(1000), cifra_afaceri=100000)
    assert any("V5-bis" in e for e in erori), "V5-bis trebuie sa prinda P43 > 0.75%% CA: %r" % erori
    assert not any("DUK regula V5:" in e for e in erori), "V5 (20%%) NU trebuie sa se declanseze aici: %r" % erori


def test_v5bis_sub_075_ca_ok():
    """CONTROL: P43=700 < 0.75% x CA(100000)=750 -> niciun V5-bis."""
    erori = _erori_valori_p(_g(), _P(700), cifra_afaceri=100000)
    assert not any("V5-bis" in e for e in erori), erori


def test_v5bis_fara_ca_sarit_backward_compat():
    """CONTROL backward-compat: cifra_afaceri=None (apelant pur, fara balanta) -> gardul V5-bis e SARIT."""
    erori = _erori_valori_p(_g(), _P(1000), cifra_afaceri=None)
    assert not any("V5-bis" in e for e in erori), erori


def test_v5bis_e_limita_binding_nu_20pct():
    """Impozit mare (20% permite mult) DAR cifra mica -> V5-bis e limita care musca (limita DUBLA:
    min(0.75% CA, 20% impozit); cand CA e mica, 0.75% CA < 20% impozit)."""
    # P41=100000 -> 20%*(100000)=20000 permite P43 pana la 20000; dar CA=100000 -> 0.75%=750 musca la 750.
    erori = _erori_valori_p(_g(), {"P41": 100000, "P42": 0, "P43": 5000, "P422": 0, "P423": 0},
                            cifra_afaceri=100000)
    assert any("V5-bis" in e for e in erori) and not any("DUK regula V5:" in e for e in erori), erori


def test_calcul_d101_ridica_pe_v5bis():
    """INTEGRARE: calcul_d101 cu P431 peste 0.75% CA (dar impozit mare) -> ridica ValueError cu V5-bis."""
    prof = {"cui": "14399840", "nume": "X"}
    intrari = {"P1": 1000000, "P431": 1000}   # venituri 1M -> impozit mare (V5 20% permite); CA mica -> V5-bis musca
    import pytest
    with pytest.raises(ValueError) as ei:
        calcul_d101(prof, 2025, intrari, cifra_afaceri=100000)
    assert "V5-bis" in str(ei.value), str(ei.value)


def test_calcul_d101_fara_ca_nu_ridica_v5bis():
    """CONTROL: acelasi P431 dar fara cifra_afaceri -> calcul_d101 NU ridica V5-bis (backward-compat)."""
    prof = {"cui": "14399840", "nume": "X"}
    # fara cifra_afaceri: doar V5 (20%) conteaza; P431=1000 << 20% din impozitul pe 1M -> trece
    res = calcul_d101(prof, 2025, {"P1": 1000000, "P431": 1000})
    assert res is not None
