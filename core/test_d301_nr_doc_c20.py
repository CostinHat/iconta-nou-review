# -*- coding: utf-8 -*-
"""TURA 3 / T6: nr_doc > C(20) passthrough NETRUNCHIAT nicaieri (leak pur). DUK NU impune lungimea,
deci un numar de document supra-lung ajungea in XML nedetectat. FIX: genereaza() blocheaza cu motiv
exact care numeste operatiunea si lungimea (nu se emite netrunchiat, nu se trunchiaza tacit).

Pe HEAD (8b74ccb): niciun gard -> nr_doc de 30 caractere ajunge NETRUNCHIAT in XML -> PICA.
"""
import pytest
from core import d301
from core.common import Perioada

PROF = {"nume": "PROBA SRL", "cui": "14399840", "banca": "BCR", "iban": "RO49AAAA1B31007593840000"}


def _op(nr_doc):
    return {"tip": 1, "nr_doc": nr_doc, "data_doc": "10.06.2026", "val_valuta": 1000,
            "tip_valuta": "EUR", "curs": 4.97, "tva": 210}


def test_nr_doc_peste_20_blocat(monkeypatch):
    lung = "F" * 30
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (PROF, [_op(lung)]))
    with pytest.raises(ValueError) as ei:
        d301.genereaza(None, "tenant_014", Perioada(2026, luna=8))
    assert "C(20)" in str(ei.value) and "30 caractere" in str(ei.value), str(ei.value)


def test_nr_doc_20_exact_trece(monkeypatch):
    nr = "F" * 20
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (PROF, [_op(nr)]))
    xml, res = d301.genereaza(None, "tenant_014", Perioada(2026, luna=8))
    assert nr in xml   # C(20) exact e permis, emis intact (nu trunchiat)
