# -*- coding: utf-8 -*-
"""Teste securitate JWT — default gol pe cheie HMAC = bypass complet de auth (tokenuri forjabile).
Reparat 22.07 pe 3 straturi: garda cripto (nucleu), cfg_secret (excepție dură), fail-fast la pornire.
Vezi DECIZII 22.07.
"""
import pytest
from core import nucleu, common


# ---- Stratul 1: garda cripto in nucleu (secret gol -> exceptie, NU token/verificare cu cheie goala) ----

def test_creeaza_token_secret_gol_ridica():
    for gol in ("", None):
        with pytest.raises(ValueError):
            nucleu.creeaza_token({"uid": 1}, gol)


def test_verifica_token_secret_gol_ridica():
    for gol in ("", None):
        with pytest.raises(ValueError):
            nucleu.verifica_token("orice.token", gol)


def test_token_valid_cu_secret_real_merge():
    # cu secret real semnarea + verificarea functioneaza (nu am rupt calea buna)
    tok = nucleu.creeaza_token({"uid": 7}, "secret-real")
    r = nucleu.verifica_token(tok, "secret-real")
    assert r["ok"] and r["payload"]["uid"] == 7
    # secret DIFERIT -> semnatura invalida (nu exceptie, ci token respins)
    r2 = nucleu.verifica_token(tok, "alt-secret")
    assert not r2["ok"]


# ---- Stratul 2: cfg_secret — exceptie DURA la absenta/gol, NICIODATA default ----

def test_cfg_secret_absent_ridica(monkeypatch):
    monkeypatch.delenv("ZZ_TEST_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        common.cfg_secret("ZZ_TEST_SECRET")


def test_cfg_secret_gol_ridica(monkeypatch):
    monkeypatch.setenv("ZZ_TEST_SECRET", "")
    with pytest.raises(RuntimeError):
        common.cfg_secret("ZZ_TEST_SECRET")


def test_cfg_secret_setat_intoarce_valoarea(monkeypatch):
    monkeypatch.setenv("ZZ_TEST_SECRET", "valoare")
    assert common.cfg_secret("ZZ_TEST_SECRET") == "valoare"


# ---- Stratul 3: fail-fast la pornire (test pe FUNCTIE, nu pe serviciul real) ----

def test_boot_fara_jwt_secret_refuza():
    from main import verifica_secrete_obligatorii
    # env fara JWT_SECRET -> RuntimeError (app-ul nu porneste)
    with pytest.raises(RuntimeError):
        verifica_secrete_obligatorii(env={})
    with pytest.raises(RuntimeError):
        verifica_secrete_obligatorii(env={"JWT_SECRET": ""})


def test_boot_cu_jwt_secret_trece():
    from main import verifica_secrete_obligatorii
    verifica_secrete_obligatorii(env={"JWT_SECRET": "x"})   # nu ridica
