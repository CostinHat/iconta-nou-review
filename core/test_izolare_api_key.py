# -*- coding: utf-8 -*-
"""core/test_izolare_api_key.py — GARD de izolare pe CHEIE API (namespace /api/v1/firme/{tenant_id}).

Gardul structural (test_izolare_structurala) probeaza rutele {tenant_id} cu token Bearer. Rutele
/api/v1/firme/{tenant_id}/* NU folosesc Bearer, ci X-Api-Key (cere_api_key -> firm_id). Probate cu
Bearer, ele raspund 401 (lipsa X-Api-Key) -> gardul structural le vede "izolate" FARA sa exercite
vreodata calea cheii API. Punct orb: o ruta /api/v1/firme/{tenant_id}/X noua care uita chokepoint-ul
_api_schema(actx, tenant_id) ar trece fals-verde la Bearer, dar o cheie a firmei A ar citi firma B.

Acest gard inchide punctul orb: enumeram DINAMIC rutele /api/v1/firme/{tenant_id}/* din main.app.routes
(nu lista hardcodata) si probam cu cheia firmei A pe tenantul firmei B -> niciodata 2xx, niciodata
sentinela firmei B. Control pozitiv: cheia firmei A pe tenantul firmei A -> 2xx cu datele A (altfel un
404 uniform ar trece gardul degeaba). O ruta noua {tenant_id} sub /api/v1 fara _api_schema intra
automat in enumerare si PICA testul.

Siguranta probelor: acelasi tipar ca gardul structural - firma/tenant/cheie/schema efemere pe o
conexiune din pool, db.get_conn monkeypatch-uit la un proxy cu SAVEPOINT (nicio persistare in public),
schemele sterse + rollback la final. Fara poluare.
"""
import contextlib
import hashlib
import re
import secrets
import pytest

from core import db as _db, tenant_provisioning as _tp

SCH_A, SCH_B = "ztest_apik_a", "ztest_apik_b"


class _ConnProxy:
    """commit/rollback = no-op; izolarea o face SAVEPOINT-ul din _fake (ca la gardul structural)."""
    def __init__(self, real):
        object.__setattr__(self, "_real", real)
    def __getattr__(self, n):
        return getattr(self._real, n)
    def commit(self):
        pass
    def rollback(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _seed(cur, schema, nume, factura_nr):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
    cur.execute('SET search_path TO "%s", public' % schema)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont) "
                "VALUES (1,%s,'14399840','Str 1','Buc','B','6202',true,'L')", (nume,))
    cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva) "
                "VALUES (%s,'2026-06-10','emisa','RO14399840','CLIENT',1210,210)", (factura_nr,))
    cur.execute("SET search_path TO public")


def _rute_apiv1():
    """TOATE (ruta, metoda) sub /api/v1/firme/{tenant_id} din app (nu hardcodat) -> prinde rute noi."""
    import main
    out = set()
    for r in main.app.routes:
        p = getattr(r, "path", "")
        if p.startswith("/api/v1/firme/{tenant_id}"):
            for m in (getattr(r, "methods", set()) or set()):
                if m in ("GET", "POST", "PUT", "DELETE"):
                    out.add((p, m))
    return sorted(out)


def _fill(path, tid):
    return re.sub(r"{(\w+)}", lambda mm: str(tid) if mm.group(1) == "tenant_id" else "1", path)


@pytest.fixture
def env(monkeypatch):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST APIK A') RETURNING id")
            firmA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST APIK B') RETURNING id")
            firmB = cur.fetchone()[0]
            _seed(cur, SCH_A, "TENANT APIK A SRL", "APIKA-100")
            _seed(cur, SCH_B, "TENANT APIK B SRL", "APIKB-200")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT APIK A','14399840',%s,true) RETURNING id", (SCH_A, firmA))
            tA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT APIK B','14399840',%s,true) RETURNING id", (SCH_B, firmB))
            tB = cur.fetchone()[0]
            # Inseram cheia API MANUAL (acelasi format ca api_public.genereaza: ick_ + sha256 stocat).
            # NU folosim api_public.genereaza pentru ca acela face conn.commit() pe conexiunea reala ->
            # ar persista firmele/schemele efemere in public (poluare). Aici totul ramane in tranzactia
            # efemera, anulata la rollback-ul din finally.
            def _mk_key(firm):
                k = "ick_" + secrets.token_urlsafe(32)
                cur.execute("INSERT INTO public.api_chei (accounting_firm_id,cheie_hash,prefix,nume) "
                            "VALUES (%s,%s,%s,'ztest')",
                            (firm, hashlib.sha256(k.encode()).hexdigest(), k[:12]))
                return k
            cheieA = _mk_key(firmA)
            cheieB = _mk_key(firmB)

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
                c.execute("SAVEPOINT probe_sp")
            try:
                yield _ConnProxy(conn)
            finally:
                with conn.cursor() as c:
                    try:
                        c.execute("ROLLBACK TO SAVEPOINT probe_sp"); c.execute("RELEASE SAVEPOINT probe_sp")
                    except Exception:
                        pass
        monkeypatch.setattr(_db, "get_conn", _fake)

        yield {"tA": tA, "tB": tB, "cheieA": cheieA, "cheieB": cheieB}
    finally:
        with conn.cursor() as c:
            for s in (SCH_A, SCH_B):
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % s)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_control_pozitiv_cheia_A_isi_vede_tenantul(env):
    """Fara control pozitiv, un 404 uniform ar trece gardul degeaba: cheia A CITESTE tenantul A."""
    cl = _client()
    r = cl.get(_fill("/api/v1/firme/{tenant_id}/facturi", env["tA"]) + "?an=2026&luna=6",
               headers={"X-Api-Key": env["cheieA"]})
    assert r.status_code == 200, "control pozitiv rupt: %d %s" % (r.status_code, r.text[:200])
    assert "APIKA-100" in r.text, "cheia A nu-si vede propria factura"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cheia_A_nu_atinge_tenantul_B(env):
    """Pe TOATE (ruta,metoda) /api/v1/firme/{tenant_id}: cheia A pe tenantul B -> niciodata 2xx,
    niciodata sentinela B. O ruta noua fara _api_schema(actx, tenant_id) pica aici."""
    cl = _client()
    perechi = _rute_apiv1()
    assert len(perechi) >= 3, "gard gol? doar %d rute /api/v1/firme/{tenant_id}" % len(perechi)
    H = {"X-Api-Key": env["cheieA"]}
    scapari = []
    for (p, m) in perechi:
        url = _fill(p, env["tB"]) + "?an=2026&luna=6"
        body = {} if m in ("POST", "PUT") else None
        r = cl.request(m, url, headers=H, json=body)
        if 200 <= r.status_code < 300:
            scapari.append("%s %s -> %d (2xx cross-firma: ruta nefiltrata pe cheie!)" % (m, url, r.status_code))
            continue
        if "APIKB-200" in r.text or "TENANT APIK B" in r.text:
            scapari.append("%s %s -> sentinela B (SCURGERE)" % (m, url))
    assert not scapari, "IZOLARE CHEIE API (%d/%d): %s" % (len(scapari), len(perechi), scapari)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_cheie_401(env):
    """Fara X-Api-Key -> 401, niciodata date."""
    cl = _client()
    r = cl.get(_fill("/api/v1/firme/{tenant_id}/facturi", env["tA"]))
    assert r.status_code == 401
