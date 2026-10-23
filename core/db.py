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


class SchemaInvalida(ValueError):
    """Invariant de PROGRAMATOR: numele schemei vine din cod (tenants.schema_name), nu de la om, și trebuie să fie sigur de pus în
    SQL. Rămâne `ValueError` pentru apelanții care o prind așa; mesajul nu e text pentru contabil (`core/test_text_afisat_limbaj.py`,
    `EXCEPTII_DEV` — deficiența 172, retestul Costin 09.10.2026)."""
    def __init__(self, schema):
        super().__init__("numele schemei nu e sigur pentru SQL: %r" % (schema,))


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


def config_fara_parola(cfg):
    """Configurația conexiunii, de ARĂTAT (jurnal, artefact de măsurare): parola înlocuită cu `***`, inclusiv cea din
    `url`. Pură.

    [comanda Costin 05.10.2026] `scripts/masoara_concurenta.py` a scris `str(cfg)` într-un artefact comis — parola bazei
    de producție a ajuns în git și pe oglinda publică. Orice configurație care pleacă spre un fișier sau un ecran trece
    pe aici; gard `core/test_fara_secrete_in_git.py`."""
    if cfg is None:
        return None
    out = dict(cfg)
    if out.get("password"):
        out["password"] = "***"
    if out.get("url"):
        out["url"] = _re.sub(r"(://[^:/@]+:)[^@]*@", r"\1***@", out["url"])
        out["url"] = _re.sub(r"(\bpassword=)\S+", r"\1***", out["url"])
    return out


# ============================================================
#  POOL — init o dată la pornire
# ============================================================
#: [C40, 15.10.2026] cât AȘTEAPTĂ o cerere o conexiune liberă când toate cele `maxconn` sunt împrumutate (ICONTA_POOL_ASTEPTARE_SEC)
ASTEPTARE_SEC_IMPLICIT = 20


def _clasa_pool():
    """`ThreadedConnectionPool` care AȘTEAPTĂ o conexiune eliberată (până la `asteptare_sec`) în loc să ridice pe loc
    `PoolError('connection pool exhausted')`. [C40, 15.10.2026] Înainte, un val de cereri paralele (pagina principală cere mai
    multe rute deodată) peste recalcularea din fundal pornită după orice scriere (`firma_rezumat.recalculeaza_in_fundal`) depășea
    cele `maxconn` conexiuni, iar cererea în plus primea 500, deși o conexiune se elibera după câteva milisecunde. Văzut în plasa
    e2e (`GET /coada` 500 după `POST /admin/invitatii`); aceeași fereastră există pe producție. După termen, eroarea rămâne cea a
    pool-ului (nicio cerere nu atârnă la nesfârșit). Gard: core/test_pool_asteptare.py."""
    import threading
    import time
    from psycopg2.pool import PoolError, ThreadedConnectionPool

    class PoolCuAsteptare(ThreadedConnectionPool):
        def __init__(self, minconn, maxconn, *a, asteptare_sec=ASTEPTARE_SEC_IMPLICIT, **k):
            super().__init__(minconn, maxconn, *a, **k)
            self._eliberata = threading.Condition()
            self.asteptare_sec = asteptare_sec

        def getconn(self, key=None):
            termen = time.monotonic() + self.asteptare_sec
            with self._eliberata:
                while True:
                    try:
                        return super().getconn(key)
                    except PoolError as e:
                        ramas = termen - time.monotonic()
                        if "exhausted" not in str(e) or ramas <= 0:
                            raise
                        self._eliberata.wait(ramas)

        def putconn(self, conn=None, key=None, close=False):
            try:
                super().putconn(conn, key, close)
            finally:
                with self._eliberata:
                    self._eliberata.notify()

    return PoolCuAsteptare


def init_pool(cfg=None):
    """Inițializează pool-ul global. psycopg2 importat lazy aici."""
    global _pool
    if _pool is not None:
        return _pool
    cfg = cfg if cfg is not None else config_din_env()
    _pool = _clasa_pool()(cfg["minconn"], cfg["maxconn"], dsn_din_config(cfg),
                          asteptare_sec=float(os.environ.get("ICONTA_POOL_ASTEPTARE_SEC", ASTEPTARE_SEC_IMPLICIT)))
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
        raise SchemaInvalida(schema)
    p = pool()
    # [P5, 10.09.2026] Reperele despart AȘTEPTAREA de EXECUȚIE. Inerte fără `ICONTA_CRONOMETRU=1`
    # — v. `core/cronometru.py`. Importul e local ca `db` să rămână fără dependențe la import.
    from core import cronometru as _crono
    conn = p.getconn()
    _crono.marca("pool_asteptare")
    _cu_autor = False
    try:
        if schema is not None:
            with conn.cursor() as cur:
                cur.execute('SET search_path TO "%s", public' % schema)
            _crono.marca("pool_search_path")
        # [validare_note 06.10.2026] autorul cererii, pe SESIUNE cât ține împrumutul conexiunii (nu pe tranzacție: un
        # `conn.commit()` din mijlocul unui use-case l-ar pierde pentru notele scrise după el); se ȘTERGE în `finally`, înainte
        # ca conexiunea să se întoarcă în pool. Coloana `inregistrari.creat_de_id` îl preia ca valoare implicită, iar
        # triggerul de sincronizare cu coada îl scrie ca aprobator. În afara unei cereri e None și nu se scrie nimic.
        from core import autor_cerere as _autor
        _cu_autor = _autor.uid() is not None
        if _cu_autor:
            with conn.cursor() as cur:
                cur.execute("SET iconta.utilizator TO %s", (str(_autor.uid()),))
        yield conn
        conn.commit()
    except Exception:
        # [C3] rollback-ul de aici nu are voie sa MASCHEZE eroarea originala: pe o conexiune moarta
        # ridica la randul lui, iar `raise` gol ar propaga eroarea de rollback in loc de cea reala.
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        # [C3, 17.09.2026] `putconn` RULEAZA MEREU, iar o conexiune MOARTA se INCHIDE (close=True).
        # Inainte, cand `RESET search_path` (sau rollback-ul lui) ridica pe o conexiune moarta
        # (pg_terminate_backend, failover PostgreSQL, RST), exceptia sarea PESTE `p.putconn(conn)` din
        # `finally` -> conexiunea ramanea in `_used` pentru totdeauna. Dupa `ICONTA_POOL_MAX` astfel de
        # evenimente: `PoolError('connection pool exhausted')` pe TOATE rutele, pana la restart manual
        # (procesul web n-are deadman, R75). Masurat de audit (C3) cu `pg_terminate_backend` in bloc.
        _moarta = bool(getattr(conn, "closed", 0))
        if (schema is not None or _cu_autor) and not _moarta:
            try:
                with conn.cursor() as cur:
                    if schema is not None:
                        cur.execute("RESET search_path")
                    if _cu_autor:
                        cur.execute("RESET iconta.utilizator")
                conn.commit()
            except Exception:
                _moarta = True
                try:
                    conn.rollback()
                except Exception:
                    pass
        try:
            p.putconn(conn, close=_moarta)
        except Exception:
            # ultima plasa: daca nici putconn nu reuseste, inchidem manual ca sa nu scurgem.
            try:
                conn.close()
            except Exception:
                pass


# ============================================================
#  pe_firma_existenta — o firmă a portofoliului, citită într-o buclă din cerere
# ============================================================
def schema_exista(schema):
    """True dacă schema firmei există încă în bază (pe o conexiune proprie; citirea e a depozitului, `repo_admin.schema_exista`)."""
    from core import repo_admin
    with get_conn() as conn:
        with conn.cursor() as cur:
            return repo_admin.schema_exista(cur, schema)


def fire_de_fundal_permise():
    """[lotul 11, poarta 3] False în suită (`ICONTA_FIRE_FUNDAL=0`, conftest); peste tot în rest, True. Vezi `fir_de_fundal`."""
    return os.environ.get("ICONTA_FIRE_FUNDAL", "1") != "0"


def fir_de_fundal(tinta, *args, nume):
    """`tinta(*args)` pe un fir daemon, pornit din drumul unei cereri; întoarce True dacă a pornit.

    [lotul 11, poarta 3] Singurul loc din aplicație care pornește un fir ce deschide conexiuni la bază. După orice scriere reușită,
    middleware-ul pornea `uc_coada.reia_in_fundal` (fără comutator, spre deosebire de recalcularea rezumatelor): în suită, unde testul
    înlocuiește `get_conn` cu o singură conexiune comună, firul punea `search_path` pe `public` în mijlocul lui `d300.pull` din test
    („relation inregistrari does not exist”, două picături în poarta 3, numai sub încărcare). În suită firele nu pornesc; testele
    cheamă funcțiile direct. Garda: `core/test_fire_fundal.py` (niciun `threading.Thread` în afara acestei funcții, cu excepțiile
    numite acolo)."""
    if not fire_de_fundal_permise():
        return False
    import threading
    threading.Thread(target=tinta, args=args, name=nume, daemon=True).start()
    return True


def pe_firma_existenta(schema, fn):
    """[lotul 10, eroarea 500 din `/eu/ciorne`] `fn(conn)` pe schema unei firme din portofoliu, citită în bucla unei cereri.
    Între citirea listei firmelor și interogarea uneia, firma se poate șterge (schema ei dispare): atunci întoarce
    `(False, None)` și bucla trece mai departe — firma nu mai e în portofoliu. Orice altă eroare (sau aceeași eroare pe o
    schemă care încă există, adică un defect real: o tabelă lipsă, o migrare nerulată) se ridică mai departe, neschimbată.
    Întoarce `(True, fn(conn))`."""
    import psycopg2.errors as _pe
    try:
        with get_conn(schema) as conn:
            return True, fn(conn)
    except (_pe.UndefinedTable, _pe.InvalidSchemaName):
        if schema_exista(schema):
            raise
        return False, None
