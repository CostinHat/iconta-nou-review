# -*- coding: utf-8 -*-
"""TURA 3: genereaza() gardeaza doar LUNA (1..12), nu ANUL. D301 (formularul 301) se depune din
2013; un an < 2013 trecea nevalidat pana la DUK. FIX: gard an >= 2013 -> ValueError.

Pe HEAD (8b74ccb): niciun gard pe an -> genereaza() reuseste pentru an=2012 -> PICA.
"""
import pytest
from core import d301
from core.common import Perioada

PROF = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR", "nume": "PROBA SRL", "cui": "14399840", "banca": "BCR", "iban": "RO49AAAA1B31007593840000"}


def _op():
    return {"tip": 1, "nr_doc": "F1", "data_doc": "10.06.2012", "val_valuta": 1000,
            "tip_valuta": "EUR", "curs": 4.5, "tva": 210}


def test_an_sub_2013_blocat(monkeypatch):
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (PROF, [_op()]))
    with pytest.raises(ValueError) as ei:
        d301.genereaza(None, "tenant_014", Perioada(2012, luna=6))
    assert "an invalid" in str(ei.value) and "2013" in str(ei.value), str(ei.value)


def test_an_2013_trece(monkeypatch):
    op = dict(_op(), data_doc="10.06.2013")
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (PROF, [op]))
    xml, res = d301.genereaza(None, "tenant_014", Perioada(2013, luna=6))
    assert "<declaratie301" in xml
