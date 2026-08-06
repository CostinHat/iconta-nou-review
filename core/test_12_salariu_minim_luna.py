# -*- coding: utf-8 -*-
"""GARD #12: CF art.77 alin.(3) teza finala — cand in aceeasi luna se aplica mai multe valori ale
salariului minim brut pe tara, se ia CEA MAI MICA. `salariu_minim_luna()` implementeaza regula;
`cota()` intoarce valoarea la data (nu regula). Verificat verbatim la MO (anaf_surse/cod_fiscal)."""
from datetime import date
from decimal import Decimal

from core import common


def test_salariu_minim_luna_ia_cea_mai_mica(monkeypatch):
    """O luna cu DOUA valori de salariu minim -> se ia cea mai mica (art.77 alin.3)."""
    T = common.Temei
    entries = [
        (date(2099, 5, 1), Decimal("5000"), T(text="sm-vechi", data_in="2099-05-01", data_out="2099-05-14")),
        (date(2099, 5, 15), Decimal("5200"), T(text="sm-nou", data_in="2099-05-15")),
    ]
    monkeypatch.setitem(common.COTE, "salariu_minim", entries)
    val, _ = common.salariu_minim_luna(date(2099, 5, 20))
    assert val == Decimal("5000"), "luna cu doua valori -> cea mai mica (art.77 alin.3)"
    val6, _ = common.salariu_minim_luna(date(2099, 6, 10))
    assert val6 == Decimal("5200"), "luna cu o singura valoare -> valoarea aia"


def test_salariu_minim_luna_no_op_pe_date_reale():
    """Pe datele reale (schimbari la granita de luna) = identic cu cota() -> zero regresie D112."""
    v1, _ = common.salariu_minim_luna(date(2026, 7, 15))
    c1, _ = common.cota("salariu_minim", date(2026, 7, 1))
    assert v1 == c1 == Decimal("4325")
    v2, _ = common.salariu_minim_luna(date(2025, 6, 10))
    assert v2 == Decimal("4050")
