# -*- coding: utf-8 -*-
"""[C3, 17.09.2026] O conexiune moartă nu se scurge din pool.

Constatarea C3: în `finally`, `RESET search_path` (sau rollback-ul lui) ridica pe o conexiune moartă
(pg_terminate_backend, failover, RST), iar excepția sărea PESTE `p.putconn(conn)` → conexiunea rămânea
în `_used` pentru totdeauna. După `ICONTA_POOL_MAX` evenimente: `PoolError('connection pool
exhausted')` pe toate rutele. Proba omoară backend-ul în interiorul unui bloc `get_conn(schema)` și
verifică că `_used` revine la baseline (conexiunea se ÎNCHIDE, nu se scurge). PICĂ pe codul de
dinainte (used rămâne crescut), TRECE după.
"""
import pytest

from core import db as _db


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_conexiune_moarta_se_inchide_nu_se_scurge():
    _db.init_pool()
    p = _db.pool()
    inainte = len(getattr(p, "_used", {}))
    try:
        with _db.get_conn("ztest_c3_schema") as conn:
            pid = conn.get_backend_pid()
            # omoară backend-ul ACESTEI conexiuni dintr-o ALTĂ conexiune din pool
            k = p.getconn()
            try:
                with k.cursor() as c:
                    c.execute("SELECT pg_terminate_backend(%s)", (pid,))
                k.commit()
            finally:
                p.putconn(k)
            # forțează recunoașterea morții (altfel `closed` rămâne 0 până la prima operațiune)
            with conn.cursor() as c:
                c.execute("SELECT 1")
    except Exception:
        pass
    dupa = len(getattr(p, "_used", {}))
    assert dupa == inainte, ("conexiune moartă SCURSĂ din pool: _used %d -> %d (ar trebui să revină la "
                             "baseline — conexiunea moartă se închide, nu rămâne rezervată)" % (inainte, dupa))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mai_multe_morti_nu_epuizeaza_poolul():
    """Repetat: N morți consecutive NU cresc `_used` (altfel s-ar ajunge la PoolError)."""
    _db.init_pool()
    p = _db.pool()
    inainte = len(getattr(p, "_used", {}))
    for _ in range(4):
        try:
            with _db.get_conn("ztest_c3_schema") as conn:
                pid = conn.get_backend_pid()
                k = p.getconn()
                try:
                    with k.cursor() as c:
                        c.execute("SELECT pg_terminate_backend(%s)", (pid,))
                    k.commit()
                finally:
                    p.putconn(k)
                with conn.cursor() as c:
                    c.execute("SELECT 1")
        except Exception:
            pass
    dupa = len(getattr(p, "_used", {}))
    assert dupa == inainte, "pool epuizat de morți repetate: _used %d -> %d" % (inainte, dupa)
