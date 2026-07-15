# -*- coding: utf-8 -*-
"""Teste gardian pentru duk (partea pura, fara java)."""
import os
from core.duk import CHEIE_DUK, validatoare_instalate, poate_valida, valideaza


def _fals_dist(tmp, jars):
    lib = os.path.join(tmp, "lib")
    os.makedirs(lib, exist_ok=True)
    for j in jars:
        open(os.path.join(lib, j), "w").close()
    return tmp


def test_biblioteca_de_baza_nu_e_declaratie(tmp_path):
    d = _fals_dist(str(tmp_path), ["Validator.jar", "D112Validator.jar"])
    assert validatoare_instalate(d) == {"D112"}
    assert poate_valida("", d) is False


def test_backup_nu_conteaza_ca_instalat(tmp_path):
    d = _fals_dist(str(tmp_path), ["D300Validator.jar.bak_pre22042026"])
    assert validatoare_instalate(d) == set()


def test_validator_neinstalat_da_gri_nu_valid(tmp_path):
    """Un XML nevalidat NU se declara valid."""
    d = _fals_dist(str(tmp_path), [])
    r = valideaza("<x/>", "d300", dist=d)
    assert r["stare"] == "gri"
    assert "nu e instalat" in r["temei"]


def test_tip_necunoscut_da_gri(tmp_path):
    r = valideaza("<x/>", "d999", dist=str(tmp_path))
    assert r["stare"] == "gri"


def test_toate_declaratiile_din_dispecer_au_cheie():
    from core.declaratii_api import DECLARATII
    for tip in DECLARATII:
        assert tip in CHEIE_DUK, "tipul %s nu are cheie DUK" % tip
