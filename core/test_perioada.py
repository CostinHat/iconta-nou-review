# -*- coding: utf-8 -*-
"""Perioada confirmata (DESIGN_SYSTEM cap.23): ciclul CONFIRMAT/NECONFIRMAT + blocajul motivat."""
import pytest
from datetime import date
from core import db as _db, tenant_provisioning as _tp, perioada as _per

SCHEMA = "ztest_perioada"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def test_ciclu_confirmat_neconfirmat(conn):
    assert _per.e_confirmat(conn, SCHEMA, 2026, 8, "pontaj")["confirmat"] is False
    _per.confirma(conn, SCHEMA, 2026, 8, "pontaj", user_id=7)
    st = _per.e_confirmat(conn, SCHEMA, 2026, 8, "pontaj")
    assert st["confirmat"] is True and st["confirmat_de"] == 7 and st["confirmat_la"]
    _per.deconfirma(conn, SCHEMA, 2026, 8, "pontaj")   # modificare inainte de depunere -> re-blocheaza
    assert _per.e_confirmat(conn, SCHEMA, 2026, 8, "pontaj")["confirmat"] is False


def test_blocaj_motivat_are_cele_4_elemente():
    e = _per.PerioadaNeconfirmata("Tichetele de masa", 2026, 8, "pontaj", "HG 1045/2018 art.10(3)")
    m = str(e)
    assert "PERIOADA_BLOCATA:" in m and isinstance(e, ValueError)
    assert "Tichetele de masa nu se poate calcula" in m       # ce s-a oprit
    assert "nu e CONFIRMAT" in m                                # de ce
    assert "Confirma pontaj-ul lunii" in m and "buton" in m     # ce se poate face
    assert "admin_firma" in m                                    # cine decide
