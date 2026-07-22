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


# ============================================================
#  FUS ORAR — verdictele de zi in Europe/Bucharest (robust la OS TZ). DECIZII 22.07.
# ============================================================
import datetime as _dt
import zoneinfo as _zi
from core.common import azi_ro

_UTC = _zi.ZoneInfo("UTC")
_BUC = _zi.ZoneInfo("Europe/Bucharest")


def test_azi_ro_in_fereastra_00_03_nu_sare_ziua():
    # instant real: 27 iul 22:00 UTC = 28 iul 01:00 ora Romaniei (fereastra 00:00-02:59)
    instant = _dt.datetime(2026, 7, 27, 22, 0, tzinfo=_UTC)
    # azi_ro() -> ZIUA ROMANIEI (28), corect pt verdictul de zi
    assert azi_ro(acum=instant) == _dt.date(2026, 7, 28)
    # "date.today() sub proces UTC" ar da ziua UTC (27) -> SARE ziua
    assert instant.astimezone(_UTC).date() == _dt.date(2026, 7, 27)
    # ele DIFERA in fereastra -> exact bug-ul evitat
    assert azi_ro(acum=instant) != instant.astimezone(_UTC).date()


def test_azi_ro_in_afara_ferestrei_coincide():
    # la pranz ambele dau aceeasi zi (fereastra e doar 00:00-02:59)
    instant = _dt.datetime(2026, 7, 27, 12, 0, tzinfo=_UTC)
    assert azi_ro(acum=instant) == instant.astimezone(_UTC).date() == _dt.date(2026, 7, 27)


# ---- garda de boot pe fus (test pe FUNCTIE, offset/pg_tz injectate) ----

def test_boot_os_tz_gresit_refuza():
    from main import verifica_fus_orar
    buc_off = _dt.datetime.now(_BUC).utcoffset()
    # OS pe UTC (offset 0) -> refuz, chiar daca PG e corect
    with pytest.raises(RuntimeError):
        verifica_fus_orar(offset_local=_dt.timedelta(0), pg_tz="Europe/Bucharest")
    # PG pe UTC -> refuz, chiar daca OS e corect
    with pytest.raises(RuntimeError):
        verifica_fus_orar(offset_local=buc_off, pg_tz="UTC")


def test_boot_fus_corect_trece():
    from main import verifica_fus_orar
    buc_off = _dt.datetime.now(_BUC).utcoffset()
    verifica_fus_orar(offset_local=buc_off, pg_tz="Europe/Bucharest")   # nu ridica
