# -*- coding: utf-8 -*-
"""
Teste core/spv_conector.py — pe MOCK, niciodata pe ANAF real (brief BRIEF_CODE_CONECTOR_SPV.md).

Apara explicit CAPCANA CRITICA din ARHITECTURA_SPV.md: la refresh se salveaza AMBELE
valori noi (access_token SI refresh_token). test_refresh_salveaza_ambele dovedeste asta
prin round-trip real in DB (INSERT + refresh mock + citire + ROLLBACK) — daca cineva
"optimizeaza" salvand doar access-ul, testul pica.

Apara si PRINCIPALUL (F160): tokenul e cheiat pe cabinet XOR gratuit, iar cronul F177 NU
sare peste tokenele gratuite (GARDUL 3).

Env de test in core/conftest.py (constantele modulului se citesc la import; conftest ruleaza primul).
Testele DB ruleaza pe server (get skip daca DB indisponibil), cu ROLLBACK — zero reziduu.
"""
import json
import base64
import time

# env de test (SPV_FERNET_KEY/JWT_SECRET/ANAF_CLIENT_ID/ANAF_REDIRECT_URI) e setat in core/conftest.py,
# INAINTE de colectare -> constantele spv_conector (citite la import) sunt garantat prezente indiferent
# de ordinea in care testele importa modulul. Vezi conftest pentru de ce nu aici.
import pytest
import psycopg2

from core import db as _db
from core import spv_conector as s

FIRM_TEST = 999999      # cabinet de test; toate testele DB fac ROLLBACK
TENANT_TEST = 888888    # firma gratuita de test (tenant_id fara FK)
PRIN_FIRM = s.principal_firm(FIRM_TEST)
PRIN_TENANT = s.principal_tenant(TENANT_TEST)


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
    assert s.extrage_serial({"altceva": 1}) == "NECONFIRMAT"


def test_state_roundtrip_firm():
    st = s.genereaza_state(s.principal_firm(42))
    assert s.verifica_state(st) == s.principal_firm(42)


def test_state_roundtrip_tenant():
    # PRINCIPAL gratuit: state-ul poarta kind=tenant, nu se confunda cu firm
    st = s.genereaza_state(s.principal_tenant(42))
    p = s.verifica_state(st)
    assert p == s.principal_tenant(42)
    assert p != s.principal_firm(42)   # acelasi id, principal DIFERIT


def test_state_expirat_arunca():
    st = s.genereaza_state(s.principal_firm(42), acum=1000)
    with pytest.raises(s.EroareSpv):
        s.verifica_state(st, acum=1000 + s.STATE_DURATA_SEC + 1)


def test_state_modificat_arunca():
    st = s.genereaza_state(s.principal_firm(42))
    with pytest.raises(s.EroareSpv):
        s.verifica_state(st[:-3] + "xxx")


def test_url_autorizare_contine_parametrii():
    url, st = s.url_autorizare(s.principal_firm(7))
    assert s.AUTHORIZE_URL in url
    assert "response_type=code" in url
    assert "token_content_type=jwt" in url
    assert "state=" in url
    assert "iconta.eu%2Fanaf%2Foauth%2Fcallback" in url
    assert s.verifica_state(st) == s.principal_firm(7)


def test_valori_din_raspuns_extrage_ambele():
    acum = 1_700_000_000
    tok = {"access_token": _fake_jwt({"serial_number": "SER-1", "exp": acum + 90 * 86400}),
           "refresh_token": "refresh-nou", "expires_in": 90 * 86400}
    v = s.valori_din_raspuns_token(tok, acum=acum)
    assert v["access_token"] == tok["access_token"]
    assert v["refresh_token"] == "refresh-nou"
    assert v["serial_certificat"] == "SER-1"
    assert v["refresh_expira"].timestamp() == pytest.approx(acum + 365 * 86400, abs=2)
    assert v["access_expira"].timestamp() == pytest.approx(acum + 90 * 86400, abs=2)


def test_valori_din_raspuns_fara_refresh_arunca():
    with pytest.raises(s.EroareSpv):
        s.valori_din_raspuns_token({"access_token": _fake_jwt({}), "expires_in": 10})


def test_principal_din_rand():
    assert s.principal_din_rand(5, None) == s.principal_firm(5)
    assert s.principal_din_rand(None, 8) == s.principal_tenant(8)
    with pytest.raises(s.EroareSpv):
        s.principal_din_rand(None, None)   # GARDUL 3: rand fara principal = eroare, nu firm tacit


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


def _salveaza_initial(conn, principal=PRIN_FIRM, serial="SER-1", access="acc-0", refresh="ref-0"):
    acum = int(time.time())
    valori = {
        "access_token": _fake_jwt({"serial_number": serial, "exp": acum + 90 * 86400})
        if access == "JWT" else access,
        "refresh_token": refresh,
        "serial_certificat": serial,
        "access_expira": s.datetime.fromtimestamp(acum + 90 * 86400, tz=s.timezone.utc),
        "refresh_expira": s.datetime.fromtimestamp(acum + 365 * 86400, tz=s.timezone.utc),
    }
    return s.salveaza_token(conn, principal, valori)


def test_ia_token_activ_none_daca_lipseste(conn):
    assert s.ia_token_activ(conn, PRIN_FIRM) is None


def test_salveaza_si_citeste_decripteaza(conn):
    _salveaza_initial(conn, access="acc-0", refresh="ref-0")
    tok = s.ia_token_activ(conn, PRIN_FIRM)
    assert tok["access_token"] == "acc-0"     # decriptat corect
    assert tok["refresh_token"] == "ref-0"
    assert tok["accounting_firm_id"] == FIRM_TEST and tok["tenant_id"] is None
    with conn.cursor() as cur:
        cur.execute("SELECT access_token FROM public.spv_token WHERE id=%s", (tok["id"],))
        assert cur.fetchone()[0] != "acc-0"   # stocat criptat


def test_salveaza_si_citeste_gratuit_izolat_de_cabinet(conn):
    # token gratuit (tenant) si token cabinet cu acelasi id numeric NU se confunda
    _salveaza_initial(conn, principal=PRIN_TENANT, serial="SER-G", access="acc-grat")
    tg = s.ia_token_activ(conn, PRIN_TENANT)
    assert tg["access_token"] == "acc-grat"
    assert tg["tenant_id"] == TENANT_TEST and tg["accounting_firm_id"] is None
    assert s.ia_token_activ(conn, s.principal_firm(TENANT_TEST)) is None  # nu e cheiat pe firm


def test_refresh_salveaza_ambele_valori_noi(conn, monkeypatch):
    """CAPCANA CRITICA: refresh-ul salveaza AMBELE valori noi (access + refresh)."""
    _salveaza_initial(conn, serial="SER-1", access="acc-0", refresh="ref-0")
    tok = s.ia_token_activ(conn, PRIN_FIRM)

    acum = int(time.time())
    raspuns_nou = {
        "access_token": _fake_jwt({"serial_number": "SER-1", "exp": acum + 90 * 86400, "v": 2}),
        "refresh_token": "ref-1-NOU",
        "expires_in": 90 * 86400,
    }
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda rt: raspuns_nou)
    s.reimprospateaza_token(conn, tok)

    dupa = s.ia_token_activ(conn, PRIN_FIRM)
    assert dupa["refresh_token"] == "ref-1-NOU", "refresh-ul NOU nu a fost salvat (capcana rotatiei)"
    assert dupa["access_token"] == raspuns_nou["access_token"], "access-ul nou nu a fost salvat"
    assert dupa["access_token"] != "acc-0" and dupa["refresh_token"] != "ref-0"


def test_refresh_gratuit_deriveaza_principal_tenant(conn, monkeypatch):
    """GARDUL 3: refresh pe un token GRATUIT deriva principal_tenant, nu crapa pe firm NULL."""
    _salveaza_initial(conn, principal=PRIN_TENANT, serial="SER-G", access="acc-0", refresh="ref-0")
    tok = s.ia_token_activ(conn, PRIN_TENANT)
    acum = int(time.time())
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda rt: {
        "access_token": _fake_jwt({"serial_number": "SER-G", "exp": acum + 90 * 86400}),
        "refresh_token": "ref-grat-NOU", "expires_in": 90 * 86400})
    s.reimprospateaza_token(conn, tok)
    assert s.ia_token_activ(conn, PRIN_TENANT)["refresh_token"] == "ref-grat-NOU"


def test_cron_F177_prinde_token_gratuit(conn):
    """GARDUL 3 (capcana F177): query-ul de reinnoire NU sare peste tokenele gratuite."""
    from core import spv_refresh
    acum = int(time.time())
    valori = {
        "access_token": "acc-g", "refresh_token": "ref-g", "serial_certificat": "SER-G",
        "access_expira": s.datetime.fromtimestamp(acum + 3 * 86400, tz=s.timezone.utc),  # sub marja
        "refresh_expira": s.datetime.fromtimestamp(acum + 365 * 86400, tz=s.timezone.utc),
    }
    s.salveaza_token(conn, PRIN_TENANT, valori)
    randuri = spv_refresh.token_uri_de_reimprospatat(conn)   # SELECT: id, firm, tenant, serial, refresh, expira
    gratuite = [r for r in randuri if r[2] == TENANT_TEST]
    assert gratuite, "cronul F177 a SARIT peste tokenul gratuit (accounting_firm_id NULL)"
    assert gratuite[0][1] is None   # accounting_firm_id NULL pe randul gratuit


def test_stare_conexiune_neconectat(conn):
    assert s.stare_conexiune(conn, PRIN_FIRM)["conectat"] is False


def test_stare_conexiune_conectat_fara_secrete(conn):
    _salveaza_initial(conn, serial="SER-1")
    st = s.stare_conexiune(conn, PRIN_FIRM)
    assert st["conectat"] is True
    assert st["serial_certificat"] == "SER-1"
    assert "access_token" not in st and "refresh_token" not in st
    assert st["expira_curand"] is False


def test_refresh_esuat_dezactiveaza_tokenul(conn, monkeypatch):
    id0 = _salveaza_initial(conn, refresh="ref-0")
    tok = s.ia_token_activ(conn, PRIN_FIRM)

    def _cade(rt):
        raise s.EroareSpv("HTTP 400 la /token")
    monkeypatch.setattr(s, "reimprospateaza_pereche", _cade)

    with pytest.raises(s.EroareSpvRefreshEsuat):
        s.reimprospateaza_token(conn, tok)
    assert s.ia_token_activ(conn, PRIN_FIRM) is None
    with conn.cursor() as cur:
        cur.execute("SELECT activ FROM public.spv_token WHERE id=%s", (id0,))
        assert cur.fetchone()[0] is False
