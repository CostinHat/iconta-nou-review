# -*- coding: utf-8 -*-
"""[lotul 11, C98] „Primii pași” (`GET /eu/inceput`) nu cade cu 500 când firma sau contul dispar în timpul cererii (găsit în plasa e2e din
22.10.2026: `UndefinedTable "tenant_381".solduri_initiale` și `cannot unpack non-iterable NoneType`, de 3 ori în uvicorn.log).
(1) firma ștearsă între listarea firmelor și citirea ei -> nu mai e o firmă a cabinetului: nepreluată, fără eroare; (2) contul șters cât
sesiunea era deschisă -> 401 (`Neautentificat`), nu 500. MUTAȚII: ramura `UndefinedTable` scoasă -> (1) pică; verificarea `om is None`
scoasă -> (2) pică cu TypeError."""
import contextlib

import psycopg2.errors
import pytest

from core import erori, repo_inceput, uc_inceput


class _CurFirmaStearsa:
    """Cursorul unei firme a cărei schemă dispare după `to_regclass` (cele două tabele existau la verificare)."""
    def __init__(self):
        self.sql = []

    def execute(self, sql, params=None):
        self.sql.append(sql)
        if sql.startswith("SELECT EXISTS"):
            raise psycopg2.errors.UndefinedTable('relation "tenant_x".solduri_initiale does not exist')

    def fetchone(self):
        return (True, True)


def test_firma_stearsa_in_timpul_cererii_nu_e_preluata_si_nu_cade():
    cur = _CurFirmaStearsa()
    assert repo_inceput.preluare_facuta(cur, "tenant_x") == (False, False)
    assert cur.sql[-1] == "ROLLBACK TO SAVEPOINT preluare_facuta"   # tranzacția cererii rămâne utilizabilă pentru firmele următoare


def test_contul_sters_in_timpul_sesiunii_e_401_nu_500(monkeypatch):
    class _Conn:
        def cursor(self):
            return contextlib.nullcontext(object())
    monkeypatch.setattr(uc_inceput.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(uc_inceput._repo, "omul", lambda cur, uid: None)
    with pytest.raises(erori.Neautentificat):
        uc_inceput.carduri({"uid": 7})
