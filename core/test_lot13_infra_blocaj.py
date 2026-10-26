# -*- coding: utf-8 -*-
"""Lotul 13, C201 — blocajul fără ieșire dintre o cerere care ține DOUĂ conexiuni și o operație de structură (DDL) pe aceeași firmă,
reprodus determinist pe baza de TEST, cu două fire, înainte și după reparație.

CE S-A VĂZUT (25.10.2026, rularea țintită e2e a lotului 12; `DEFICIENTE.md` C201). Control fiscal ținea în aceeași cerere
`with db.get_conn(schema) as cs, db.get_conn() as cp`. `cs` citise tabelele firmei (blocare AccessShare, ținută până la capătul
tranzacției) și stătea „idle in transaction”; `DROP SCHEMA … CASCADE` al curățeniei e2e a cerut AccessExclusive și a intrat la coadă
după `cs`; `cp` a cerut apoi o blocare pe aceleași obiecte și a intrat la coadă după `DROP`. Ciclul trece prin firul aplicației (care
așteaptă `cp` ca să termine `cs`), deci PostgreSQL nu-l vede: 38 de minute, până la `pg_terminate_backend`.

FORMA PROBEI. Schema efemeră `ztest_l13_infra_blocaj` cu un tabel; firul CERERE ia `cs`, citește, se oprește la un semnal; firul DDL
pornește `DROP SCHEMA` pe o conexiune fără termen (ca vechea curățenie); proba așteaptă până când DDL-ul chiar stă la coadă după `cs`
(`pg_stat_activity.wait_event_type = 'Lock'`, nu un somn), apoi lasă cererea să continue:

  1. ÎNAINTE — conexiunile aplicației fără termen (forma de dinainte de C201), două conexiuni: după 4 s cererea și DDL-ul stau amândouă
     la coadă (`pg_blocking_pids` arată ciclul DDL <- cs, cp <- DDL). Proba îl desface cu `pg_terminate_backend`, ca pe 25.10.
  2. DUPĂ, partea a doua a reparației — termenele aplicației (`db.optiuni_sesiune`, aici `lock_timeout` scurtat la 2 s ca proba să
     fie scurtă): `cp` se oprește cu `LockNotAvailable`, `cs` se anulează, DDL-ul trece; eroarea are textul pentru contabil.
  3. DUPĂ, partea întâi — O SINGURĂ conexiune (forma reparată a Control fiscal): a doua citire e pe `cs`, care ține deja blocarea, deci
     nu intră la coadă; cererea se termină, DDL-ul trece după ea. Nicio eroare, niciun termen atins.

Temei: N/A — reparație tehnică (nu aplică o regulă fiscală).
"""
import threading
import time

import psycopg2
import pytest

from core import db

SCH = "ztest_l13_infra_blocaj"


def _dsn():
    return db.dsn_din_config(db.config_din_env())


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def schema_cu_tabel():
    if not _db_ok():
        pytest.skip("fara baza de date")
    with psycopg2.connect(_dsn()) as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute("CREATE SCHEMA %s" % SCH)
        cur.execute("CREATE TABLE %s.t (x int)" % SCH)
        cur.execute("INSERT INTO %s.t VALUES (1)" % SCH)
    try:
        yield SCH
    finally:
        with psycopg2.connect(_dsn()) as c, c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)


def _pool(optiuni):
    """Un pool separat al probei, cu termenele date (`options` la conectare, exact ca `db.init_pool`)."""
    return db._clasa_pool()(1, 4, _dsn(), asteptare_sec=5, options=optiuni)


def _asteapta(conditie, termen=10.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < termen:
        if conditie():
            return True
        time.sleep(0.05)
    return False


def _sta_la_coada(pid):
    with psycopg2.connect(_dsn()) as c, c.cursor() as cur:
        cur.execute("SELECT wait_event_type FROM pg_stat_activity WHERE pid = %s", (pid,))
        r = cur.fetchone()
        return bool(r) and r[0] == "Lock"


def _blocanti(pid):
    with psycopg2.connect(_dsn()) as c, c.cursor() as cur:
        cur.execute("SELECT pg_blocking_pids(%s)", (pid,))
        return set(cur.fetchone()[0] or [])


def _ruleaza(monkeypatch, optiuni, doua_conexiuni):
    """Pune în scenă cererea și DDL-ul. Întoarce (stare, firul_cererii, firul_ddl, pid-uri) imediat după ce cererea a fost lăsată să
    continue; apelantul decide cât așteaptă și ce verifică."""
    p = _pool(optiuni)
    monkeypatch.setattr(db, "_pool", p)
    st = {"pid_cs": None, "pid_cp": None, "pid_ddl": None, "eroare_cerere": None, "cerere_gata": None, "ddl_gata": None,
          "eroare_ddl": None}
    pas1, continua = threading.Event(), threading.Event()

    def cerere():
        try:
            with db.get_conn(SCH) as cs:
                with cs.cursor() as cur:
                    cur.execute("SELECT pg_backend_pid()")
                    st["pid_cs"] = cur.fetchone()[0]
                    cur.execute("SELECT count(*) FROM t")          # AccessShare pe t, ținută până la capătul tranzacției
                pas1.set()
                continua.wait(20)
                if doua_conexiuni:
                    with db.get_conn() as cp:                       # forma de dinainte: a doua conexiune a aceleiași cereri
                        with cp.cursor() as cur:
                            cur.execute("SELECT pg_backend_pid()")
                            st["pid_cp"] = cur.fetchone()[0]
                            cur.execute("SELECT count(*) FROM %s.t" % SCH)
                else:
                    with cs.cursor() as cur:                        # forma reparată: pe aceeași conexiune
                        cur.execute("SELECT count(*) FROM %s.t" % SCH)
            st["cerere_gata"] = time.monotonic()
        except Exception as e:  # noqa: BLE001 — proba citește eroarea
            st["eroare_cerere"] = e
            st["cerere_gata"] = time.monotonic()

    ddl_conn = psycopg2.connect(_dsn(), options="-c lock_timeout=0")   # vechea curățenie: fără termen

    def ddl():
        try:
            with ddl_conn.cursor() as cur:
                cur.execute("SELECT pg_backend_pid()")
                st["pid_ddl"] = cur.fetchone()[0]
                cur.execute("DROP SCHEMA %s CASCADE" % SCH)
            ddl_conn.commit()
            st["ddl_gata"] = time.monotonic()
        except Exception as e:  # noqa: BLE001
            st["eroare_ddl"] = e

    fc = threading.Thread(target=cerere, daemon=True)
    fc.start()
    assert pas1.wait(10), "cererea n-a ajuns la prima citire"
    fd = threading.Thread(target=ddl, daemon=True)
    fd.start()
    assert _asteapta(lambda: st["pid_ddl"] is not None and _sta_la_coada(st["pid_ddl"])), "DDL-ul nu a intrat la coadă după cerere"
    assert st["pid_cs"] in _blocanti(st["pid_ddl"]), "DDL-ul nu așteaptă conexiunea cererii"
    st["t_continua"] = time.monotonic()
    continua.set()
    return st, fc, fd, p, ddl_conn


def _inchide(st, fc, fd, p, ddl_conn):
    """Oprește proba fără să lase nimic agățat: dacă firele încă așteaptă (proba a căzut), conexiunea cererii se oprește din bază,
    ca pe 25.10 — altfel curățenia schemei ar aștepta după ele până la `idle_in_transaction_session_timeout`."""
    fc.join(1)
    if fc.is_alive() or fd.is_alive():
        with psycopg2.connect(_dsn()) as c, c.cursor() as cur:
            cur.execute("SELECT pg_terminate_backend(p) FROM unnest(%s::int[]) p WHERE p IS NOT NULL",
                        ([st["pid_cs"], st["pid_cp"]],))
    fc.join(15)
    fd.join(15)
    try:
        ddl_conn.close()
    finally:
        p.closeall()


def test_inainte_doua_conexiuni_fara_termen_blocaj_fara_iesire(schema_cu_tabel, monkeypatch):
    """Forma de dinainte de C201: cererea ține două conexiuni, nicio conexiune n-are termen. Ciclul se formează și nu se desface singur
    (aici 4 s; pe 25.10, 38 de minute)."""
    st, fc, fd, p, ddl_conn = _ruleaza(monkeypatch, "-c lock_timeout=0 -c idle_in_transaction_session_timeout=0", True)
    try:
        assert _asteapta(lambda: st["pid_cp"] is not None and _sta_la_coada(st["pid_cp"])), "a doua conexiune nu a intrat la coadă"
        time.sleep(4)
        assert fc.is_alive() and fd.is_alive(), "blocajul s-a desfăcut singur — atunci forma de dinainte nu mai reproduce C201"
        assert st["pid_ddl"] in _blocanti(st["pid_cp"]), "a doua conexiune a cererii nu așteaptă DDL-ul"
        assert st["pid_cs"] in _blocanti(st["pid_ddl"]), "DDL-ul nu așteaptă prima conexiune a cererii"
    finally:
        with psycopg2.connect(_dsn()) as c, c.cursor() as cur:              # deblocarea de pe 25.10: conexiunea aplicației, oprită
            cur.execute("SELECT pg_terminate_backend(%s)", (st["pid_cs"],))
        _inchide(st, fc, fd, p, ddl_conn)
    assert st["ddl_gata"] is not None, "DDL-ul n-a trecut nici după oprirea conexiunii cererii"


def test_dupa_termenul_aplicatiei_opreste_cererea_cu_mesaj_si_ddl_trece(schema_cu_tabel, monkeypatch):
    """Partea a doua a reparației: conexiunile aplicației poartă `lock_timeout` (`db.optiuni_sesiune`). Chiar dacă un drum ar mai ține
    două conexiuni, a doua se oprește cu `LockNotAvailable` după termen, tranzacția cererii se anulează, DDL-ul trece."""
    optiuni = db.optiuni_sesiune({"ICONTA_LOCK_TIMEOUT": "2s"})
    st, fc, fd, p, ddl_conn = _ruleaza(monkeypatch, optiuni, True)
    try:
        assert _asteapta(lambda: st["cerere_gata"] is not None, 8), "cererea nu s-a oprit la termen"
        assert _asteapta(lambda: st["ddl_gata"] is not None, 8), "DDL-ul nu a trecut după oprirea cererii"
    finally:
        _inchide(st, fc, fd, p, ddl_conn)
    e = st["eroare_cerere"]
    assert isinstance(e, psycopg2.errors.LockNotAvailable), "cererea trebuia oprită de lock_timeout, nu: %r" % (e,)
    assert 1.5 <= st["cerere_gata"] - st["t_continua"] <= 6, "termenul nu e cel cerut: %.1f s" % (st["cerere_gata"] - st["t_continua"])
    assert db.text_blocaj(e).startswith("Datele firmei sunt ocupate"), "eroarea nu are textul pentru contabil"
    assert st["eroare_ddl"] is None


def test_dupa_o_singura_conexiune_cererea_se_termina_si_ddl_trece_dupa_ea(schema_cu_tabel, monkeypatch):
    """Partea întâi a reparației (forma Control fiscal de acum): a doua citire e pe conexiunea care ține deja blocarea — nu intră la
    coadă după DDL, cererea se termină fără nicio eroare și fără să atingă termenul, iar DDL-ul trece imediat după commitul ei."""
    st, fc, fd, p, ddl_conn = _ruleaza(monkeypatch, db.optiuni_sesiune({"ICONTA_LOCK_TIMEOUT": "2s"}), False)
    try:
        assert _asteapta(lambda: st["cerere_gata"] is not None, 8), "cererea pe o singură conexiune nu s-a terminat"
        assert _asteapta(lambda: st["ddl_gata"] is not None, 8), "DDL-ul nu a trecut după cerere"
    finally:
        _inchide(st, fc, fd, p, ddl_conn)
    assert st["eroare_cerere"] is None, "cererea pe o singură conexiune a căzut: %r" % (st["eroare_cerere"],)
    assert st["cerere_gata"] - st["t_continua"] < 1.5, "cererea a așteptat (a atins termenul?) — nu trebuia să intre la coadă"
    assert st["ddl_gata"] >= st["cerere_gata"], "DDL-ul a trecut înaintea cererii — atunci cererea nu ținea blocarea"
    assert st["eroare_ddl"] is None
