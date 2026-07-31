# -*- coding: utf-8 -*-
"""Proba DINAMICA de izolare tenanti: acces incrucisat real prin HTTP.

Doi tenanti (A, B) cu date identice ca FORMA, distincte ca VALORI, sub cabinete diferite.
Autentificat ca admin_firma din cabinetul A, cere obiecte din tenantul B pe rute user-facing
reale (facturi, salariati, profil), prin ID din URL. Asteptare: 404, ZERO date din B.

Izolarea e centralizata in auth_api.schema_tenant(uid, tenant_id) -> None daca userul n-are
acces -> ruta 404. Acest test o EXERCITA end-to-end (nu clasificare statica de rute).

Mecanica: conn UNIC din pool, controlat manual (rollback la final, ZERO poluare public);
db.get_conn monkeypatch-uit sa-l intoarca, deci si rutele si setup-ul vad aceeasi tranzactie
necomisa. TestClient(app) fara lifespan."""
import contextlib
import pytest

from core import db as _db, tenant_provisioning as _tp, auth_api


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


SCH_A, SCH_B = "ztest_iso_a", "ztest_iso_b"


def _seed_schema(cur, schema, nume, factura_nr, salariat_nume):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
    cur.execute('SET search_path TO "%s", public' % schema)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont) "
                "VALUES (1,%s,'14399840','Str 1','Buc','B','6202',true,'L')", (nume,))
    cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva) "
                "VALUES (%s,'2026-06-10','emisa','RO14399840','CLIENT',1210,210) RETURNING id", (factura_nr,))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO salariati (nume,prenume,cnp) VALUES (%s,'Ion','1960101221144') RETURNING id", (salariat_nume,))
    sid = cur.fetchone()[0]
    return fid, sid


@pytest.fixture
def env(monkeypatch):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST FIRMA A') RETURNING id")
            firmA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST FIRMA B') RETURNING id")
            firmB = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ztest_iso_a@invalid','x','A','A','admin_firma',%s,true) RETURNING id", (firmA,))
            uidA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ztest_iso_b@invalid','x','B','B','admin_firma',%s,true) RETURNING id", (firmB,))
            uidB = cur.fetchone()[0]
            fidA, sidA = _seed_schema(cur, SCH_A, "TENANT A SRL", "A-100", "SALARIAT A")
            fidB, sidB = _seed_schema(cur, SCH_B, "TENANT B SRL", "B-200", "SALARIAT B")
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT A','14399840',%s,true) RETURNING id", (SCH_A, firmA))
            tA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT B','14399840',%s,true) RETURNING id", (SCH_B, firmB))
            tB = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield conn
        monkeypatch.setattr(_db, "get_conn", _fake)
        tokenA = auth_api.emite_token({"id": uidA, "rol": "admin_firma", "accounting_firm_id": firmA})
        yield {"tA": tA, "tB": tB, "fidA": fidA, "fidB": fidB, "sidA": sidA, "sidB": sidB, "token": tokenA}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH_A)
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH_B)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_acces_incrucisat_blocat_404_zero_date_B(env):
    cl = _client()
    H = {"Authorization": "Bearer " + env["token"]}
    tB, fidB, sidB = env["tB"], env["fidB"], env["sidB"]
    rute_B = [
        "/tenants/%d/facturi" % tB,
        "/tenants/%d/facturi/%d" % (tB, fidB),
        "/tenants/%d/salariati" % tB,
        "/tenants/%d/salariati/%d" % (tB, sidB),
        "/tenants/%d/firma-profil" % tB,
    ]
    for ruta in rute_B:
        r = cl.get(ruta, headers=H)
        assert r.status_code in (403, 404), "LEAK: %s -> %d (asteptat 404): %s" % (ruta, r.status_code, r.text[:200])
        assert "TENANT B" not in r.text and "B-200" not in r.text and "SALARIAT B" not in r.text, (
            "LEAK: %s a intors date din B: %s" % (ruta, r.text[:200]))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_control_pozitiv_propriul_tenant_merge(env):
    """Fara asta, un 404 uniform ar trece testul degeaba: userul A citeste PROPRIILE date."""
    cl = _client()
    H = {"Authorization": "Bearer " + env["token"]}
    r = cl.get("/tenants/%d/facturi" % env["tA"], headers=H)
    assert r.status_code == 200, "propriul tenant blocat: %d %s" % (r.status_code, r.text[:200])
    assert "A-100" in r.text, "propriile date lipsesc: %s" % r.text[:200]
