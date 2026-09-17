# -*- coding: utf-8 -*-
"""[B1–B4, 17.09.2026] Apartenența pe OBIECT — un cabinet nu lucrează pe elementul altui cabinet.

Constatarea B1: `/coada/{id}/aproba|respinge|depune` nu comparau `declaratii_coada.cabinet_id` cu
`ctx["firm"]` — doar `_are_permisiune` (dreptul apelantului). Un cabinet aproba, respingea și marca
„depusă" declarația altuia, scriind în `declaratii_depuse` al firmei celuilalt.

Proba: element în coada cabinetului B; cabinetul A (cu drepturi depline la EL) încearcă acțiuni →
404, iar starea și `declaratii_depuse` ale lui B rămân neatinse. PICA pe codul de dinainte (unde A
reușea), TRECE după. Scrisă de la caz în jos: aprobarea din alt cabinet până în declaratii_depuse.
"""
from __future__ import annotations

import contextlib
import json

import pytest

from core import auth_api
from core import db as _db

SCH_B = "ztest_b1_firmab"


class _ConnProxy:
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


@pytest.fixture
def doua_cabinete(monkeypatch):
    """Cabinet A (atacatorul, drepturi depline) + cabinet B cu un element în coadă (stare la_senior)."""
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            # Cabinet A + admin cu toate drepturile
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT A1-A') RETURNING id")
            firm_a = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ,poate_pregati,poate_valida,poate_depune) VALUES "
                        "('zt_b1_a@invalid','x','A','A','admin_firma',%s,true,true,true,true) RETURNING id",
                        (firm_a,))
            uid_a = cur.fetchone()[0]
            # Cabinet B + tenant + un element de coadă al lui B
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT A1-B') RETURNING id")
            firm_b = cur.fetchone()[0]
            # un senior al lui B, care a creat elementul (FK declaratii_coada.creat_de_id -> users.id)
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('zt_b1_seniorb@invalid','x','S','B','admin_firma',%s,true) RETURNING id",
                        (firm_b,))
            uid_b = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH_B)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH_B))
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT B','14399840',%s,true) RETURNING id", (SCH_B, firm_b))
            tid_b = cur.fetchone()[0]
            payload = json.dumps({"xml": "<x/>", "_an": 2026, "_luna": 8})
            # fixtura-sintetica-ok: element de coadă efemer al cabinetului B (firmă + schemă create
            # ad-hoc, șterse în teardown); cabinet_id-ul e al unei firme sintetice, deci nu se poate
            # ciocni de PK-ul unei depuneri reale (bug 22.07).
            cur.execute(
                "INSERT INTO public.declaratii_coada "
                "(cabinet_id, tenant_id, tip, perioada, stare, payload, creat_de, creat_de_id) "
                "VALUES (%s,%s,'d300','2026-08','la_senior',%s::jsonb,'seniorB',%s) RETURNING id",
                (firm_b, tid_b, payload, uid_b))
            coada_id = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"conn": conn, "firm_a": firm_a, "tid_b": tid_b, "coada_id": coada_id,
               "tok_a": auth_api.emite_token({"id": uid_a, "rol": "admin_firma",
                                              "accounting_firm_id": firm_a})}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH_B)
            c.execute("DELETE FROM public.declaratii_coada WHERE cabinet_id IN "
                      "(SELECT id FROM public.accounting_firms WHERE nume IN ('ZT A1-A','ZT A1-B'))")
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(tok):
    return {"Authorization": "Bearer " + tok}


def _stare(env):
    with env["conn"].cursor() as cur:
        cur.execute("SET search_path TO public")
        cur.execute("SELECT stare FROM public.declaratii_coada WHERE id=%s", (env["coada_id"],))
        return cur.fetchone()[0]


def _depuse_pentru_b(env):
    with env["conn"].cursor() as cur:
        cur.execute("SET search_path TO public")
        cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id=%s", (env["tid_b"],))
        return cur.fetchone()[0]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_alt_cabinet_nu_aproba(doua_cabinete):
    cl = _client()
    r = cl.post("/coada/%d/aproba" % doua_cabinete["coada_id"], headers=_H(doua_cabinete["tok_a"]),
                json={"motiv_trecere": "audit"})
    assert r.status_code == 404, "cabinet A a putut aproba elementul lui B: %s %s" % (r.status_code, r.text)
    assert _stare(doua_cabinete) == "la_senior", "starea elementului lui B s-a schimbat"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_alt_cabinet_nu_respinge(doua_cabinete):
    cl = _client()
    r = cl.post("/coada/%d/respinge" % doua_cabinete["coada_id"], headers=_H(doua_cabinete["tok_a"]),
                json={"motiv": "audit"})
    assert r.status_code == 404, "cabinet A a putut respinge elementul lui B: %s %s" % (r.status_code, r.text)
    assert _stare(doua_cabinete) == "la_senior"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_alt_cabinet_nu_depune_in_declaratii_depuse_ale_lui_b(doua_cabinete):
    cl = _client()
    r = cl.post("/coada/%d/depune" % doua_cabinete["coada_id"], headers=_H(doua_cabinete["tok_a"]),
                json={"confirmari": [], "motiv_trecere": "audit"})
    assert r.status_code == 404, "cabinet A a putut depune elementul lui B: %s %s" % (r.status_code, r.text)
    assert _depuse_pentru_b(doua_cabinete) == 0, "s-a scris în declaratii_depuse al firmei B"
    assert _stare(doua_cabinete) == "la_senior"
