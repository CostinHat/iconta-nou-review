# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] GARDA: formularul D177 gol NU produce declaratie.

D177 (redirectionarea impozitului pe profit catre entitati nonprofit / unitati de cult) e produsa din
beneficiarii introdusi de contabil in formularul manual (lista, ecran nou, scos din _DOAR_API). Un formular
GOL (niciun beneficiar) e structural invalid la validator (<beneficiar> 1-n). genereaza refuza PRE-XML cu
mesaj de CONTABIL (ce lipseste, in limba lui), NU numele intern al atributului XML (tipB/cuiB/denB/ibanB/
sumaB/contractB/sumaMax/sumaRest/tipPlatitor/totalPlata_A) si NU un XML respins de validator. Geaman cu
core/test_d107_formular.py / test_d307_formular.py.
"""
import pytest
from core import d177
from core.common import Perioada

_PROF = {"cui": "14399840", "den": "T SRL", "adresa": "Str. Testului nr. 1", "telefon": "", "email": ""}

_INTERNE = ("tipPlatitor", "tip_platitor", "sumaMax", "suma_max", "sumaAnt", "suma_ant", "sumaRest",
            "suma_rest", "denB", "cuiB", "tipB", "contractB", "ibanB", "sumaB", "totalPlata_A")

_BENEF_OK = {"tip": "2", "cui": "14399840", "den": "Asociatia Binele",
             "iban": "RO49AAAA1B31007593840000", "contract": "12/2025", "suma": 10000, "acord": "1"}


def _manual(**ov):
    m = {"tip_platitor": 1, "data_inceput": "2025-01-01", "data_sfarsit": "2025-12-31",
         "suma_max": 10000, "suma_ant": 0, "suma_rest": 10000, "beneficiari": [dict(_BENEF_OK)]}
    m.update(ov)
    return m


def _fake_pull(m):
    m.setattr(d177, "pull", lambda conn, schema, per: dict(_PROF))


def _fara_nume_interne(msg):
    for intern in _INTERNE:
        assert intern not in msg, "mesajul expune numele intern %r: %s" % (intern, msg)


def test_d177_formular_gol_refuza():
    """Niciun beneficiar -> ValueError cu mesaj de contabil, nu XML, nu nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        with pytest.raises(ValueError) as e:
            d177.genereaza(None, "x", Perioada(2025, luna=6),
                           {"suma_max": 10000, "suma_ant": 0, "suma_rest": 10000, "beneficiari": []})
    finally:
        m.undo()
    msg = str(e.value)
    assert "beneficiar" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d177_beneficiar_incomplet_refuza():
    """Un beneficiar fara cod fiscal / IBAN / contract -> refuz in limba contabilului, fara nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        rau = _manual(beneficiari=[{"tip": "1", "cui": "", "den": "", "iban": "gresit", "suma": 100, "acord": "1"}])
        with pytest.raises(ValueError) as e:
            d177.genereaza(None, "x", Perioada(2025, luna=6), rau)
    finally:
        m.undo()
    msg = str(e.value)
    assert ("IBAN" in msg or "contract" in msg.lower() or "denumire" in msg.lower()), msg
    _fara_nume_interne(msg)


def test_d177_plafon_depasit_refuza():
    """Suma alocata beneficiarilor > suma ramasa -> refuz prietenos, fara nume interne."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        rau = _manual(suma_rest=5000, beneficiari=[dict(_BENEF_OK, suma=8000)])
        with pytest.raises(ValueError) as e:
            d177.genereaza(None, "x", Perioada(2025, luna=6), rau)
    finally:
        m.undo()
    msg = str(e.value)
    assert "depășește" in msg.lower() and "rămas" in msg.lower(), msg
    _fara_nume_interne(msg)


def test_d177_un_beneficiar_valid_genereaza():
    """Regresie: un beneficiar real -> NU refuza (produce XML cu <beneficiar> si tipB)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m)
        xml, res = d177.genereaza(None, "x", Perioada(2025, luna=6), _manual())
    finally:
        m.undo()
    assert "<beneficiar " in xml and 'tipB="2"' in xml and 'sumaRest="10000"' in xml
    # [R4.1] chiar daca perioada vine cu luna=6 (default dispatch), luna XML = luna din dataSfarsit (12)
    assert 'luna="12"' in xml, xml
    assert res.nr_beneficiari == 1
