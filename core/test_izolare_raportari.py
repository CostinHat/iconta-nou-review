# -*- coding: utf-8 -*-
"""core/test_izolare_raportari.py — GARD structural de izolare pe /raportari (apararea de DATE, nu doar ruta).

Auditul 3de694e (pozitia 4): /raportari/{rid} + /{rid}/citit aveau SQL nefiltrat pe proprietar;
apararea statea DOAR in stratul de ruta (autor-match). Aceeasi clasa care a lasat cross-check-ul D300
mort sa treaca: aparare intr-un singur strat cedeaza tacut. DECIZIE Costin: filtrul de AUTOR coboara in
SQL (firul_complet), sub garda de ruta care RAMANE (nu se relaxeaza la cabinet). /citit intra in acelasi lot.

Proba (HTTP real, sesiune cross-cabinet): un fir al cabinetului B, cerut de o sesiune a cabinetului A ->
trebuie 404 (data-layer refuza, nu doar ruta). MUTATIE: pe codul de dinainte (firul_complet nefiltrat),
ruta intoarce 403 pe non-autor (nu 404) si /citit intoarce 200 (marcheaza citit strain) -> testul PICA.
Control pozitiv: autorul isi vede firul (200). Efemer: firme/useri/raportare pe o conexiune din pool,
get_conn monkeypatch-uit la un proxy cu SAVEPOINT (nicio persistare), rollback la final.
"""
import contextlib
import pytest

from core import db as _db, auth_api, raportari_api


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


def _user(cur, email, firm):
    cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                "VALUES (%s,'x','N','N','admin_firma',%s,true) RETURNING id", (email, firm))
    return cur.fetchone()[0]


@pytest.fixture
def env(monkeypatch):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST RAP A') RETURNING id")
            firmA = cur.fetchone()[0]
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST RAP B') RETURNING id")
            firmB = cur.fetchone()[0]
            userA = _user(cur, "ztest_rap_a@invalid", firmA)
            userB = _user(cur, "ztest_rap_b@invalid", firmB)
        # fir al cabinetului B (autor userB) — necomis (creeaza_raportare nu comite; get_conn ar comite)
        r = raportari_api.creeaza_raportare(conn, userB, firmB, "fir B", "mesaj privat B")
        ridB = r["raportare_id"]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute("SAVEPOINT rap_sp")
            try:
                yield _ConnProxy(conn)
            finally:
                with conn.cursor() as c:
                    try:
                        c.execute("ROLLBACK TO SAVEPOINT rap_sp"); c.execute("RELEASE SAVEPOINT rap_sp")
                    except Exception:
                        pass
        monkeypatch.setattr(_db, "get_conn", _fake)

        def tok(uid, firm):
            return auth_api.emite_token({"id": uid, "rol": "admin_firma", "accounting_firm_id": firm})
        yield {"ridB": ridB, "tok_A": tok(userA, firmA), "tok_B": tok(userB, firmB)}
    finally:
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fir_alt_cabinet_da_404_nu_403(env):
    """Sesiune cabinet A -> fir al cabinetului B: 404 (data-layer refuza). Mutatie: firul_complet nefiltrat
    -> ruta da 403 pe non-autor (SQL a ADUS deja firul) -> assert 404 pica."""
    cl = _client()
    r = cl.get("/raportari/%d" % env["ridB"], headers={"Authorization": "Bearer " + env["tok_A"]})
    assert r.status_code == 404, (
        "cross-cabinet /raportari/{rid} a intors %d, asteptat 404. 403 = firul_complet inca aduce "
        "firul din SQL, apararea sta doar in ruta." % r.status_code)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_citit_alt_cabinet_da_404(env):
    """Sesiune cabinet A -> /raportari/{rid}/citit pe fir B: 404. Mutatie: fara check de proprietar,
    marcheaza_citit ruleaza pe firul strain si intoarce 200."""
    cl = _client()
    r = cl.post("/raportari/%d/citit" % env["ridB"], headers={"Authorization": "Bearer " + env["tok_A"]})
    assert r.status_code == 404, (
        "cross-cabinet /raportari/{rid}/citit a intors %d, asteptat 404 (scriere pe fir strain)." % r.status_code)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_autorul_isi_vede_firul(env):
    """Control pozitiv: fara el, un 404 uniform ar trece gardul degeaba. Autorul (cabinet B) vede firul."""
    cl = _client()
    r = cl.get("/raportari/%d" % env["ridB"], headers={"Authorization": "Bearer " + env["tok_B"]})
    assert r.status_code == 200, "autorul nu-si mai vede firul: %d %s" % (r.status_code, r.text[:200])
    assert "mesaj privat B" in r.text
