# -*- coding: utf-8 -*-
"""GARD detector "running == HEAD" (DECIZII/GARZI iulie: detector vizibil, NU auto-restart).
Probe: (a) divergenta simulata -> semnal APRINS; egalitate -> semnal STINS; necunoscut -> nu alarmeaza.
(b) semnalul NU ajunge la alte roluri: endpoint-ul /admin/versiune e 403 pentru orice rol != superadmin, 200
pentru superadmin. Mutatie: inversarea logicii de divergenta -> rosu.
"""
import os, sys
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import versiune as V

A = "a" * 40
B = "b" * 40


# ---------- (a) logica de divergenta (pura) ----------
def test_divergenta_aprinde_semnalul():
    s = V.stare_versiune(A, B)
    assert s["divergent"] is True, "commit rulat != HEAD trebuie sa aprinda semnalul"
    assert s["necunoscut"] is False


def test_egalitate_stinge_semnalul():
    s = V.stare_versiune(A, A)
    assert s["divergent"] is False, "running == HEAD -> niciun semnal"
    assert s["necunoscut"] is False


def test_necunoscut_nu_alarmeaza():
    assert V.stare_versiune(None, B)["divergent"] is False
    assert V.stare_versiune(A, None)["divergent"] is False
    assert V.stare_versiune(None, B)["necunoscut"] is True
    assert V.stare_versiune(A, None)["necunoscut"] is True


def test_stampila_citeste_git_head_real():
    """stampileaza() citeste un commit real de 40 hex din procesul viu (nu None pe repo git)."""
    h = V.stampileaza()
    assert h is not None and len(h) == 40, "stampila de startup nu a citit git HEAD fidel: %r" % h


# ---------- (b) RBAC: semnalul e DOAR pentru superadmin ----------
def _client():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app)


def _tok(rol):
    from core import auth_api
    return auth_api.emite_token({"id": 1, "rol": rol, "accounting_firm_id": 1})


def test_endpoint_superadmin_vede():
    c = _client()
    r = c.get("/admin/versiune", headers={"Authorization": "Bearer " + _tok("superadmin")})
    assert r.status_code == 200, "superadmin trebuie sa vada detectorul (got %d)" % r.status_code
    j = r.json()
    assert "divergent" in j and "running" in j and "head" in j


def test_endpoint_alte_roluri_403():
    c = _client()
    for rol in ("admin_firma", "asistent", "client", "patron"):
        r = c.get("/admin/versiune", headers={"Authorization": "Bearer " + _tok(rol)})
        assert r.status_code == 403, "rolul %s NU trebuie sa vada detectorul, dar a primit %d" % (rol, r.status_code)


def test_endpoint_fara_token_401():
    c = _client()
    r = c.get("/admin/versiune")
    assert r.status_code == 401, "fara token -> 401 (got %d)" % r.status_code
