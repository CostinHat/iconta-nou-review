# -*- coding: utf-8 -*-
"""Teste gardian pentru core/numere.py — sursa UNICA de parsare a numerelor.

Extras 15.07.2026 din 9 copii ale aceleiasi functii, 6 cu acelasi bug: "(200)"
(format contabil = suma negativa) devenea 0.0 TACUT. O sursa unica inseamna un
singur loc de reparat si un singur loc de testat.
"""
import pytest
from core.numere import numar


def test_formate_uzuale():
    assert numar("1.234,56") == 1234.56      # RO
    assert numar("1,234.56") == 1234.56      # EN
    assert numar("1 000") == 1000
    assert numar("") == 0
    assert numar(None) == 0
    assert numar(-12.5) == -12.5


def test_parantezele_sunt_suma_negativa():
    assert numar("(500)") == -500
    assert numar("(1.234,56)") == -1234.56


def test_sufixele_uzuale():
    assert numar("500 lei") == 500
    assert numar("1.234,56 RON") == 1234.56
    assert numar("2 buc") == 2
    assert numar("60%") == 60


def test_strict_nu_ascunde_gunoiul():
    assert numar("N/A") == 0
    with pytest.raises(ValueError):
        numar("N/A", strict=True)


def test_toate_modulele_folosesc_sursa_unica():
    """Regresie: 9 module aveau _numar copiata, 6 cu bugul parantezelor.
    Fara asta, un fix in numere.py nu s-ar propaga si bug-ul s-ar putea intoarce
    intr-un modul necunoscut."""
    import inspect
    from core import (articole_import_api, asociati_import_api,
                       mijloace_fixe_import_api, retete_import_api,
                       salariati_import_api, solduri_parteneri_api, solduri_api)
    for mod in (articole_import_api, asociati_import_api, mijloace_fixe_import_api,
                retete_import_api, salariati_import_api, solduri_parteneri_api):
        assert mod._numar is numar, "%s nu foloseste sursa unica" % mod.__name__
    # solduri_api ramane sursa istorica, cu semnatura proprie (strict=) - verificat separat
    assert solduri_api._numar("(200)") == -200.0
