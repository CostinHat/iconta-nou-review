# -*- coding: utf-8 -*-
"""GARD TURA 3 — D710 C5: cod_oblig 131/132 cer Data_I (data incheierii exercitiului financiar) pe care
aplicatia NU o furnizeaza. PE HEAD (8b74ccb) se emitea un XML pe care validatorul il respinge cu 'F: Eroare
fatala de parsare' (CRASH validator NPE, dupa DUK regula R_cod131_132). DUPA: blocat PRE-DUK cu ValueError
clar. Gardul PICA pe HEAD (nu se ridica nimic) si TRECE dupa fix."""
import pytest
from core.d710 import calcul_d710 as _c
from core.common import Perioada

_PROF = {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL", "adresa": "Str Test 1 Bucuresti"}


def _gen(cod):
    return _c(_PROF, Perioada(2025, luna=3), {},
              {"obligatii": [{"cod_oblig": cod, "suma_dat_i": 100, "suma_dat_c": 150, "cod_bugetar": "5503XXXXXX"}]})


def test_cod_131_blocat_cu_motiv_data_i():
    with pytest.raises(ValueError) as ei:
        _gen("131")
    msg = str(ei.value)
    assert "131" in msg and "Data_I" in msg and "neacceptat" in msg, msg


def test_cod_132_blocat_cu_motiv_data_i():
    with pytest.raises(ValueError) as ei:
        _gen("132")
    msg = str(ei.value)
    assert "132" in msg and "Data_I" in msg, msg


def test_mesajul_citeaza_regula_duk():
    with pytest.raises(ValueError) as ei:
        _gen("131")
    assert "R_cod131_132" in str(ei.value)
