# -*- coding: utf-8 -*-
"""[C40, 15.10.2026] Pool-ul de conexiuni AȘTEAPTĂ o conexiune eliberată în loc să dea pe loc „connection pool exhausted” (o cerere
în plus peste `maxconn` primea 500, deși o conexiune se elibera după câteva milisecunde — văzut în plasă: `GET /coada` 500 cât rula
recalcularea din fundal). Pe baza de TEST, cu un pool separat de UNA singură conexiune.
MUTAȚII: `getconn` fără așteptare (ridică pe loc) -> pică primul test; așteptare fără termen -> pică al doilea (atârnă)."""
import threading
import time

import pytest

from core import db


def _pool_de_unu(asteptare):
    return db._clasa_pool()(1, 1, db.dsn_din_config(db.config_din_env()), asteptare_sec=asteptare)


def test_cererea_in_plus_asteapta_conexiunea_eliberata():
    p = _pool_de_unu(5)
    try:
        prima = p.getconn()
        threading.Timer(0.3, lambda: p.putconn(prima)).start()
        t0 = time.monotonic()
        a_doua = p.getconn()                  # înainte: PoolError pe loc
        assert 0.2 < time.monotonic() - t0 < 4
        p.putconn(a_doua)
    finally:
        p.closeall()


def test_dupa_termen_eroarea_pool_ului_nu_atarna():
    from psycopg2.pool import PoolError
    p = _pool_de_unu(0.3)
    try:
        prima = p.getconn()
        t0 = time.monotonic()
        with pytest.raises(PoolError):
            p.getconn()
        assert time.monotonic() - t0 < 2
        p.putconn(prima)
    finally:
        p.closeall()
