# -*- coding: utf-8 -*-
"""GARD TURA 3 — D710: valorile MANUALE cod_oblig / cod_bugetar / cota / scadenta erau acceptate raw si
respinse abia de DUK. PE HEAD (8b74ccb) toate construiau XML fara eroare (proba: DUK 'erori'). DUPA:
fiecare e prinsa PRE-DUK cu motiv exact. Gardurile PICA pe HEAD (nu se ridica nimic) si TREC dupa fix."""
import pytest
from core.d710 import calcul_d710 as _c
from core.common import Perioada

_PROF = {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL", "adresa": "Str Test 1 Bucuresti"}


def _gen(obl, luna=3):
    return _c(_PROF, Perioada(2025, luna=luna), {}, {"obligatii": obl})


# ---- C2/C3: cod_oblig in afara nomenclatorului ----

def test_c2_cod_oblig_necunoscut_ridica():
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "888", "suma_dat_i": 100, "suma_dat_c": 150}])
    assert "888" in str(ei.value) and "nomenclator" in str(ei.value)


def test_c3_cod_necunoscut_cu_cod_bugetar_manual_tot_respins():
    """Un cod_bugetar manual NU mai lasa un cod garbage sa treaca (ocolire eliminata)."""
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "888", "suma_dat_i": 100, "suma_dat_c": 150, "cod_bugetar": "5503XXXXXX"}])


# ---- D4: cod_bugetar manual divergent de nomenclator ----

def test_d4_cod_bugetar_manual_gresit_ridica_r14a():
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "cod_bugetar": "9999999999"}])
    assert "R14a" in str(ei.value) and "9999999999" in str(ei.value)


def test_d4_cod_bugetar_manual_corect_trece():
    """cod_bugetar manual = nomenclatorul (5503XXXXXX) -> acceptat."""
    o = _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "cod_bugetar": "5503XXXXXX"}]).obligatii[0]
    assert o.cod_bugetar == "5503XXXXXX"


# ---- E: cota (rata micro) in afara ratelor valide pt cod 121 ----

def test_e_cota_micro_invalida_ridica_r17():
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "16"}])
    assert "R17" in str(ei.value) and "16" in str(ei.value)


def test_e_cota_micro_valida_trece():
    for rata in ("1", "3"):
        o = _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": rata}]).obligatii[0]
        assert o.cota == rata


# ---- E: scadenta manuala forma corecta dar data calendaristica imposibila ----

def test_e_scadenta_calendar_invalida_ridica():
    with pytest.raises(ValueError) as ei:
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "scadenta": "31.02.2025"}])
    assert "calendaristic" in str(ei.value) and "31.02.2025" in str(ei.value)


def test_e_scadenta_luna_13_ridica():
    with pytest.raises(ValueError):
        _gen([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "scadenta": "10.13.2025"}])


def test_e_scadenta_valida_trece():
    o = _gen([{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400, "scadenta": "25.12.2025"}], luna=12).obligatii[0]
    assert o.scadenta == "25.12.2025"
