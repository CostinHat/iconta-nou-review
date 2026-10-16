# -*- coding: utf-8 -*-
"""Registrul de evidență fiscală, varianta PROFIT, se construiește pe conexiunea FIRMEI (lotul 6, găsit de garda e2e 285, care deschide
toate cardurile firmei: `GET /tenants/{id}/registru-evidenta-fiscala?varianta=profit` -> 500 „relation firma_profil does not exist” —
`d101.genereaza` citește tabelele firmei fără schemă în nume, iar use-case-ul îi dădea conexiunea publică). Temei: N/A — tooling.
Schemă efemeră din template, ștearsă la ieșire."""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

SCH = "efemer_registru_conn"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_registrul_pe_profit_nu_cade_pe_conexiunea_publica(monkeypatch):
    """MUTAȚIE: `with db.get_conn(schema) as conn:` -> `with db.get_conn() as conn:` în `registru_fiscal_citeste` -> UndefinedTable."""
    from core import auth_api, uc_tenants, erori
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, regim_fiscal) VALUES (1, 'F SRL', 'RO14399840', 'profit')" % SCH)
        c.commit()
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    try:
        try:
            r = uc_tenants.registru_fiscal_citeste(1, 2025, "profit", "an", {"uid": 1})
            assert r, r
        except erori.EroareDeDomeniu as e:   # un refuz al datelor (profil incomplet) e răspuns, nu cădere
            assert "does not exist" not in str(e.detaliu), e.detaliu
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()
