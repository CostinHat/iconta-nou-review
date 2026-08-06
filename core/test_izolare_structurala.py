# -*- coding: utf-8 -*-
"""core/test_izolare_structurala.py — GARD STRUCTURAL de izolare (C-5 P1, clasele 5+6).

Izolarea (tenant + cross-cabinet) NU are mesaj conform cap.6: comportamentul CORECT e 404 TĂCUT
(un mesaj care ar explica "de ce" = scurgere de informatie). Deci NU se cataloghează un mesaj,
se PROBEAZĂ că izolarea ȚINE, pentru toate cele patru principii de acces, pe TOATE rutele {tenant_id}
și pe TOATE metodele (GET + POST/PUT/DELETE — scrierea cross-tenant e mai gravă decât citirea).

Chokepoint unic: auth_api.schema_tenant(conn, user_id, tenant_id) -> None dacă userul n-are acces:
  - superadmin: DOAR tenanti fără cabinet (accounting_firm_id IS NULL);
  - admin_firma: DOAR firmele cabinetului lui;
  - angajat/client: DOAR prin user_tenants.
Ruta care rezolvă tenantul fără acest chokepoint = scurgere.

GARD STRUCTURAL: enumeram DINAMIC (rută,metodă) cu {tenant_id} DIN main.app.routes (nu listă
hardcodată) și probăm cross-acces pentru fiecare principiu -> niciodată 2xx, niciodată sentinela
tenantului interzis. O RUTĂ NOUĂ {tenant_id} fără filtrare pe tenant intră automat și PICĂ testul.

Siguranța probelor de SCRIERE: conn.commit e neutralizat (nicio persistare în public) + SAVEPOINT
per request (rollback la savepoint după fiecare cerere -> anulează orice scriere ȘI recuperează dintr-o
tranzacție abortată). Fără poluare, fără cascadă de aborturi.
"""
import contextlib
import re
import pytest

from core import db as _db, tenant_provisioning as _tp, auth_api

SCH_A, SCH_B, SCH_C = "ztest_izs_a", "ztest_izs_b", "ztest_izs_c"
_METODE = ("GET", "POST", "PUT", "DELETE")


class _ConnProxy:
    """Proxy peste conn: commit/rollback = no-op (izolarea o face SAVEPOINT-ul din _fake).
    psycopg2 connection.commit e read-only -> nu poate fi monkeypatch-uit direct."""
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


def _seed_schema(cur, schema, nume, factura_nr, salariat_nume):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
    cur.execute('SET search_path TO "%s", public' % schema)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont) "
                "VALUES (1,%s,'14399840','Str 1','Buc','B','6202',true,'L')", (nume,))
    cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva) "
                "VALUES (%s,'2026-06-10','emisa','RO14399840','CLIENT',1210,210) RETURNING id", (factura_nr,))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO salariati (nume,prenume,cnp) VALUES (%s,'Ion','1960101221144') RETURNING id",
                (salariat_nume,))
    sid = cur.fetchone()[0]
    return fid, sid


def _user(cur, email, rol, firm):
    cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                "VALUES (%s,'x','N','N',%s,%s,true) RETURNING id", (email, rol, firm))
    return cur.fetchone()[0]


def _tenant_row(cur, schema, nume, firm):
    cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                "VALUES (%s,%s,'14399840',%s,true) RETURNING id", (schema, nume, firm))
    return cur.fetchone()[0]


@pytest.fixture
def env(monkeypatch):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST PRISMA') RETURNING id")
            firmA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST NEXUS') RETURNING id")
            firmB = cur.fetchone()[0]
            adminA = _user(cur, "izs_admin_a@invalid", "admin_firma", firmA)
            _user(cur, "izs_admin_b@invalid", "admin_firma", firmB)
            asistentA = _user(cur, "izs_asist_a@invalid", "angajat", firmA)
            clientA = _user(cur, "izs_client_a@invalid", "client", firmA)
            superad = _user(cur, "izs_super@invalid", "superadmin", None)
            fidA, sidA = _seed_schema(cur, SCH_A, "TENANT A SRL", "A-100", "SALARIAT A")
            fidB, sidB = _seed_schema(cur, SCH_B, "TENANT B SRL", "B-200", "SALARIAT B")
            _seed_schema(cur, SCH_C, "TENANT C SRL", "C-300", "SALARIAT C")
            cur.execute("SET search_path TO public")
            tA = _tenant_row(cur, SCH_A, "TENANT A", firmA)
            tB = _tenant_row(cur, SCH_B, "TENANT B", firmB)
            tC = _tenant_row(cur, SCH_C, "TENANT C", firmA)   # cabinet A, dar NEATRIBUIT asistentului/clientului
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (asistentA, tA))
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (clientA, tA))

        # niciun request nu persistă (anti-poluare public); scrierile se anulează la savepoint
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

        def tok(uid, rol, firm):
            return auth_api.emite_token({"id": uid, "rol": rol, "accounting_firm_id": firm})
        yield {
            "tA": tA, "tB": tB, "tC": tC, "fidA": fidA, "sidA": sidA, "fidB": fidB, "sidB": sidB,
            "tok_adminA": tok(adminA, "admin_firma", firmA),
            "tok_asistentA": tok(asistentA, "angajat", firmA),
            "tok_clientA": tok(clientA, "client", firmA),
            "tok_super": tok(superad, "superadmin", None),
        }
    finally:
        with conn.cursor() as c:
            for s in (SCH_A, SCH_B, SCH_C):
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % s)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _rute_tenant(metode=_METODE):
    """TOATE perechile (rută, metodă) cu {tenant_id} din app (nu hardcodat) -> prinde rute noi."""
    import main
    out = set()
    for r in main.app.routes:
        p = getattr(r, "path", "")
        ms = getattr(r, "methods", set()) or set()
        if "{tenant_id}" in p:
            for m in ms:
                if m in metode:
                    out.add((p, m))
    return sorted(out)


def _fill(path, tid, ctx):
    def repl(mm):
        name = mm.group(1)
        return str(tid) if name == "tenant_id" else str(ctx.get(name, 1))
    return re.sub(r"{(\w+)}", repl, path)


def _probe_refuz(cl, token, tid_interzis, sentinele, ctx=None):
    """Pe TOATE (rută,metodă) {tenant_id}: acces la tid_interzis -> niciodată 2xx, niciodată sentinela.
    POST/PUT trimit corp gol; izolarea corectă refuză (403/404) ÎNAINTE de orice scriere."""
    ctx = ctx or {}
    H = {"Authorization": "Bearer " + token}
    perechi = _rute_tenant()
    assert len(perechi) >= 150, "gard gol? doar %d (rută,metodă) {tenant_id}" % len(perechi)
    scapari = []
    for (p, m) in perechi:
        url = _fill(p, tid_interzis, ctx)
        body = {} if m in ("POST", "PUT") else None
        try:
            r = cl.request(m, url, headers=H, json=body)
        except Exception as e:
            scapari.append("%s %s -> EXCEPTIE %s" % (m, url, type(e).__name__)); continue
        if 200 <= r.status_code < 300:
            scapari.append("%s %s -> %d (2xx cross-tenant: rută nefiltrată pe tenant!)" % (m, url, r.status_code))
            continue
        for s in sentinele:
            if s in r.text:
                scapari.append("%s %s -> sentinela %r (SCURGERE DE DATE)" % (m, url, s))
    assert not scapari, "IZOLARE (%d din %d rute×metodă): %s" % (len(scapari), len(perechi), scapari[:15])
    return len(perechi)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_control_pozitiv_adminA_isi_vede_tenantul(env):
    """Fără control pozitiv, un 404 uniform ar trece gardul degeaba: adminA CITEȘTE tA."""
    cl = _client()
    r = cl.get("/tenants/%d/facturi" % env["tA"], headers={"Authorization": "Bearer " + env["tok_adminA"]})
    assert r.status_code == 200 and "A-100" in r.text, "propriul tenant blocat: %d %s" % (r.status_code, r.text[:200])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_cross_cabinet_admin(env):
    """(1) admin_firma dintr-un cabinet NU vede/scrie tenantul altui cabinet, pe nicio rută {tenant_id}."""
    cl = _client()
    n = _probe_refuz(cl, env["tok_adminA"], env["tB"], ["TENANT B", "B-200", "SALARIAT B"],
                     ctx={"factura_id": env["fidB"], "salariat_id": env["sidB"]})
    assert n >= 150


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_asistent_firma_neatribuita(env):
    """(2) asistent (angajat) atribuit DOAR tA nu vede/scrie tC (același cabinet, neatribuit) și nici tB."""
    cl = _client()
    _probe_refuz(cl, env["tok_asistentA"], env["tC"], ["TENANT C", "C-300", "SALARIAT C"])
    _probe_refuz(cl, env["tok_asistentA"], env["tB"], ["TENANT B", "B-200", "SALARIAT B"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_client_portal_alta_firma(env):
    """(3) client de portal atribuit tA nu vede/scrie altă firmă (tB)."""
    cl = _client()
    _probe_refuz(cl, env["tok_clientA"], env["tB"], ["TENANT B", "B-200", "SALARIAT B"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_superadmin_nu_vede_tenant_cu_cabinet(env):
    """(4) superadmin (GDPR) vede DOAR conturi fără cabinet -> nu vede/scrie tA (are cabinet)."""
    cl = _client()
    _probe_refuz(cl, env["tok_super"], env["tA"], ["TENANT A", "A-100", "SALARIAT A"],
                 ctx={"factura_id": env["fidA"], "salariat_id": env["sidA"]})


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_gard_enumera_rute_netrivial(env):
    """Meta-gard: setul (rută,metodă) {tenant_id} enumerat e netrivial (altfel probele trec pe gol)."""
    assert len(_rute_tenant()) >= 150
