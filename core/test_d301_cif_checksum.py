# -*- coding: utf-8 -*-
"""TURA 3 / T1: CIF checksum + lungime NICIODATA pre-validat de app. erori_generare verifica doar
non-gol -> un CIF cu cifra de control gresita / supra-lung era emis TACIT (doar DUK il prindea,
criptic). FIX: erori_generare foloseste validatorul partajat core.identitate.valideaza_cui.

Pe HEAD (8b74ccb): erori_generare accepta orice CIF non-gol -> genereaza() reuseste -> PICA.
Dupa fix: ValueError cu motivul exact (cifra de control / lungime).
"""
import pytest
from core import d301
from core.common import Perioada

BASE = {"nume": "PROBA SRL", "banca": "BCR", "iban": "RO49AAAA1B31007593840000"}


def _op():
    return {"tip": 1, "nr_doc": "F1", "data_doc": "10.06.2026", "val_valuta": 1000,
            "tip_valuta": "EUR", "curs": 4.97, "tva": 210}


def _gen(monkeypatch, cui):
    prof = dict(BASE, cui=cui)
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (prof, [_op()]))
    return d301.genereaza(None, "tenant_014", Perioada(2026, luna=8))


def test_cif_checksum_gresit_blocat(monkeypatch):
    with pytest.raises(ValueError) as ei:
        _gen(monkeypatch, "12345678")   # cifra de control gresita
    assert "cifra de control" in str(ei.value), str(ei.value)


def test_cif_supra_lung_blocat(monkeypatch):
    with pytest.raises(ValueError) as ei:
        _gen(monkeypatch, "12345678901234")   # 14 cifre, peste 10/C(13)
    assert "lungime" in str(ei.value) or "C(13)" in str(ei.value), str(ei.value)


def test_cif_valid_trece(monkeypatch):
    xml, res = _gen(monkeypatch, "14399840")   # checksum OK
    assert "<declaratie301" in xml
