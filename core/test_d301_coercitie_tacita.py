# -*- coding: utf-8 -*-
"""TURA 3 / T3: coercitie TACITA enum-necunoscut -> default. calcul_d301 face `int(tip or 1)`
(tip=0/necunoscut -> sectiunea 1) si `(tip_valuta or 'EUR')` (valuta lipsa -> EUR). XML iesea
DUK-valid dar RAPORTA date GRESITE la ANAF, fara niciun mesaj. FIX: pe calea de GENERARE valoarea
coercita din gunoi iese la suprafata (ValueError cu motiv exact), nu devine tacit un default.

Documenteaza intai coercitia veche (pe functia PURA calcul_d301, neschimbata), apoi probeaza ca
genereaza() o BLOCHEAZA acum. Pe HEAD (8b74ccb) genereaza() emitea tacit -> testele de blocare PICA.
"""
import pytest
from core import d301
from core.common import Perioada

PROF = {"nume": "PROBA SRL", "cui": "14399840", "banca": "BCR", "iban": "RO49AAAA1B31007593840000"}


def _op(**kw):
    o = {"tip": 1, "nr_doc": "F1", "data_doc": "10.06.2026", "val_valuta": 1000,
         "tip_valuta": "EUR", "curs": 4.97, "tva": 210}
    o.update(kw)
    return o


def test_coercitia_pura_inca_exista_documentata():
    """calcul_d301 (PUR) inca coercita - de-aceea era periculos: tip=0->1, valuta lipsa->EUR.
    Nu schimbam functia pura; gardul e pe calea de generare (vezi testele de mai jos)."""
    res = d301.calcul_d301(PROF, Perioada(2026, luna=8), [_op(tip=0, tip_valuta="")])
    assert res.operatiuni[0].tip == 1          # tip 0 a devenit tacit 1
    assert res.operatiuni[0].tip_valuta == "EUR"  # valuta lipsa a devenit tacit EUR


def test_tip_zero_nu_devine_tacit_sectiunea_1(monkeypatch):
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (PROF, [_op(tip=0)]))
    with pytest.raises(ValueError) as ei:
        d301.genereaza(None, "tenant_014", Perioada(2026, luna=8))
    assert "nu se reclasifica tacit in sectiunea 1" in str(ei.value), str(ei.value)


def test_valuta_lipsa_nu_devine_tacit_eur(monkeypatch):
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (PROF, [_op(tip_valuta="")]))
    with pytest.raises(ValueError) as ei:
        d301.genereaza(None, "tenant_014", Perioada(2026, luna=8))
    assert "nu se completeaza tacit EUR" in str(ei.value), str(ei.value)
