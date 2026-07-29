# -*- coding: utf-8 -*-
"""
Teste core/spv_receive.py (F179) — pe MOCK (retea + parser), niciodata pe ANAF real.

Apara cele 3 garduri: anti-scurgere (cif_beneficiar == CIF tenant la insert), dedup pe id_mesaj_anaf,
masina de stari (ciorna daca parsabila / descarcata fallback; NU creeaza cheltuiala - four-eyes).

IZOLARE (29.07.2026): NU mai depinde de tenant_002 persistent. Un test care depindea de o firma
din baza testa prezenta firmei, nu logica. importa_mesaj e SCRIITOR care isi deschide propria
conexiune si COMITE -> ROLLBACK-ul fixturii n-are ce anula (spre deosebire de pull() care primeste
conn si traieste in tranzactia fixturii). Deci: schema efemera COMISA din tenant_template + DROP la
teardown, cu DROP IF EXISTS la setup pentru siguranta la crash. Vezi DECIZII 29.07.
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
from core import tenant_provisioning as tp

CIF_TENANT = "14399840"
PRIN = sc.principal_firm(1)
SCHEMA_T = "ztest_spv"


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


@pytest.fixture
def schema():
    """Schema efemera COMISA din tenant_template + DROP la teardown. importa_mesaj isi deschide
    propria conexiune si comite -> schema trebuie sa fie VIZIBILA (comisa), nu in tranzactia noastra."""
    _db.init_pool()
    with _db.get_conn() as conn:          # get_conn comite la iesirea din bloc -> schema devine vizibila
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
            cur.execute(tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
    yield SCHEMA_T
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)


@pytest.fixture(autouse=True)
def _mock_retea(monkeypatch):
    monkeypatch.setattr(efs, "descarca", lambda p, i, m: _Resp())
    monkeypatch.setattr(efi, "extrage_fisiere", lambda nume, cont: [("f.xml", b"<Invoice/>")])
    yield


def _rand(schema, id_mesaj):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"SELECT status, cif_beneficiar, cif_emitent, factura_id "
                        f"FROM {schema}.efactura_primite WHERE id_mesaj_anaf=%s", (id_mesaj,))
            return cur.fetchone()


def test_anti_scurgere_cif_beneficiar_gresit(schema, monkeypatch):
    monkeypatch.setattr(efi, "parseaza_xml", lambda x, c: None)
    st = _stat()
    msg = {"id": "MSGX1", "cif_beneficiar": "99999999", "cif_emitent": "111"}  # NU e tenantul
    rcv.importa_mesaj(schema, PRIN, CIF_TENANT, msg, st)
    assert st["scurgere_evitata"] == 1
    assert _rand(schema, "MSGX1") is None   # NU s-a importat (scurgere evitata la insert)


def test_import_ciorna_daca_parsabila(schema, monkeypatch):
    monkeypatch.setattr(efi, "parseaza_xml", lambda x, c: {"numar": "F1"})   # parsabila
    st = _stat()
    msg = {"id": "MSGX2", "cif_beneficiar": CIF_TENANT, "cif_emitent": "RO111", "id_solicitare": "S1", "tip": "FACTURA PRIMITA"}
    rcv.importa_mesaj(schema, PRIN, CIF_TENANT, msg, st)
    r = _rand(schema, "MSGX2")
    assert r and r[0] == "ciorna" and r[1] == CIF_TENANT and r[3] is None   # factura_id NULL (four-eyes)
    assert st["ciorna"] == 1


def test_descarcata_daca_neparsabila(schema, monkeypatch):
    def _cade(x, c): raise ValueError("XML invalid")
    monkeypatch.setattr(efi, "parseaza_xml", _cade)
    st = _stat()
    msg = {"id": "MSGX3", "cif_beneficiar": CIF_TENANT, "cif_emitent": "222"}
    rcv.importa_mesaj(schema, PRIN, CIF_TENANT, msg, st)
    assert _rand(schema, "MSGX3")[0] == "descarcata"   # fallback, nu ciorna
    assert st["descarcata"] == 1


def test_dedup_nu_reimporta(schema, monkeypatch):
    monkeypatch.setattr(efi, "parseaza_xml", lambda x, c: None)
    st = _stat()
    msg = {"id": "MSGX4", "cif_beneficiar": CIF_TENANT, "cif_emitent": "333"}
    rcv.importa_mesaj(schema, PRIN, CIF_TENANT, msg, st)
    rcv.importa_mesaj(schema, PRIN, CIF_TENANT, msg, st)   # a 2-a oara
    assert st["ciorna"] == 1 and st["deja"] == 1
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM {schema}.efactura_primite WHERE id_mesaj_anaf='MSGX4'")
            assert cur.fetchone()[0] == 1   # un singur rand (dedup)
