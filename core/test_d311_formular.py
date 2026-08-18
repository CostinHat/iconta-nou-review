# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] GARDA: formularul D311 gol NU produce declaratie.

D311 (TVA datorata dupa anularea codului de TVA) e produsa din situatiile introduse de contabil in
formularul manual (ecran nou, scos din _DOAR_API). Un formular GOL (fara data anularii, fara motiv
bifat, cu toate sumele 0) e structural invalid. genereaza refuza PRE-XML cu mesaj de CONTABIL (ce
lipseste, in limba lui), NU numele intern al campului (Data_A/d_anul1/OB_51) si NU un XML respins de
validator. Geaman cu core/test_d710_formular.py.
"""
import pytest
from core import d311
from core.common import Perioada

_PROF = {"den": "T SRL", "nume": "T SRL", "cui": "14399840", "adresa": "Str. Testului nr. 1",
         "declarant_nume": "Ion", "declarant_prenume": "Pop", "declarant_functie": "administrator",
         "telefon": "", "email": ""}

# numele interne XSD care NU au voie sa apara in textul aratat contabilului
_INTERNE = ("Data_A", "d_anul1", "d_anul2", "OB_11", "OB_12", "OB_21", "OB_22",
            "OB_41", "OB_42", "OB_51", "OB_52", "manual", "totalPlata_A")


def _fake_pull(m):
    m.setattr(d311, "pull", lambda conn, schema, per: dict(_PROF))


def _fara_nume_interne(msg):
    for intern in _INTERNE:
        assert intern not in msg, "mesajul expune numele intern %r: %s" % (intern, msg)


def test_d311_formular_gol_refuza():
    """Manual GOL -> ValueError cu mesaj de contabil, nu XML, nu nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d311.genereaza(None, "x", Perioada(2026, luna=6), {})
    finally:
        m.undo()
    msg = str(e.value)
    assert "data anulării" in msg.lower(), msg          # lipsa data anularii, in limba contabilului
    assert "motivul anulării" in msg.lower(), msg       # lipsa bifei motiv
    _fara_nume_interne(msg)


def test_d311_fara_sume_refuza():
    """Data + motiv completate, dar toate sumele 0 -> refuz 'nu se depune pe zero', fara nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d311.genereaza(None, "x", Perioada(2026, luna=6),
                           {"schema": 1, "Data_A": "2026-03-15", "d_anul1": 1, "d_anul2": 0})
    finally:
        m.undo()
    msg = str(e.value)
    assert "zero" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d311_completat_genereaza():
    """Regresie: data + motiv + o suma reala -> NU refuza (produce XML)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        xml, res = d311.genereaza(None, "x", Perioada(2026, luna=6),
                                  {"schema": 1, "Data_A": "2026-03-15", "d_anul1": 1, "d_anul2": 0,
                                   "OB_11": 1000, "OB_12": 210})
    finally:
        m.undo()
    assert 'OB_51="1000"' in xml and 'OB_52="210"' in xml
