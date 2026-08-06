# -*- coding: utf-8 -*-
"""core/test_izolare_structurala.py — GARD STRUCTURAL de izolare (C-5 P1, clasele 5+6).

Izolarea (tenant + cross-cabinet) NU are mesaj conform cap.6: comportamentul CORECT e 404 TĂCUT
(un mesaj care ar explica "de ce" = scurgere de informatie). Deci aici NU se cataloghează un mesaj,
se PROBEAZĂ că izolarea ȚINE, pentru toate cele patru principii de acces, pe TOATE rutele {tenant_id}.

Chokepoint unic: auth_api.schema_tenant(conn, user_id, tenant_id) -> None daca userul n-are acces:
  - superadmin: DOAR tenanti fara cabinet (accounting_firm_id IS NULL);
  - admin_firma: DOAR firmele cabinetului lui;
  - angajat/client: DOAR prin user_tenants.
Ruta care rezolva tenantul fara acest chokepoint = scurgere.

GARD STRUCTURAL: enumeram rutele GET {tenant_id} DIN main.app.routes (nu listă hardcodată) și
probăm cross-acces pentru fiecare principiu -> niciodată 2xx, niciodată sentinela tenantului interzis.
O RUTĂ NOUĂ {tenant_id} fără filtrare pe tenant intră automat în probă și PICĂ testul.

Scenarii (decizie Costin C-5): (1) cabinet B cere resurse cabinet A; (2) asistent cu firme parțial
atribuite cere firmă neatribuită; (3) client de portal cere altă firmă; (4) superadmin cere tenant.
"""
import contextlib
import re
import pytest

from core import db as _db, tenant_provisioning as _tp, auth_api

SCH_A, SCH_B, SCH_C = "ztest_izs_a", "ztest_izs_b", "ztest_izs_c"


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
            adminB = _user(cur, "izs_admin_b@invalid", "admin_firma", firmB)
            asistentA = _user(cur, "izs_asist_a@invalid", "angajat", firmA)   # cabinet A, atribuit doar tA
            clientA = _user(cur, "izs_client_a@invalid", "client", firmA)     # client, portal, doar tA
            superad = _user(cur, "izs_super@invalid", "superadmin", None)     # fara cabinet
            fidA, sidA = _seed_schema(cur, SCH_A, "TENANT A SRL", "A-100", "SALARIAT A")
            fidB, sidB = _seed_schema(cur, SCH_B, "TENANT B SRL", "B-200", "SALARIAT B")
            fidC, sidC = _seed_schema(cur, SCH_C, "TENANT C SRL", "C-300", "SALARIAT C")
            cur.execute("SET search_path TO public")
            tA = _tenant_row(cur, SCH_A, "TENANT A", firmA)
            tB = _tenant_row(cur, SCH_B, "TENANT B", firmB)
            tC = _tenant_row(cur, SCH_C, "TENANT C", firmA)   # cabinet A, dar NEATRIBUIT asistentului/clientului
            # atribuiri partiale: asistentA si clientA vad DOAR tA (nu tC, nu tB)
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (asistentA, tA))
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (clientA, tA))

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield conn
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


def _rute_get_tenant():
    """TOATE rutele GET cu {tenant_id} din app (nu hardcodat) -> gardul prinde rute noi."""
    import main
    out = set()
    for r in main.app.routes:
        p = getattr(r, "path", "")
        m = getattr(r, "methods", set()) or set()
        if "{tenant_id}" in p and "GET" in m:
            out.add(p)
    return sorted(out)


def _fill(path, tid, ctx):
    def repl(mm):
        name = mm.group(1)
        return str(tid) if name == "tenant_id" else str(ctx.get(name, 1))
    return re.sub(r"{(\w+)}", repl, path)


# [FINDING C-5 P1, semnalat pt decizia Costin] Rute {tenant_id} care raspund 2xx cross-tenant DAR
# NU scurg date de tenant: intorc o constanta GLOBALA, iar tenant_id e DECORATIV (nu trec prin
# schema_tenant, doar cere_cabinet). Inconsistenta structurala (nu breach de date): fix posibil =
# adauga schema_tenant SAU muta in afara namespace-ului /tenants/. NU se repara aici (catalog intai,
# rescriere = campanie separata). Orice rută 2xx cross-tenant care NU e aici -> gardul PICĂ.
_EXCEPTAT_GLOBAL_NON_TENANT = {
    "/tenants/{tenant_id}/contracte/marcaje",   # intoarce _ct.MARCAJE (nomenclator static de marcaje contract)
}


def _probe_refuz(cl, token, tid_interzis, sentinele, ctx=None):
    """Pe TOATE rutele GET {tenant_id}: acces la tid_interzis -> niciodată 2xx (excepțiile globale
    documentate: nu 2xx-strict, dar OBLIGATORIU fără sentinela tenantului). Sentinela = date scurse."""
    ctx = ctx or {}
    H = {"Authorization": "Bearer " + token}
    rute = _rute_get_tenant()
    assert len(rute) >= 50, "gard gol? doar %d rute {tenant_id} enumerate" % len(rute)
    # excepțiile trebuie să existe încă în rute (altfel sunt stale -> de curățat)
    assert _EXCEPTAT_GLOBAL_NON_TENANT <= set(rute), (
        "excepții globale stale (nu mai sunt rute): %s" % (_EXCEPTAT_GLOBAL_NON_TENANT - set(rute)))
    scapari = []
    for p in rute:
        url = _fill(p, tid_interzis, ctx)
        try:
            r = cl.get(url, headers=H)
        except Exception as e:
            scapari.append("%s -> EXCEPTIE %s" % (url, type(e).__name__)); continue
        exceptat = p in _EXCEPTAT_GLOBAL_NON_TENANT
        if (200 <= r.status_code < 300) and not exceptat:
            scapari.append("%s -> %d (rută {tenant_id} nouă fără filtrare pe tenant?)" % (url, r.status_code))
            continue
        # chiar și excepția globală nu are voie să întoarcă DATE de tenant
        for s in sentinele:
            if s in r.text:
                scapari.append("%s -> sentinela %r in raspuns (SCURGERE DE DATE)" % (url, s))
    assert not scapari, "IZOLARE (%d din %d rute): %s" % (len(scapari), len(rute), scapari[:12])
    return len(rute)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_control_pozitiv_adminA_isi_vede_tenantul(env):
    """Fără control pozitiv, un 404 uniform ar trece gardul degeaba: adminA CITEȘTE tA."""
    cl = _client()
    r = cl.get("/tenants/%d/facturi" % env["tA"], headers={"Authorization": "Bearer " + env["tok_adminA"]})
    assert r.status_code == 200 and "A-100" in r.text, "propriul tenant blocat: %d %s" % (r.status_code, r.text[:200])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_cross_cabinet_adminB_nu_vede_A_si_invers(env):
    """(1) admin_firma dintr-un cabinet NU vede tenantul altui cabinet, pe nicio rută GET {tenant_id}."""
    cl = _client()
    n = _probe_refuz(cl, env["tok_adminA"], env["tB"], ["TENANT B", "B-200", "SALARIAT B"],
                     ctx={"factura_id": env["fidB"], "salariat_id": env["sidB"]})
    assert n >= 50


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_asistent_firma_neatribuita(env):
    """(2) asistent (angajat) atribuit DOAR tA nu vede tC (același cabinet, neatribuit) și nici tB."""
    cl = _client()
    _probe_refuz(cl, env["tok_asistentA"], env["tC"], ["TENANT C", "C-300", "SALARIAT C"])
    _probe_refuz(cl, env["tok_asistentA"], env["tB"], ["TENANT B", "B-200", "SALARIAT B"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_client_portal_alta_firma(env):
    """(3) client de portal atribuit tA nu vede altă firmă (tB)."""
    cl = _client()
    _probe_refuz(cl, env["tok_clientA"], env["tB"], ["TENANT B", "B-200", "SALARIAT B"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_izolare_superadmin_nu_vede_tenant_cu_cabinet(env):
    """(4) superadmin (id GDPR) vede DOAR conturi fără cabinet -> nu vede tA (are cabinet)."""
    cl = _client()
    _probe_refuz(cl, env["tok_super"], env["tA"], ["TENANT A", "A-100", "SALARIAT A"],
                 ctx={"factura_id": env["fidA"], "salariat_id": env["sidA"]})


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_gard_enumera_rute_netrivial(env):
    """Meta-gard: setul de rute {tenant_id} enumerate e netrivial (altfel probele trec pe gol)."""
    assert len(_rute_get_tenant()) >= 50
