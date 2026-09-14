# -*- coding: utf-8 -*-
"""Ce FAC, de fapt, cheia de API și suspendarea unui cabinet — probate prin lanțul aplicației.

DE CE EXISTĂ. Auditul din 14.09.2026 a numărat 59 de rute fără nicio probă în suită, iar cele mai
grele două erau astea: `POST/DELETE /cabinet/api-chei` e **suprafață de autentificare** (emite și
revocă chei care ocolesc parola), iar `/admin/cabinete/{id}/suspenda` schimbă accesul unui cabinet
întreg. Pentru `POST /cabinet/api-chei` exista o probă cap-coadă în `frontend_test/`, dar acolo ruta
e ȚEAVĂ (de unde se ia o cheie pentru alte probe), nu SUBIECT — și fișierul nu e cules de pytest.

CE ÎNTREABĂ, și de ce așa: nu „ce cod HTTP întoarce ruta", ci **ce se schimbă în lume**. O cheie
emisă chiar deschide ușa; una revocată chiar o închide; una a altui cabinet nu se poate revoca; iar
suspendarea chiar oprește loginul. Un test care ar cere doar `200` ar trece și pe o rută care nu
face nimic.

CUM RĂMÂNE CURAT. Firme/useri/tenanți efemeri pe o conexiune din pool, `db.get_conn` înlocuit cu un
proxy al ACELEIAȘI conexiuni, totul anulat prin `rollback` la final. Spre deosebire de gărzile de
izolare, aici NU se pune savepoint per cerere: probele sunt lanțuri (creez o cheie, o folosesc, o
revoc), iar un savepoint per cerere ar șterge chiar efectul pe care îl măsor.
"""
from __future__ import annotations

import contextlib
import hashlib

import pytest

from core import auth_api
from core import db as _db

SCH = "ztest_chei_susp"


class _ConnProxy:
    """`commit` e no-op: scrierile rămân în tranzacția efemeră, anulată la final."""

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
def env(monkeypatch):
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST CHEI A') RETURNING id")
            firmA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST CHEI B') RETURNING id")
            firmB = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_chei_a@invalid','x','N','N','admin_firma',%s,true) RETURNING id",
                        (firmA,))
            adminA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_chei_b@invalid','x','N','N','admin_firma',%s,true) RETURNING id",
                        (firmB,))
            adminB = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_chei_ang@invalid','x','N','N','angajat',%s,true) RETURNING id",
                        (firmA,))
            angajatA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_chei_super@invalid','x','N','N','superadmin',NULL,true) RETURNING id")
            superad = cur.fetchone()[0]

            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,"
                        "tip_decont) VALUES (1,'TENANT CHEI A SRL','14399840','Str 1','Buc','B',"
                        "'6202',true,'L')")
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT CHEI A','14399840',%s,true) RETURNING id", (SCH, firmA))
            tA = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)

        def tok(uid, rol, firm):
            return auth_api.emite_token({"id": uid, "rol": rol, "accounting_firm_id": firm})

        yield {"firmA": firmA, "firmB": firmB, "tA": tA, "conn": conn,
               "tok_adminA": tok(adminA, "admin_firma", firmA),
               "tok_adminB": tok(adminB, "admin_firma", firmB),
               "tok_angajatA": tok(angajatA, "angajat", firmA),
               "tok_super": tok(superad, "superadmin", None)}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(t):
    return {"Authorization": "Bearer " + t}


def _cheie(cl, tok, nume="proba"):
    r = cl.post("/cabinet/api-chei", json={"nume": nume}, headers=_H(tok))
    assert r.status_code == 200, "emiterea cheii: %d %s" % (r.status_code, r.text[:200])
    return r.json()


# ── POST /cabinet/api-chei ───────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cheia_emisa_CHIAR_deschide_usa(env):
    """Efectul rutei, nu codul ei: cheia întoarsă autentifică pe `/api/v1/firme`.

    Cu martor: aceeași rută, cu o cheie inventată, răspunde 401 — altfel un `/api/v1/firme` care
    ar răspunde 200 oricui ar face proba să treacă degeaba."""
    cl = _client()
    k = _cheie(cl, env["tok_adminA"], "proba emitere")
    assert k["cheie"].startswith("ick_") and k["prefix"] == k["cheie"][:12]

    r = cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]})
    assert r.status_code == 200, "cheia emisă NU deschide API-ul: %d %s" % (r.status_code, r.text[:200])

    r0 = cl.get("/api/v1/firme", headers={"X-Api-Key": "ick_cheie-care-nu-exista"})
    assert r0.status_code == 401, ("martorul: o cheie inventată primește %d, deci proba de mai sus "
                                  "nu dovedea nimic" % r0.status_code)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cheia_se_arata_o_singura_data_si_se_stocheaza_HASHUITA(env):
    """A doua vedere a cheii nu există: lista dă prefixul, iar în baza de date stă doar amprenta."""
    cl = _client()
    k = _cheie(cl, env["tok_adminA"], "proba stocare")

    r = cl.get("/cabinet/api-chei", headers=_H(env["tok_adminA"]))
    assert r.status_code == 200
    chei = r.json()["chei"]
    mea = [c for c in chei if c["id"] == k["id"]]
    assert mea, "cheia emisă nu apare în listă"
    assert "cheie" not in mea[0], "lista întoarce cheia în clar — ea se vede o singură dată"
    assert k["cheie"] not in r.text, "valoarea cheii apare în răspunsul listei"

    with env["conn"].cursor() as cur:
        cur.execute("SELECT cheie_hash FROM public.api_chei WHERE id=%s", (k["id"],))
        stocat = cur.fetchone()[0]
    assert stocat == hashlib.sha256(k["cheie"].encode()).hexdigest(), "altceva decât sha256 stocat"
    assert stocat != k["cheie"], "cheia e stocată în clar"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cheia_fara_nume_e_refuzata_cu_motiv(env):
    """O cheie fără nume rămâne activă și nerecunoscibilă în listă — deci nerevocabilă."""
    cl = _client()
    r = cl.post("/cabinet/api-chei", json={}, headers=_H(env["tok_adminA"]))
    # 422, nu 400: `DateInvalide` e tradusa asa de harta unica din `main._COD_EROARE`. Proba scrie
    # codul pe care il DA contractul, nu pe cel pe care il credeam eu.
    assert r.status_code == 422, "corpul gol trece: %d %s" % (r.status_code, r.text[:200])
    assert "nume" in r.text.lower(), "refuzul nu spune CE lipsește: %s" % r.text[:200]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_doua_chei_emise_sunt_diferite(env):
    cl = _client()
    a = _cheie(cl, env["tok_adminA"], "prima")
    b = _cheie(cl, env["tok_adminA"], "a doua")
    assert a["cheie"] != b["cheie"] and a["id"] != b["id"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_emiterea_cere_rolul_de_admin_de_cabinet(env):
    """Un angajat al ACELUIAȘI cabinet nu poate emite o cheie care ocolește parola."""
    cl = _client()
    r = cl.post("/cabinet/api-chei", json={"nume": "de la angajat"}, headers=_H(env["tok_angajatA"]))
    assert r.status_code in (401, 403), "angajatul emite chei de API: %d %s" % (r.status_code, r.text[:200])


# ── DELETE /cabinet/api-chei/{kid} ───────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_revocarea_CHIAR_inchide_usa(env):
    """Inima rutei: aceeași cheie, 200 înainte, 401 după. Fără perechea asta, `{"revocat": id}` e
    doar un cuvânt."""
    cl = _client()
    k = _cheie(cl, env["tok_adminA"], "proba revocare")
    assert cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]}).status_code == 200

    r = cl.delete("/cabinet/api-chei/%d" % k["id"], headers=_H(env["tok_adminA"]))
    assert r.status_code == 200 and r.json().get("revocat") == k["id"], r.text[:200]

    dupa = cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]})
    assert dupa.status_code == 401, ("cheia revocată încă deschide API-ul (%d) — revocarea e doar "
                                     "un rând schimbat, nu o ușă închisă" % dupa.status_code)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nu_pot_revoca_cheia_altui_cabinet(env):
    """Refuzul se măsoară pe EFECT, nu pe cod: cheia lui A rămâne bună după încercarea lui B."""
    cl = _client()
    k = _cheie(cl, env["tok_adminA"], "a lui A")
    r = cl.delete("/cabinet/api-chei/%d" % k["id"], headers=_H(env["tok_adminB"]))
    assert r.status_code in (403, 404), "B revocă o cheie a lui A: %d %s" % (r.status_code, r.text[:200])
    assert cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]}).status_code == 200, (
        "cheia lui A a murit după o cerere a lui B — refuzul a avut efect")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_revocarea_unei_chei_inexistente_refuza_curat(env):
    cl = _client()
    r = cl.delete("/cabinet/api-chei/999999999", headers=_H(env["tok_adminA"]))
    assert r.status_code == 404, "cheie inexistentă -> %d (nu 404): %s" % (r.status_code, r.text[:200])
    assert r.status_code != 500


# ── /admin/cabinete/{firm_id}/suspenda · reactiveaza ─────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_suspendarea_cere_superadmin(env):
    """Un admin de cabinet nu-și poate suspenda concurentul — nici pe sine."""
    cl = _client()
    for tok in (env["tok_adminA"], env["tok_angajatA"]):
        r = cl.post("/admin/cabinete/%d/suspenda" % env["firmB"], headers=_H(tok))
        assert r.status_code in (401, 403), "suspendare fără superadmin: %d %s" % (r.status_code, r.text[:200])
    with env["conn"].cursor() as cur:
        cur.execute("SELECT activ FROM public.accounting_firms WHERE id=%s", (env["firmB"],))
        assert cur.fetchone()[0] is True, "refuzul a avut totuși efect: cabinetul B e suspendat"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_suspendarea_opreste_loginul_iar_reactivarea_il_reda(env):
    """Efectul măsurat la poartă, nu în coloană: `login` distinge CABINET_SUSPENDAT de AUTH_ESEC
    ÎNAINTE de a verifica parola, deci se vede cu o parolă oricare."""
    cl = _client()
    conn = env["conn"]

    inainte = auth_api.login(conn, "ztest_chei_a@invalid", "parola-gresita")
    assert inainte["cod"] == "AUTH_ESEC", "martor: %r" % inainte

    r = cl.post("/admin/cabinete/%d/suspenda" % env["firmA"], headers=_H(env["tok_super"]))
    assert r.status_code == 200, r.text[:200]
    dupa = auth_api.login(conn, "ztest_chei_a@invalid", "parola-gresita")
    assert dupa["cod"] == "CABINET_SUSPENDAT", (
        "suspendarea nu se vede la login: %r — ruta ar schimba o coloană fără urmare" % dupa)

    r = cl.post("/admin/cabinete/%d/reactiveaza" % env["firmA"], headers=_H(env["tok_super"]))
    assert r.status_code == 200, r.text[:200]
    redat = auth_api.login(conn, "ztest_chei_a@invalid", "parola-gresita")
    assert redat["cod"] == "AUTH_ESEC", "reactivarea nu redă accesul: %r" % redat


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cheia_moare_cu_cabinetul_suspendat_si_INVIE_la_reactivare(env):
    """[DECIZIA lui Costin, 14.09.2026] Suspendarea e poartă de autentificare și închide TOT
    accesul: datele unui cabinet suspendat se livrează prin export explicit, nu prin chei live.
    Reactivarea redă cheile existente — fără regenerare și fără ca ele să fi fost revocate.

    Proba a fost scrisă `xfail(strict=True)` când a găsit gaura (cheile mergeau mai departe);
    acum e poarta deciziei. **Aceeași cheie**, trei stări — altfel un 401 de la altceva (o cheie
    stricată, o rută căzută) ar trece drept „suspendarea funcționează"."""
    cl = _client()
    k = _cheie(cl, env["tok_adminA"], "inainte de suspendare")
    assert cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]}).status_code == 200

    assert cl.post("/admin/cabinete/%d/suspenda" % env["firmA"],
                   headers=_H(env["tok_super"])).status_code == 200
    dupa = cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]})
    assert dupa.status_code == 401, (
        "cheia unui cabinet SUSPENDAT încă deschide API-ul (%d)" % dupa.status_code)

    assert cl.post("/admin/cabinete/%d/reactiveaza" % env["firmA"],
                   headers=_H(env["tok_super"])).status_code == 200
    redat = cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]})
    assert redat.status_code == 200, (
        "după reactivare, ACEEAȘI cheie nu mai deschide (%d) — reactivarea ar cere regenerarea "
        "cheilor, ceea ce decizia spune explicit că nu trebuie" % redat.status_code)

    with env["conn"].cursor() as cur:
        cur.execute("SELECT activ FROM public.api_chei WHERE id=%s", (k["id"],))
        assert cur.fetchone()[0] is True, (
            "suspendarea a REVOCAT cheia (`api_chei.activ=false`) — revocarea e un act separat, "
            "iar o cheie revocată de suspendare n-ar mai învia la reactivare")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_o_incercare_respinsa_nu_se_scrie_ca_folosire(env):
    """`ultima_folosire` spune când a deschis cheia, nu când a fost încercată. Dacă poarta de
    suspendare ar scrie-o oricum, coloana ar arăta că un cabinet suspendat își folosește cheile."""
    cl = _client()
    k = _cheie(cl, env["tok_adminA"], "urma folosirii")
    assert cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]}).status_code == 200
    with env["conn"].cursor() as cur:
        cur.execute("SELECT ultima_folosire FROM public.api_chei WHERE id=%s", (k["id"],))
        dupa_folosire = cur.fetchone()[0]
    assert dupa_folosire is not None, "martor: o folosire REUȘITĂ nu lasă urmă — proba n-ar separa nimic"

    assert cl.post("/admin/cabinete/%d/suspenda" % env["firmA"],
                   headers=_H(env["tok_super"])).status_code == 200
    assert cl.get("/api/v1/firme", headers={"X-Api-Key": k["cheie"]}).status_code == 401
    with env["conn"].cursor() as cur:
        cur.execute("SELECT ultima_folosire FROM public.api_chei WHERE id=%s", (k["id"],))
        dupa_refuz = cur.fetchone()[0]
    assert dupa_refuz == dupa_folosire, (
        "o încercare RESPINSĂ a mutat `ultima_folosire` (%s -> %s)" % (dupa_folosire, dupa_refuz))
