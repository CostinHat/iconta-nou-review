# -*- coding: utf-8 -*-
"""Compensari cu tertii (core/compensare.py) - motor pur, ancorat la sursa in corpus.

TEMEI verificat verbatim (anaf_surse/): Cod civil (Legea 287/2009) art.1616 (min), art.1617 (certe/lichide/
exigibile), art.1618 (excluderi) + OMFP 1802/2014 pct.56 alin.(3) (nota 401=4111 dupa contabilizare; valoarea
bruta in note explicative). HG 685/1999 e ABROGAT (HG 773/2019, nu e in corpus) -> pragul nu se hardcodeaza.
"""
import os
from decimal import Decimal

import pytest

from core import compensare as c


def test_suma_compensabila_min_art1616():
    """Cod civil art.1616: se sting pana la concurenta celei mai mici."""
    assert c.suma_compensabila(1000, 300) == Decimal("300.00")
    assert c.suma_compensabila(300, 1000) == Decimal("300.00")
    assert c.suma_compensabila(500, 500) == Decimal("500.00")


def test_nota_401_egal_4111_si_echilibrata():
    n = c.nota_compensare(1000, 300)
    assert n["linii"] == [("401", "4111", Decimal("300.00"))]   # 401 = 4111
    debit = sum(s for _dc, _cr, s in n["linii"])
    credit = sum(s for _dc, _cr, s in n["linii"])
    assert debit == credit == Decimal("300.00")                 # nota echilibrata
    assert n["compensat"] == Decimal("300.00")


def test_valori_brute_si_resturi_pastrate_omfp_pct56():
    """OMFP 1802 pct.56 alin.3: valoarea bruta se prezinta in note -> nota pastreaza brutul + resturile."""
    n = c.nota_compensare(1000, 300)
    assert n["brut_creanta"] == Decimal("1000.00")
    assert n["brut_datorie"] == Decimal("300.00")
    assert n["rest_creanta"] == Decimal("700.00")   # creanta ramasa dupa compensare
    assert n["rest_datorie"] == Decimal("0.00")     # datoria stinsa integral


def test_fara_una_din_parti_nu_exista_compensare():
    """Compensarea cere AMBELE (creanta si datorie) fata de acelasi partener."""
    with pytest.raises(ValueError):
        c.nota_compensare(1000, 0)
    with pytest.raises(ValueError):
        c.nota_compensare(0, 500)


def test_valori_negative_refuzate():
    with pytest.raises(ValueError):
        c.suma_compensabila(-1, 100)


def test_propune_doar_parteneri_cu_ambele_solduri():
    parteneri = [
        {"cui": "RO1", "denumire": "ALFA", "creanta": 1000, "datorie": 300},   # compensabil 300
        {"cui": "RO2", "denumire": "BETA", "creanta": 0, "datorie": 500},      # doar datorie -> exclus
        {"cui": "RO3", "denumire": "GAMA", "creanta": 800, "datorie": 0},      # doar creanta -> exclus
        {"cui": "RO4", "denumire": "DELTA", "creanta": 200, "datorie": 800},   # compensabil 200
    ]
    rez = c.propune_compensari(parteneri)
    assert [r["cui"] for r in rez] == ["RO1", "RO4"]
    assert rez[0]["compensat"] == Decimal("300.00")
    assert rez[1]["compensat"] == Decimal("200.00")


def test_prag_necunoscut_e_none_nu_false():
    """HG 773/2019 (pragul curent) nu e in corpus -> fara prag confirmat, semnalul e None (necunoscut),
    NU False (nu se afirma ca nu e nevoie de sistemul electronic)."""
    assert c.necesita_sistem_electronic(50000) is None
    assert c.necesita_sistem_electronic(50000, prag=10000) is True
    assert c.necesita_sistem_electronic(5000, prag=10000) is False


def test_rotunjire_half_up():
    assert c.suma_compensabila("100.005", 999) == Decimal("100.01")


def test_temei_are_sursa_in_corpus():
    """Regula verificarii la sursa: actele citate de motor EXISTA in corpus."""
    surse = "anaf_surse"
    for f in ("cod_civil_287_2009_art_1616_1623_compensare.txt", "omfp_1802_2014.txt",
              "oug_77_1999_masuri_prevenire_incapacitate_plata.txt"):
        assert os.path.exists(os.path.join(surse, f)), "lipseste din corpus: %s" % f
