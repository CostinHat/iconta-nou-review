# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] GARDA: formularul D307 gol NU produce declaratie.

D307 (ajustare/corectie/regularizare TVA) e produsa din operatiunile introduse de contabil in formularul
manual (lista, ecran nou, scos din _DOAR_API). Un formular GOL (nicio operatiune) e structural invalid la
DUK (<operatie> 1-n). genereaza refuza PRE-XML cu mesaj de CONTABIL (ce lipseste, in limba lui), NU numele
intern al campului (operatiuni/denO/codO/d_anulare) si NU un XML respins de validator. Geaman cu
core/test_d311_formular.py / core/test_d710_formular.py.
"""
import pytest
from core import d307
from core.common import Perioada

_PROF = {"den": "T SRL", "cui": "14399840", "adresa": "Str. Testului nr. 1",
         "declarant_nume": "Ion", "declarant_prenume": "Pop", "declarant_functie": "administrator",
         "telefon": "", "email": ""}

_INTERNE = ("operatiuni", "denO", "codO", "d_anulare", "declarant_nume", "declarant_prenume",
            "tvaA", "tvaL", "tvaC", "totalPlata_A", "manual")


def _fake_pull(m):
    m.setattr(d307, "pull", lambda conn, schema, per: dict(_PROF))


def _fara_nume_interne(msg):
    for intern in _INTERNE:
        assert intern not in msg, "mesajul expune numele intern %r: %s" % (intern, msg)


def test_d307_formular_gol_refuza():
    """Nicio operatiune -> ValueError cu mesaj de contabil, nu XML, nu nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d307.genereaza(None, "x", Perioada(2026, luna=6), {"operatiuni": []})
    finally:
        m.undo()
    msg = str(e.value)
    assert "operațiune" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d307_operatiune_incompleta_refuza():
    """O operatiune fara tip / denumire / cod -> refuz in limba contabilului, fara nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d307.genereaza(None, "x", Perioada(2026, luna=6),
                           {"operatiuni": [{"tip": "", "cod": "", "den": "", "tva": 100}]})
    finally:
        m.undo()
    msg = str(e.value)
    assert "tip" in msg.lower() or "operator" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d307_o_operatiune_valida_genereaza():
    """Regresie: o operatiune reala (transfer active) -> NU refuza (produce XML cu <operatie>)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        xml, res = d307.genereaza(None, "x", Perioada(2026, luna=6),
                                  {"operatiuni": [{"tip": "A", "cod": "14399840", "den": "Cedent SRL", "tva": 5000}]})
    finally:
        m.undo()
    assert '<operatie ' in xml and 'tvaA="5000"' in xml
