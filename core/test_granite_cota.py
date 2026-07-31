# -*- coding: utf-8 -*-
"""Granite API — cota TVA lipsa = intrare INCOMPLETA -> eroare, nu default 21 ghicit.

DE CE (31.07.2026, directie Costin): la granita, `corp.get("cota", 21)` insemna "daca
apelantul n-a trimis cota, pun eu una". Dar o factura/linie fara cota e o intrare incompleta,
nu o factura cu cota standard. Regula bazei nule: se ridica eroare, nu se ghiceste - nici
macar corect. Un default cu common.cota() ar fi tot o valoare inventata, doar actualizata.

Distinctie cheie: cota 0 (scutit/neplatitor) e VALOARE VALIDA, nu absenta.
"""
import pytest

from core.common import cota_ceruta


# ── TEMA A: helper de granita cota_ceruta(corp) ──────────────────────────────
def test_cota_lipsa_din_corp_ridica():
    """Cheie cota absenta -> ValueError (endpoint o prinde -> HTTP 422), NU 21 tacut."""
    with pytest.raises(ValueError) as e:
        cota_ceruta({"pret_vanzare": 100, "pret_cumparare": 80})
    assert "cot" in str(e.value).lower()


def test_cota_none_explicit_ridica():
    with pytest.raises(ValueError):
        cota_ceruta({"cota": None})


def test_cota_zero_scutit_e_valoare_valida_nu_absenta():
    """0 = scutit/neplatitor TVA: cota valida, NU absenta -> se intoarce 0, nu se ridica,
    nu se transforma in 21. (regula bazei nule distinge None de 0)."""
    assert cota_ceruta({"cota": 0}) == 0


def test_cota_prezenta_se_intoarce_ca_atare():
    assert cota_ceruta({"cota": 11}) == 11
    assert cota_ceruta({"cota": 21}) == 21
