# -*- coding: utf-8 -*-
"""Teste gardian pentru solduri_api (partea PURA).

Modulul n-a avut niciun test. Bugul de mai jos a fost gasit prin migrare reala,
nu de teste: ecranul afisa "neechilibrat" rosu, iar importul scria oricum.
"""
import pytest
from core.solduri_api import verifica_echilibru, importa, _numar


def test_balanta_echilibrata():
    ok, td, tc, dif = verifica_echilibru([
        {"cont": "4111", "debit": 1000, "credit": 0},
        {"cont": "401", "debit": 0, "credit": 1000},
    ])
    assert ok and td == 1000 and tc == 1000 and dif == 0


def test_balanta_neechilibrata_e_prinsa():
    ok, td, tc, dif = verifica_echilibru([
        {"cont": "4111", "debit": 1000, "credit": 0},
        {"cont": "401", "debit": 0, "credit": 900},
    ])
    assert not ok and dif == 100


def test_importa_REFUZA_balanta_neechilibrata():
    """Semnalarea fara oprire e mai rea decat tacerea: da impresia ca s-a verificat.
    Regresie 15.07.2026: importa() scria orice, iar migrarea marca stratul 'gata' verde."""
    with pytest.raises(ValueError) as e:
        importa(None, [{"cont": "4111", "debit": 1000, "credit": 0},
                       {"cont": "401", "debit": 0, "credit": 900}])
    m = str(e.value)
    assert "echilibr" in m.lower()
    assert "100" in m          # spune diferenta
    assert "debit" in m.lower() and "credit" in m.lower()


def test_toleranta_de_un_ban():
    """Rotunjirile de bani nu blocheaza o balanta corecta."""
    ok, _, _, _ = verifica_echilibru([
        {"cont": "4111", "debit": 1000.004, "credit": 0},
        {"cont": "401", "debit": 0, "credit": 1000},
    ])
    assert ok


def test_balanta_goala_e_echilibrata():
    assert verifica_echilibru([])[0]
    assert verifica_echilibru(None)[0]


def test_numar_accepta_formatele_din_export():
    assert _numar("1.234,56") == 1234.56       # RO
    assert _numar("1,234.56") == 1234.56       # EN
    assert _numar("1 000") == 1000
    assert _numar("") == 0
    assert _numar(None) == 0
    assert _numar(-12.5) == -12.5


def test_parantezele_sunt_suma_negativa():
    """Format contabil (SAGA/Ciel/Excel): (500) = -500. Inainte cadea pe float() si
    devenea 0.0 TACUT - soldul disparea, iar totalurile pareau corecte."""
    assert _numar("(500)") == -500
    assert _numar("(1.234,56)") == -1234.56


def test_sufixele_de_moneda_nu_anuleaza_suma():
    """Exporturile scriu '500 lei' / '1.234,56 RON'."""
    assert _numar("500 lei") == 500
    assert _numar("1.234,56 RON") == 1234.56


def test_strict_nu_transforma_gunoiul_in_zero():
    """Un sold care devine 0 in tacere e mai periculos decat un import refuzat."""
    assert _numar("N/A") == 0                  # implicit: tolerant (comportament vechi)
    with pytest.raises(ValueError):
        _numar("N/A", strict=True)
