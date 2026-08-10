# -*- coding: utf-8 -*-
"""TURA 3 / T1: erori_generare verifica pana acum doar NON-GOL pentru cui/caen/pro_rata.
Un CUI cu cifra de control gresita, un CAEN cu forma gresita (nu C(4)) sau un pro_rata in
afara [0,100] erau emise TACIT si prinse abia de DUK (OE-2/3/5/6). Aici probam ca sunt
prinse PRE-DUK, cu motiv exact, in erori_generare (poarta din genereaza).

Pe HEAD (8b74ccb): erori_generare accepta bad-checksum cui / caen '62' / pro_rata=150 ->
listele sunt goale -> testele PICA. Dupa T1 -> TREC.
"""
import pytest
from core import d300
from core.common import Perioada

BAZA = {"cui": "14399840", "nume": "PROBA SRL", "caen": "6202",
        "banca": "ING Bank", "iban": "RO49AAAA1B31007593840000"}


def test_profil_valid_ramane_gol():
    assert d300.erori_generare(dict(BAZA)) == []


def test_cui_cifra_de_control_gresita_e_prinsa():
    e = d300.erori_generare(dict(BAZA, cui="14399841"))   # ultima cifra alterata
    assert any("CUI" in m and "control" in m for m in e), e


def test_caen_forma_gresita_e_prinsa():
    assert any("CAEN" in m for m in d300.erori_generare(dict(BAZA, caen="62")))       # 2 cifre
    assert any("CAEN" in m for m in d300.erori_generare(dict(BAZA, caen="620200")))   # 6 cifre


def test_pro_rata_in_afara_intervalului_e_prinsa():
    assert any("pro_rata" in m for m in d300.erori_generare(dict(BAZA, pro_rata=150)))
    assert any("pro_rata" in m for m in d300.erori_generare(dict(BAZA, pro_rata=-1)))


def test_pro_rata_valid_sau_absent_trece():
    assert d300.erori_generare(dict(BAZA, pro_rata=50)) == []
    assert d300.erori_generare(dict(BAZA, pro_rata="")) == []      # gol = absent = 100%
    assert d300.erori_generare(dict(BAZA)) == []                    # absent


def test_genereaza_blocheaza_cui_invalid_pre_duk(monkeypatch):
    prof = dict(BAZA, cui="14399841")
    monkeypatch.setattr(d300, "pull", lambda conn, schema, perioada: (prof, []))
    with pytest.raises(ValueError) as ei:
        d300.genereaza(None, "tenant_013", Perioada(2026, luna=8))
    assert "CUI" in str(ei.value), str(ei.value)
