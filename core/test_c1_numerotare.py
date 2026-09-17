# -*- coding: utf-8 -*-
"""[C1, 17.09.2026] Numerotarea facturilor: două cereri concurente NU mai primesc același număr.

Constatarea C1: `numerotare` citea `urmator_numar_factura` fără `FOR UPDATE`, iar incrementul venea
într-un UPDATE de mai târziu — între citire și scriere, cereri simultane primeau același număr
(audit: numărul 6 pe 3 facturi). Reparația: `_rezerva_numar` face `UPDATE ... = +1 RETURNING`, atomic,
cu rândul blocat. Proba: N fire rezervă simultan → toate numerele sunt DISTINCTE. Plus indexul unic
ca plasă a doua. PICĂ pe codul de dinainte (numere duplicate), TRECE după.
"""
import threading

import pytest

from core import db as _db
from core import facturi_api

SCH = "ztest_c1_num"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def firma():
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,serie_factura,urmator_numar_factura) "
                        "VALUES (1,'ZT C1','14399840','A',1)")
        conn.commit()
        yield {"conn": conn, "pool": p}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()
        p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_rezervare_concurenta_da_numere_distincte(firma):
    p = firma["pool"]
    N = 6   # sub maxconn (10) minus conexiunea fixturii; concurenta reala, fara epuizarea pool-ului
    rezultate = []
    lock = threading.Lock()

    def worker():
        c = p.getconn()
        try:
            with c.cursor() as cur:
                cur.execute('SET search_path TO "%s", public' % SCH)
            serie, numar = facturi_api._rezerva_numar(c, "factura")
            c.commit()
            with lock:
                rezultate.append(numar)
        finally:
            with c.cursor() as cur:
                cur.execute("SET search_path TO public")
            p.putconn(c)

    fire = [threading.Thread(target=worker) for _ in range(N)]
    for t in fire:
        t.start()
    for t in fire:
        t.join()

    assert len(rezultate) == N, "%d fire, doar %d rezultate" % (N, len(rezultate))
    assert len(set(rezultate)) == N, ("numere DUPLICATE sub concurență: %s (distincte: %d din %d)"
                                      % (sorted(rezultate), len(set(rezultate)), N))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_index_unic_respinge_duplicatul(firma):
    """Plasa a doua: chiar dacă un drum ar ocoli rezervarea, INSERT-ul cu număr existent PICĂ."""
    from core import migrare_unic_numar_factura as _miu
    conn = firma["conn"]
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
    creat, dup = _miu.aplica(conn, SCH)
    conn.commit()
    assert creat, "indexul unic n-a putut fi creat: duplicate %r" % dup
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("INSERT INTO facturi (numar,serie,data_emitere,directie,total,tva) "
                    "VALUES ('A100','A','2026-09-01','emisa',100,0)")
        conn.commit()
        with pytest.raises(Exception):
            cur.execute("INSERT INTO facturi (numar,serie,data_emitere,directie,total,tva) "
                        "VALUES ('A100','A','2026-09-02','emisa',200,0)")
            conn.commit()
    conn.rollback()
