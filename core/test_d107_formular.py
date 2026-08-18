# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] GARDA: formularul D107 gol NU produce declaratie.

D107 (informativa sponsorizari/mecenat/burse) e produsa din beneficiarii introdusi de contabil in formularul
manual (lista, ecran nou, scos din _DOAR_API). Un formular GOL (niciun beneficiar) e structural invalid la
DUK (<entit> 1-n). genereaza refuza PRE-XML cu mesaj de CONTABIL (ce lipseste, in limba lui), NU numele
intern al campului/atributului XML (denE/cifE/adrE/Val1/Val2/Val3/Val2_NI/entit1/cod_oblig/totalPlata_A) si
NU un XML respins de validator. Geaman cu core/test_d307_formular.py / test_d311_formular.py / test_d710_formular.py.
"""
import pytest
from core import d107
from core.common import Perioada

_PROF = {"den": "T SRL", "cui": "14399840", "adresa": "Str. Testului nr. 1", "regim_fiscal": "micro",
         "declarant_nume": "Ion", "declarant_prenume": "Pop", "declarant_functie": "administrator",
         "telefon": "", "email": ""}

# Atribute XML / campuri interne care NU au voie sa apara in mesajele de eroare (numele-contabil
# "beneficiar"/"neindividualizat"/"suma reportata/dedusa/acordata" sunt PERMISE - sunt limba actului).
_INTERNE = ("denE", "cifE", "adrE", "denE_NI", "cifE_NI", "adrE_NI", "entit1", "Val1", "Val2", "Val3",
            "Val2_NI", "Val3_NI", "TVal1", "TVal2", "TVal3", "totalPlata_A", "cod_oblig", "cod_bug",
            "d_PM", "denS", "declarant_nume", "declarant_prenume")


def _fake_pull(m):
    m.setattr(d107, "pull", lambda conn, schema, per: dict(_PROF))


def _fara_nume_interne(msg):
    for intern in _INTERNE:
        assert intern not in msg, "mesajul expune numele intern %r: %s" % (intern, msg)


def test_d107_formular_gol_refuza():
    """Niciun beneficiar -> ValueError cu mesaj de contabil, nu XML, nu nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d107.genereaza(None, "x", Perioada(2026), {"beneficiari": []})
    finally:
        m.undo()
    msg = str(e.value)
    assert "beneficiar" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d107_beneficiar_incomplet_refuza():
    """Un beneficiar fara denumire / cod fiscal / adresa -> refuz in limba contabilului, fara nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d107.genereaza(None, "x", Perioada(2026),
                           {"beneficiari": [{"den": "", "cif": "", "adresa": "", "val1": 100}]})
    finally:
        m.undo()
    msg = str(e.value)
    assert "denumire" in msg.lower() or "identificare" in msg.lower() or "adresa" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d107_neindividualizat_fara_lista_refuza():
    """Suma reportata neindividualizati > 0 dar fara lista -> refuz prietenos (Anexa entit1 obligatorie)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d107.genereaza(None, "x", Perioada(2026),
                           {"beneficiari": [{"den": "Scoala X", "cif": "4221306", "adresa": "Str 2", "val1": 500}],
                            "val2_ni": 300, "neindividualizati": []})
    finally:
        m.undo()
    msg = str(e.value)
    assert "neindividualiza" in msg.lower() and "reportat" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d107_un_beneficiar_valid_genereaza():
    """Regresie: un beneficiar real -> NU refuza (produce XML cu <entit> si Val1)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        xml, res = d107.genereaza(None, "x", Perioada(2026),
                                  {"beneficiari": [{"den": "Scoala X", "cif": "4221306",
                                                    "adresa": "Str 2", "val1": 5000, "val2": 0, "val3": 5000}]})
    finally:
        m.undo()
    assert "<entit " in xml and 'Val1="5000"' in xml and 'TVal1="5000"' in xml
    assert res.nr_beneficiari == 1
