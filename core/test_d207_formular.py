# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] GARDA: formularul D207 gol NU produce declaratie.

D207 (informativa impozit retinut la sursa - beneficiari nerezidenti) e produsa din beneficiarii introdusi
de contabil in formularul manual (lista, ecran nou, scos din _DOAR_API). Un formular GOL (niciun beneficiar)
e structural invalid la DUK (<benef> 1-n). genereaza refuza PRE-XML cu mesaj de CONTABIL (ce lipseste, in
limba lui), NU numele intern al campului/atributului XML (den1/Stat_R/cifR/cifS/baza1/imp1/imps1/Act_N/
tip_venit1/Tbaza/Tscutit/totalPlata_A) si NU un XML respins de validator.
Geaman cu core/test_d107_formular.py / test_d177_formular.py / test_d307_formular.py.

In plus verifica ca d207 NU mai e in _DOAR_API (are formular in UI -> apare in selectorul de tipuri).
"""
import pytest
from core import d207
from core.common import Perioada

_PROF = {"den": "T SRL", "cui": "14399840", "adresa": "Str. Testului nr. 1",
         "declarant_nume": "Ion", "declarant_prenume": "Pop", "declarant_functie": "administrator",
         "telefon": "", "email": ""}

# Atribute XML / campuri interne care NU au voie sa apara in mesajele de eroare (numele-contabil
# "beneficiar"/"nerezident"/"stat de rezidenta"/"act normativ"/"impozit retinut" sunt PERMISE - limba actului).
_INTERNE = ("den1", "Stat_R", "cifR", "cifS", "baza1", "imp1", "imps1", "Act_N", "tip_venit",
            "tip_venit1", "Tbaza", "Tscutit", "Timp", "Timps", "nrben", "totalPlata_A",
            "declarant_nume", "declarant_prenume", "declarant_functie")


def _fake_pull(m):
    m.setattr(d207, "pull", lambda conn, schema, per: dict(_PROF))


def _fara_nume_interne(msg):
    for intern in _INTERNE:
        assert intern not in msg, "mesajul expune numele intern %r: %s" % (intern, msg)


def test_d207_nu_e_doar_api():
    """d207 are formular manual in UI -> nu mai e ascuns din selectorul de tipuri."""
    from core import declaratii_api
    assert "d207" not in declaratii_api._DOAR_API


def test_d207_formular_gol_refuza():
    """Niciun beneficiar -> ValueError cu mesaj de contabil, nu XML, nu nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d207.genereaza(None, "x", Perioada(2025, luna=12), {"beneficiari": []})
    finally:
        m.undo()
    msg = str(e.value)
    assert "beneficiar" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d207_beneficiar_incomplet_refuza():
    """Un beneficiar fara denumire / stat / cod fiscal -> refuz in limba contabilului, fara nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d207.genereaza(None, "x", Perioada(2025, luna=12),
                           {"beneficiari": [{"tip_venit": "01", "den": "", "stat": "",
                                             "cif_ro": "", "cif_strain": "", "act_n": "1", "baza": 1000}]})
    finally:
        m.undo()
    msg = str(e.value)
    assert ("denumire" in msg.lower() or "stat" in msg.lower() or "identificare" in msg.lower()), msg
    _fara_nume_interne(msg)


def test_d207_scutit_cu_impozit_refuza():
    """Tip scutit (12-21) cu impozit retinut > 0 -> refuz prietenos (venit scutit -> impozit 0)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d207.genereaza(None, "x", Perioada(2025, luna=12),
                           {"beneficiari": [{"tip_venit": "12", "den": "Bank AG", "stat": "AT",
                                             "cif_strain": "AT9", "act_n": "1", "baza": 5000, "imp": 250}]})
    finally:
        m.undo()
    msg = str(e.value)
    assert "scutit" in msg.lower() and "0" in msg, msg
    _fara_nume_interne(msg)


def test_d207_un_beneficiar_valid_genereaza():
    """Regresie: un beneficiar real -> NU refuza (produce XML cu <benef> si <sect_II>)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        xml, res = d207.genereaza(None, "x", Perioada(2025, luna=12),
                                  {"beneficiari": [{"tip_venit": "01", "den": "Nonresident Ltd", "stat": "DE",
                                                    "cif_strain": "DE123", "act_n": "1",
                                                    "baza": 10000, "imp": 800, "imp_suportat": 0}]})
    finally:
        m.undo()
    assert "<benef " in xml and "<sect_II " in xml and 'baza1="10000"' in xml
    assert res.nr_beneficiari == 1
