# -*- coding: utf-8 -*-
"""TURA 3 / T2: valideaza(res) era COD MORT. genereaza() chema doar erori_generare(prof), deci
verificarile prietenoase pe operatiuni (nr_doc/data_doc gol, tip/valuta out-of-nomenclator)
NU ajungeau la contabil - primea eroarea BRUTA a validatorului la upload ("atribut vid nepermis" /
"nu se afla in lista"). Aici probam ca genereaza() cableaza verificarile: blocantele -> ValueError
cu motiv EXACT pre-DUK.

Pe HEAD (8b74ccb): _blocante_pre_duk NU exista, iar genereaza() coercita/emitea tacit (nu ridica
ValueError cu motivul) -> testele PICA. Dupa cablare -> TREC.
"""
import pytest
from core import d301
from core.common import Perioada

VALID_PROF = {"nume": "PROBA SRL", "cui": "14399840", "banca": "BCR",
              "iban": "RO49AAAA1B31007593840000", "adresa": "Str 1", "oras": "Buc", "judet": "B"}


def _op(**kw):
    o = {"tip": 1, "nr_doc": "F1", "data_doc": "10.06.2026", "val_valuta": 1000,
         "tip_valuta": "EUR", "curs": 4.97, "tva": 210}
    o.update(kw)
    return o


def _gen(monkeypatch, ops, prof=None, per=None):
    prof = prof or VALID_PROF
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (prof, ops))
    return d301.genereaza(None, "tenant_014", per or Perioada(2026, luna=8))


def test_helperul_de_rutare_exista():
    assert hasattr(d301, "_blocante_pre_duk"), "lipsește _blocante_pre_duk (T2 necablat)"


def test_nr_doc_gol_blocheaza_cu_motiv_exact(monkeypatch):
    with pytest.raises(ValueError) as ei:
        _gen(monkeypatch, [_op(nr_doc="")])
    assert "fără număr document" in str(ei.value), str(ei.value)


def test_data_doc_gol_blocheaza_cu_motiv_exact(monkeypatch):
    with pytest.raises(ValueError) as ei:
        _gen(monkeypatch, [_op(data_doc="")])
    assert "fără data document" in str(ei.value), str(ei.value)


def test_tip_out_of_nomenclator_blocheaza(monkeypatch):
    with pytest.raises(ValueError) as ei:
        _gen(monkeypatch, [_op(tip=9)])
    assert "în afară nomenclatorului" in str(ei.value), str(ei.value)


def test_valuta_out_of_nomenclator_blocheaza(monkeypatch):
    with pytest.raises(ValueError) as ei:
        _gen(monkeypatch, [_op(tip_valuta="ZZZ")])
    assert "neacceptata" in str(ei.value), str(ei.value)


def test_calea_valida_nu_e_rupta_de_cablare(monkeypatch):
    """Wiring valideaza() nu trebuie sa blocheze o operatiune complet valida."""
    xml, res = _gen(monkeypatch, [_op()])
    assert "<declaratie301" in xml
    assert res.operatiuni and res.operatiuni[0].nr_doc == "F1"
