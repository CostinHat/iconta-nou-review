# -*- coding: utf-8 -*-
"""
Teste core/etransport_send.py (F121) — pe MOCK, niciodata pe ANAF real.

Apara: garda de timp UIT (fereastra legala 3z inainte / 5-15z valabilitate), construirea URL-urilor
(path params ETRANSP/versiune), si portile trimite (blocat_timp, nevalidat, upload -> incarcat + UIT).
"""
import os
from datetime import date, timedelta

from cryptography.fernet import Fernet
os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")

import pytest

from core import db as _db
from core import spv_conector as sc
from core import etransport_send as et

PRIN = sc.principal_firm(1)


class _R:
    def __init__(self, text="", status=200):
        self.text = text; self.status_code = status


# ---- OK upload response (forma pattern ANAF; formatul exact se confirma la primul raspuns real) ----
UP_OK = '<header ExecutionStatus="0" index_incarcare="777" UIT="ABC12345"/>'
UP_ERR = '<header ExecutionStatus="1"><Errors errorMessage="date invalide"/></header>'


# ============================================================
#  GARDA DE TIMP UIT — pura
# ============================================================
def test_fereastra_in_termen_national():
    azi = date(2026, 7, 18)
    f = et.fereastra_uit(azi, intracom=False, acum=azi)   # transport azi, national
    assert f["poate_trimite"] and f["zile_valabilitate"] == 5
    assert f["uit_valabil_pana"] == azi + timedelta(days=5)


def test_fereastra_intracom_15_zile():
    azi = date(2026, 7, 18)
    f = et.fereastra_uit(azi + timedelta(days=2), intracom=True, acum=azi)
    assert f["poate_trimite"] and f["zile_valabilitate"] == 15


def test_fereastra_prea_devreme_blocheaza():
    azi = date(2026, 7, 18)
    f = et.fereastra_uit(azi + timedelta(days=5), intracom=False, acum=azi)  # >3 zile inainte
    assert not f["poate_trimite"] and f["prea_devreme"]


def test_fereastra_expirat_blocheaza():
    azi = date(2026, 7, 18)
    f = et.fereastra_uit(azi - timedelta(days=10), intracom=False, acum=azi)  # UIT (5z) demult trecut
    assert not f["poate_trimite"] and f["expirat"]


# ============================================================
#  URL-uri (path params) — mock apel_anaf
# ============================================================
def test_url_upload_stare_lista(monkeypatch):
    cap = {}
    monkeypatch.setattr(sc, "apel_anaf", lambda p, m, url, **kw: cap.setdefault("urls", []).append((m, url)) or _R(UP_OK))
    et.upload_uit(PRIN, "RO14399840", "<x/>", versiune=2, mediu="test")
    et.stare_uit(PRIN, "777", mediu="test")
    et.lista_uit(PRIN, 99, "RO14399840", mediu="test")
    urls = dict((u.split("/ws/v1/")[1].split("/")[0], (m, u)) for m, u in cap["urls"])
    # upload: ETRANSP + cif doar cifre + versiune, in PATH
    assert "/ETRANSPORT/ws/v1/upload/ETRANSP/14399840/2" in cap["urls"][0][1] and cap["urls"][0][0] == "POST"
    assert "/ETRANSPORT/ws/v1/stareMesaj/777" in cap["urls"][1][1]
    assert "/ETRANSPORT/ws/v1/lista/60/14399840" in cap["urls"][2][1]   # zile clamp 99->60
    assert "api.anaf.ro/test/ETRANSPORT" in cap["urls"][0][1]


# ============================================================
#  PORTI trimite — mock
# ============================================================
def test_trimite_blocat_timp_nu_atinge_reteaua(monkeypatch):
    def _nu(*a, **k): raise AssertionError("nu trebuia sa apeleze ANAF")
    monkeypatch.setattr(sc, "apel_anaf", _nu)
    azi = date(2026, 7, 18)
    r = et.trimite("tenant_002", PRIN, "14399840", "<x/>", data_transport=azi + timedelta(days=10),
                   intracom=False, mediu="prod", acum=azi)   # prea devreme
    assert r["stare"] == "blocat_timp"


def test_trimite_nevalidat_nu_uploadeaza_prod(monkeypatch):
    # POARTA 3: validarea pe TEST intoarce erori -> nu se trimite pe prod
    monkeypatch.setattr(sc, "apel_anaf", lambda p, m, url, **kw: _R(UP_ERR))
    azi = date(2026, 7, 18)
    r = et.trimite("tenant_002", PRIN, "14399840", "<x/>", data_transport=azi, intracom=False,
                   mediu="prod", acum=azi)
    assert r["stare"] == "nevalidat" and r["erori"]


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_trimite_prod_incarcat_scrie_uit_si_valabilitate(monkeypatch):
    monkeypatch.setattr(sc, "apel_anaf", lambda p, m, url, **kw: _R(UP_OK))   # TEST + prod ambele ok
    azi = date(2026, 7, 18)
    r = et.trimite("tenant_002", PRIN, "14399840", "<uniqXML_TEST/>", data_transport=azi,
                   intracom=False, mediu="prod", acum=azi)
    try:
        assert r["stare"] == "incarcat" and r["uit"] == "ABC12345"
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT stare, uit, uit_valabil_pana, index_incarcare FROM tenant_002.etransport_trimiteri WHERE id=%s", (r["trimitere_id"],))
                row = cur.fetchone()
        assert row[0] == "incarcat" and row[1] == "ABC12345" and row[2] == azi + timedelta(days=5)
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM tenant_002.etransport_trimiteri WHERE id=%s", (r["trimitere_id"],))
