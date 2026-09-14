# -*- coding: utf-8 -*-
"""`POST /eu/schimba-parola` — a doua suprafață de autentificare fără probă din lista auditului.

Ce întreabă, și de ce nu codul HTTP: **ce se schimbă în lume**. O parolă schimbată trebuie să
deschidă loginul, iar cea veche să nu-l mai deschidă — perechea asta e testul; un `{"ok": true}`
singur nu spune nimic. Iar un refuz (parolă actuală greșită, parolă nouă prea scurtă) trebuie să
lase parola NEATINSĂ: o rută care refuză dar apucă să scrie e mai rea decât una care acceptă.

Probele lovesc ruta, nu funcția din use-case: corpul ei stă în `core/uc_eu.py`, iar regula lui E3
spune că o probă pe rută supraviețuiește mutării — una pe funcție se rescrie.
"""
from __future__ import annotations

import contextlib

import pytest

from core import auth_api
from core import db as _db
from core import nucleu

VECHE = "parola-veche-de-proba"
NOUA = "parola-noua-de-proba"


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
def env(monkeypatch):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST PAROLA') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_parola@invalid',%s,'N','N','admin_firma',%s,true) RETURNING id",
                        (nucleu.hash_parola(VECHE), firm))
            uid = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"uid": uid, "conn": conn, "email": "ztest_parola@invalid",
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma",
                                            "accounting_firm_id": firm})}
    finally:
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _schimba(cl, env, veche, noua):
    return cl.post("/eu/schimba-parola", json={"parola_veche": veche, "parola_noua": noua},
                   headers={"Authorization": "Bearer " + env["tok"]})


def _intra(env, parola):
    """Loginul, întrebat direct (nu prin HTTP): ruta de login are limitator de ritm, iar proba n-are
    treabă cu el — aici se măsoară doar dacă parola deschide."""
    return auth_api.login(env["conn"], env["email"], parola).get("ok") is True


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_parola_schimbata_DESCHIDE_iar_cea_veche_NU_MAI_deschide(env):
    cl = _client()
    assert _intra(env, VECHE), "martor: parola de pornire nu deschide — proba n-ar dovedi nimic"

    r = _schimba(cl, env, VECHE, NOUA)
    assert r.status_code == 200, r.text[:200]

    assert _intra(env, NOUA), "parola nouă nu deschide loginul"
    assert not _intra(env, VECHE), "parola VECHE încă deschide loginul după schimbare"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_parola_actuala_gresita_refuza_SI_nu_schimba_nimic(env):
    cl = _client()
    r = _schimba(cl, env, "parola-care-nu-e-a-mea", NOUA)
    assert r.status_code == 403, "parola actuală greșită trece: %d %s" % (r.status_code, r.text[:200])
    assert _intra(env, VECHE), "refuzul a schimbat totuși parola: cea veche nu mai deschide"
    assert not _intra(env, NOUA), "refuzul a scris parola nouă"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_parola_noua_prea_scurta_e_refuzata_inainte_sa_atinga_ceva(env):
    cl = _client()
    scurta = "a" * (nucleu.PAROLA_MIN - 1)
    r = _schimba(cl, env, VECHE, scurta)
    assert r.status_code == 400, "parola prea scurtă trece: %d %s" % (r.status_code, r.text[:200])
    assert _intra(env, VECHE), "refuzul a schimbat parola"
    assert not _intra(env, scurta), "parola prea scurtă a fost totuși scrisă"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_schimbarea_lasa_urma_in_parola_schimbata(env):
    """Coloana pe care se sprijină îndemnul „schimbă-ți parola inițială": dacă rămâne false după o
    schimbare reușită, aplicația cere la nesfârșit ceva ce s-a făcut deja."""
    cl = _client()
    with env["conn"].cursor() as cur:
        cur.execute("SELECT parola_schimbata FROM public.users WHERE id=%s", (env["uid"],))
        assert cur.fetchone()[0] is False, "martor: coloana pornea deja true"

    assert _schimba(cl, env, VECHE, NOUA).status_code == 200
    with env["conn"].cursor() as cur:
        cur.execute("SELECT parola_schimbata FROM public.users WHERE id=%s", (env["uid"],))
        assert cur.fetchone()[0] is True, "schimbarea reușită n-a lăsat urmă"
