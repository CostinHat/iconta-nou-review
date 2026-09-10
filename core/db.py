"""
core/db.py — conexiune PostgreSQL: pool + get_conn, schema-per-tenant.
Construit PgBouncer-safe DIN START (transaction mode compatibil).

Aliniat la mediul iconta-prod: citește DB_HOST/PORT/NAME/USER/PASSWORD din
/home/costin/.iconta/db.env (aceleași variabile ca aplicația veche).
Dacă există DATABASE_URL, îl preferă — comutarea pe PgBouncer = doar schimbi
DATABASE_URL (sau DB_HOST/PORT), ZERO cod.

Principii:
  - Pool global (ThreadedConnectionPool). Conexiunile se reciclează
    (vechiul main.py deschidea psycopg2.connect() la FIECARE rută — înlocuit).
  - search_path cu SET LOCAL (valabil DOAR în tranzacția curentă)
    -> sigur în PgBouncer transaction mode.
  - psycopg2 importat LAZY (doar la init_pool) — restul logicii e pură.

Se dovedește pe server: forma tabelelor auth/tenant, maparea tenant->schemă.
"""
from __future__ import annotations
import os
import re as _re
from contextlib import contextmanager

REGULI = "2026.1"
MODUL = "db"

_pool = None

# nume schemă valid PostgreSQL: litere/cifre/_ , nu începe cu cifră.
# blochează injecția SQL prin numele schemei (vine din DB/tenant).
_SCHEMA_OK = _re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def schema_valida(schema):
    """True dacă numele schemei e sigur de pus în SQL. Pură, testabilă."""
    return bool(schema) and bool(_SCHEMA_OK.match(schema))


# ============================================================
#  CONFIG — DB_* din env (ca aplicația veche), DATABASE_URL preferat.
# ============================================================
def config_din_env(env=None):
    """
    Întoarce dict cu parametrii conexiunii. Pură (primește env).
    - daca DATABASE_URL exista -> il folosim direct ca DSN (cheia 'url')
    - altfel construim din DB_HOST/PORT/NAME/USER/PASSWORD
    Pool min/max din ICONTA_POOL_MIN/MAX (noi, cu fallback).
    """
    env = env if env is not None else os.environ
    minconn = int(env.get("ICONTA_POOL_MIN", "1"))
    maxconn = int(env.get("ICONTA_POOL_MAX", "10"))
    url = env.get("DATABASE_URL")
    if url:
        return {"url": url, "minconn": minconn, "maxconn": maxconn}
    return {
        "host": env.get("DB_HOST", "127.0.0.1"),
        "port": int(env.get("DB_PORT", "5432")),
        "dbname": env.get("DB_NAME", "iconta"),
        "user": env.get("DB_USER", "iconta"),
        "password": env.get("DB_PASSWORD", ""),
        "minconn": minconn,
        "maxconn": maxconn,
    }


def dsn_din_config(cfg):
    """DSN pentru psycopg2. Daca cfg are 'url', il intoarce direct. Pură."""
    if "url" in cfg:
        return cfg["url"]
    return ("host=%(host)s port=%(port)d dbname=%(dbname)s "
            "user=%(user)s password=%(password)s") % cfg


# ============================================================
#  POOL — init o dată la pornire
# ============================================================
def init_pool(cfg=None):
    """Inițializează pool-ul global. psycopg2 importat lazy aici."""
    global _pool
    if _pool is not None:
        return _pool
    cfg = cfg if cfg is not None else config_din_env()
    from psycopg2.pool import ThreadedConnectionPool
    _pool = ThreadedConnectionPool(
        cfg["minconn"], cfg["maxconn"], dsn_din_config(cfg))
    return _pool


def pool():
    """Pool-ul global. Eroare clară dacă nu e inițializat."""
    if _pool is None:
        raise RuntimeError("pool neinițializat — cheamă init_pool() la startup")
    return _pool


def inchide_pool():
    """Închide toate conexiunile. La oprirea aplicației."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


# ============================================================
#  get_conn — context manager. O tranzacție per request.
# ============================================================
@contextmanager
def get_conn(schema=None):
    """
    Scoate o conexiune din pool, optional fixeaza schema (SET LOCAL),
    commit la succes / rollback la excepție, întoarce conexiunea în pool.

    SET LOCAL = PgBouncer-safe: search_path traieste doar cat tranzactia.

    Folosire:
        with get_conn(ctx.schema) as conn:
            xml, res = d300.genereaza(conn, ctx.schema, an, luna)
    """
    if schema is not None and not schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    p = pool()
    # [P5, 10.09.2026] Reperele despart AȘTEPTAREA de EXECUȚIE. Inerte fără `ICONTA_CRONOMETRU=1`
    # — v. `core/cronometru.py`. Importul e local ca `db` să rămână fără dependențe la import.
    from core import cronometru as _crono
    conn = p.getconn()
    _crono.marca("pool_asteptare")
    try:
        if schema is not None:
            with conn.cursor() as cur:
                cur.execute('SET search_path TO "%s", public' % schema)
            _crono.marca("pool_search_path")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if schema is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("RESET search_path")
                conn.commit()
            except Exception:
                conn.rollback()
        p.putconn(conn)
