# -*- coding: utf-8 -*-
"""GARD TURA 3 — D710 T9: parsarea obligatiei MANUALE (contabil) ridica ValueError CLAR (camp + valoare)
in loc de exceptie bruta. PE HEAD (8b74ccb): suma "abc" -> decimal.InvalidOperation; cod_oblig lipsa ->
KeyError. DUPA: ValueError care numeste campul si valoarea, PRE-DUK. Gardul PICA pe HEAD (alt tip de
exceptie) si TRECE dupa fix."""
import pytest
from core.d710 import calcul_d710 as _c
from core.common import Perioada

_PROF = {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL", "adresa": "Str Test 1 Bucuresti"}


def _gen(obl):
    return _c(_PROF, Perioada(2025, luna=3), {}, {"obligatii": obl})


def test_b1_suma_nenumerica_ridica_valueerror_cu_camp_si_valoare():
    """B1: suma_dat_i='abc' -> ValueError (nu decimal.InvalidOperation)."""
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": "abc", "suma_dat_c": 150, "cota": "1"}])
    msg = str(ei.value)
    assert "suma_dat_i" in msg and "abc" in msg, "mesajul trebuie sa numeasca campul si valoarea: %r" % msg


def test_b1_suma_corectat_nenumerica():
    """B1 pe latura corectata: suma_dat_c='x' -> ValueError care numeste suma_dat_c."""
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": "x", "cota": "1"}])
    assert "suma_dat_c" in str(ei.value)


def test_b2_cod_oblig_lipsa_ridica_valueerror():
    """B2: cod_oblig absent -> ValueError (nu KeyError)."""
    with pytest.raises(ValueError) as ei:
        _gen([{"suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    assert "cod_oblig" in str(ei.value)


def test_b2_cod_oblig_gol_ridica_valueerror():
    """cod_oblig='' (gol) tratat la fel ca lipsa -> ValueError."""
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "  ", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    assert "cod_oblig" in str(ei.value)


def test_baseline_valid_inca_trece():
    """Baza valida nu e afectata de garduri: obligatie corecta se construieste normal."""
    res = _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    assert res.obligatii[0].suma_dat_i == 100 and res.obligatii[0].suma_dat_c == 150
