# -*- coding: utf-8 -*-
"""
Teste core/spv_conector.py — pe MOCK, niciodata pe ANAF real (brief BRIEF_CODE_CONECTOR_SPV.md).

Apara explicit CAPCANA CRITICA din ARHITECTURA_SPV.md: la refresh se salveaza AMBELE
valori noi (access_token SI refresh_token). test_refresh_salveaza_ambele dovedeste asta
prin round-trip real in DB (INSERT + refresh mock + citire + ROLLBACK) — daca cineva
"optimizeaza" salvand doar access-ul, testul pica.

Env setat INAINTE de import (constantele modulului se citesc la import).
Testele DB ruleaza pe server (get skip daca DB indisponibil), cu ROLLBACK — zero reziduu.
"""
import os
import json
import base64
import time

# --- env de test, INAINTE de importul modulului (constante la import) ---
from cryptography.fernet import Fernet
os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST_CLIENT")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")

import pytest
import psycopg2

from core import db as _db
from core import spv_conector as s

FIRM_TEST = 999999   # id de test; toate testele DB fac ROLLBACK


def _fake_jwt(payload):
    """JWT minim (header.payload.sig) — doar payload conteaza (decodare fara verificare)."""
    def b64(d):
        return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
    return "%s.%s.%s" % (b64({"alg": "none"}), b64(payload), "sig")


# ============================================================
#  PURE — fara DB
# ============================================================
def test_cripteaza_decripteaza_roundtrip():
    assert s.decripteaza(s.cripteaza("tok-secret")) == "tok-secret"


def test_cripteaza_produce_ciphertext_diferit_de_clar():
    assert s.cripteaza("acces123") != "acces123"


def test_decodeaza_jwt():
    tok = _fake_jwt({"serial_number": "AB12", "exp": 111})
    assert s.decodeaza_jwt(tok) == {"serial_number": "AB12", "exp": 111}


def test_decodeaza_jwt_gunoi_nu_arunca():
    assert s.decodeaza_jwt("nu-e-jwt") == {}


def test_extrage_serial_din_candidati():
    assert s.extrage_serial({"serialNumber": "XYZ"}) == "XYZ"
    assert s.extrage_serial({"sub": "fallback-sub"}) == "fallback-sub"


def test_extrage_serial_necunoscut_marcat_nu_ghicit():
    # NECUNOSCUTA DECLARATA: fara claim cunoscut -> marcaj, nu valoare inventata
    assert s.extrage_serial({"altceva": 1}) == "NECONFIRMAT"


def test_state_roundtrip():
    st = s.genereaza_state(42)
    assert s.verifica_state(st) == 42


def test_state_expirat_arunca():
    st = s.genereaza_state(42, acum=1000)
    with pytest.raises(s.EroareSpv):
        s.verifica_state(st, acum=1000 + s.STATE_DURATA_SEC + 1)


def test_state_modificat_arunca():
    st = s.genereaza_state(42)
    with pytest.raises(s.EroareSpv):
        s.verifica_state(st[:-3] + "xxx")


def test_url_autorizare_contine_parametrii():
    url, st = s.url_autorizare(7)
    assert s.AUTHORIZE_URL in url
    assert "response_type=code" in url
    assert "token_content_type=jwt" in url
    assert "state=" in url
    assert "iconta.eu%2Fanaf%2Foauth%2Fcallback" in url  # redirect_uri url-encoded
    assert s.verifica_state(st) == 7


def test_valori_din_raspuns_extrage_ambele():
    acum = 1_700_000_000
    tok = {"access_token": _fake_jwt({"serial_number": "SER-1", "exp": acum + 90 * 86400}),
           "refresh_token": "refresh-nou", "expires_in": 90 * 86400}
    v = s.valori_din_raspuns_token(tok, acum=acum)
    assert v["access_token"] == tok["access_token"]
    assert v["refresh_token"] == "refresh-nou"
    assert v["serial_certificat"] == "SER-1"
    # refresh_expira ~ acum + 365 zile
    assert v["refresh_expira"].timestamp() == pytest.approx(acum + 365 * 86400, abs=2)
    assert v["access_expira"].timestamp() == pytest.approx(acum + 90 * 86400, abs=2)


def test_valori_din_raspuns_fara_refresh_arunca():
    with pytest.raises(s.EroareSpv):
        s.valori_din_raspuns_token({"access_token": _fake_jwt({}), "expires_in": 10})


# ============================================================
#  DB + MOCK — se dovedesc pe server, cu ROLLBACK
# ============================================================
@pytest.fixture
def conn():
    try:
        c = psycopg2.connect(_db.dsn_din_config(_db.config_din_env()))
    except Exception as e:  # noqa: BLE001
        pytest.skip("DB indisponibil: %s" % e)
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def _salveaza_initial(conn, serial="SER-1", access="acc-0", refresh="ref-0"):
    acum = int(time.time())
    valori = {
        "access_token": _fake_jwt({"serial_number": serial, "exp": acum + 90 * 86400})
        if access == "JWT" else access,
        "refresh_token": refresh,
        "serial_certificat": serial,
        "access_expira": s.datetime.fromtimestamp(acum + 90 * 86400, tz=s.timezone.utc),
        "refresh_expira": s.datetime.fromtimestamp(acum + 365 * 86400, tz=s.timezone.utc),
    }
    return s.salveaza_token(conn, FIRM_TEST, valori)


def test_ia_token_activ_none_daca_lipseste(conn):
    assert s.ia_token_activ(conn, FIRM_TEST) is None


def test_salveaza_si_citeste_decripteaza(conn):
    _salveaza_initial(conn, access="acc-0", refresh="ref-0")
    tok = s.ia_token_activ(conn, FIRM_TEST)
    assert tok["access_token"] == "acc-0"     # decriptat corect
    assert tok["refresh_token"] == "ref-0"
    # stocat criptat in DB, nu in clar
    with conn.cursor() as cur:
        cur.execute("SELECT access_token FROM public.spv_token WHERE id=%s", (tok["id"],))
        assert cur.fetchone()[0] != "acc-0"


def test_refresh_salveaza_ambele_valori_noi(conn, monkeypatch):
    """CAPCANA CRITICA: refresh-ul salveaza AMBELE valori noi (access + refresh)."""
    _salveaza_initial(conn, serial="SER-1", access="acc-0", refresh="ref-0")
    tok = s.ia_token_activ(conn, FIRM_TEST)
    tok["accounting_firm_id"] = FIRM_TEST

    acum = int(time.time())
    raspuns_nou = {
        "access_token": _fake_jwt({"serial_number": "SER-1", "exp": acum + 90 * 86400, "v": 2}),
        "refresh_token": "ref-1-NOU",
        "expires_in": 90 * 86400,
    }
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda rt: raspuns_nou)

    s.reimprospateaza_token(conn, tok)

    dupa = s.ia_token_activ(conn, FIRM_TEST)
    assert dupa["refresh_token"] == "ref-1-NOU", "refresh-ul NOU nu a fost salvat (capcana rotatiei)"
    assert dupa["access_token"] == raspuns_nou["access_token"], "access-ul nou nu a fost salvat"
    assert dupa["access_token"] != "acc-0" and dupa["refresh_token"] != "ref-0"


def test_refresh_esuat_dezactiveaza_tokenul(conn, monkeypatch):
    id0 = _salveaza_initial(conn, refresh="ref-0")
    tok = s.ia_token_activ(conn, FIRM_TEST)
    tok["accounting_firm_id"] = FIRM_TEST

    def _cade(rt):
        raise s.EroareSpv("HTTP 400 la /token")
    monkeypatch.setattr(s, "reimprospateaza_pereche", _cade)

    with pytest.raises(s.EroareSpvRefreshEsuat):
        s.reimprospateaza_token(conn, tok)
    # tokenul devine inactiv -> ia_token_activ nu-l mai vede
    assert s.ia_token_activ(conn, FIRM_TEST) is None
    with conn.cursor() as cur:
        cur.execute("SELECT activ FROM public.spv_token WHERE id=%s", (id0,))
        assert cur.fetchone()[0] is False
