# -*- coding: utf-8 -*-
"""GARD TURA 3 — D710 B4: sume negative in obligatia manuala. PE HEAD (8b74ccb) o suma negativa era emisa
in XML si respinsa abia de DUK ('suma_dat_I: valoarea -100 nu se incadreaza in intervalul cerut'). DUPA:
ValueError PRE-DUK care numeste obligatia si campul. Gardul PICA pe HEAD (nu se ridica nimic) si TRECE
dupa fix."""
import pytest
from core.d710 import calcul_d710 as _c
from core.common import Perioada

_PROF = {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL", "adresa": "Str Test 1 Bucuresti"}


def _gen(obl):
    return _c(_PROF, Perioada(2025, luna=3), {}, {"obligatii": obl})


def test_b4_suma_initiala_negativa_ridica():
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": -100, "suma_dat_c": 150, "cota": "1"}])
    msg = str(ei.value)
    assert "suma_dat_i" in msg and "negativ" in msg and "121" in msg, msg


def test_b4_suma_corectata_negativa_ridica():
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": -50, "cota": "1"}])
    assert "suma_dat_c" in str(ei.value) and "negativ" in str(ei.value)


def test_b4_ambele_negative_ridica():
    """Ambele negative: pe HEAD erau tratate ca <=0 si SARITE tacit; acum se ridica pe prima."""
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "121", "suma_dat_i": -100, "suma_dat_c": -50, "cota": "1"}])


def test_baseline_pozitiv_trece():
    res = _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    assert res.obligatii[0].suma_dat_i == 100
