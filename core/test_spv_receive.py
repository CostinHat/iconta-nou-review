# -*- coding: utf-8 -*-
"""
Teste core/spv_receive.py (F179) — pe MOCK (retea + parser), niciodata pe ANAF real.

Apara cele 3 garduri: anti-scurgere (cif_beneficiar == CIF tenant la insert), dedup pe id_mesaj_anaf,
masina de stari (ciorna daca parsabila / descarcata fallback; NU creeaza cheltuiala - four-eyes).
"""
import os

from cryptography.fernet import Fernet
os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")

import pytest

from core import db as _db
from core import spv_conector as sc
from core import efactura_send as efs
from core import efactura_import as efi
from core import spv_receive as rcv

CIF_TENANT = "14399840"   # tenant_002 (DANTE) - controlat direct (param al importa_mesaj)
PRIN = sc.principal_firm(1)


class _Resp:
    def __init__(self, content=b"zip", status=200):
        self.content = content; self.status_code = status


def _stat():
    return {"ciorna": 0, "descarcata": 0, "deja": 0, "scurgere_evitata": 0,
            "skip_auth": 0, "descarca_esec": 0, "fara_xml": 0, "tenanti_fara_cif": 0}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture(autouse=True)
def _mock_retea(monkeypatch):
    # descarca -> ZIP fake; extrage_fisiere -> un XML; nu atingem ANAF
    monkeypatch.setattr(efs, "descarca", lambda p, i, m: _Resp())
    monkeypatch.setattr(efi, "extrage_fisiere", lambda nume, cont: [("f.xml", b"<Invoice/>")])
    yield


@pytest.fixture
def curata():
    ids = []
    yield ids
    with _db.get_conn() as c:
        with c.cursor() as cur:
            for i in ids:
                cur.execute("DELETE FROM tenant_002.efactura_primite WHERE id_mesaj_anaf=%s", (i,))


def _rand(id_mesaj):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT status, cif_beneficiar, cif_emitent, factura_id "
                        "FROM tenant_002.efactura_primite WHERE id_mesaj_anaf=%s", (id_mesaj,))
            return cur.fetchone()


def test_anti_scurgere_cif_beneficiar_gresit(curata, monkeypatch):
    monkeypatch.setattr(efi, "parseaza_xml", lambda x, c: None)
    st = _stat()
    msg = {"id": "MSGX1", "cif_beneficiar": "99999999", "cif_emitent": "111"}  # NU e tenantul
    rcv.importa_mesaj("tenant_002", PRIN, CIF_TENANT, msg, st)
    curata.append("MSGX1")
    assert st["scurgere_evitata"] == 1
    assert _rand("MSGX1") is None   # NU s-a importat (scurgere evitata la insert)


def test_import_ciorna_daca_parsabila(curata, monkeypatch):
    monkeypatch.setattr(efi, "parseaza_xml", lambda x, c: {"numar": "F1"})   # parsabila
    st = _stat()
    msg = {"id": "MSGX2", "cif_beneficiar": CIF_TENANT, "cif_emitent": "RO111", "id_solicitare": "S1", "tip": "FACTURA PRIMITA"}
    rcv.importa_mesaj("tenant_002", PRIN, CIF_TENANT, msg, st)
    curata.append("MSGX2")
    r = _rand("MSGX2")
    assert r and r[0] == "ciorna" and r[1] == CIF_TENANT and r[3] is None   # factura_id NULL (four-eyes)
    assert st["ciorna"] == 1


def test_descarcata_daca_neparsabila(curata, monkeypatch):
    def _cade(x, c): raise ValueError("XML invalid")
    monkeypatch.setattr(efi, "parseaza_xml", _cade)
    st = _stat()
    msg = {"id": "MSGX3", "cif_beneficiar": CIF_TENANT, "cif_emitent": "222"}
    rcv.importa_mesaj("tenant_002", PRIN, CIF_TENANT, msg, st)
    curata.append("MSGX3")
    assert _rand("MSGX3")[0] == "descarcata"   # fallback, nu ciorna
    assert st["descarcata"] == 1


def test_dedup_nu_reimporta(curata, monkeypatch):
    monkeypatch.setattr(efi, "parseaza_xml", lambda x, c: None)
    st = _stat()
    msg = {"id": "MSGX4", "cif_beneficiar": CIF_TENANT, "cif_emitent": "333"}
    rcv.importa_mesaj("tenant_002", PRIN, CIF_TENANT, msg, st)
    rcv.importa_mesaj("tenant_002", PRIN, CIF_TENANT, msg, st)   # a 2-a oara
    curata.append("MSGX4")
    assert st["ciorna"] == 1 and st["deja"] == 1
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM tenant_002.efactura_primite WHERE id_mesaj_anaf='MSGX4'")
            assert cur.fetchone()[0] == 1   # un singur rand (dedup)
