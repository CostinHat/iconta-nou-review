# -*- coding: utf-8 -*-
"""[lotul 13, poarta 1 (27.10.2026), clasa „`options` explicit calcă `PGOPTIONS`”] Scripturile care citesc producția ca read-only își pun
`PGOPTIONS=-c default_transaction_read_only=on` (`scripts/cifre_referinta.py`, `scripts/amprente_declaratii.py`) și trec apoi prin pool-ul aplicației.
C201 a dat pool-ului `options="-c lock_timeout=… -c idle_in_transaction_session_timeout=…"`; în libpq, parametrul `options` ÎNLOCUIEȘTE variabila de mediu
PGOPTIONS, deci sesiunea ieșea read-WRITE. Garda fail-closed a cifrelor („sesiunea nu e read-only — refuz”) a oprit poarta; fără ea, un generator ar fi
putut scrie pe producție. Aici: `optiuni_sesiune` păstrează PGOPTIONS (ultimul), iar o conexiune REALĂ din pool, cu PGOPTIONS read-only în mediu, e read-only.

Temei: N/A — tooling (siguranța citirii producției, CLAUDE.md regimul pilot §3).
MUTAȚIA: scos `explicit` din `db.optiuni_sesiune` -> ambele teste pică (primul: lipsește read-only din șir; al doilea: `SHOW` dă off)."""
import pytest

from core import db


def test_optiunile_aplicatiei_pastreaza_pgoptions_al_mediului():
    sir = db.optiuni_sesiune({"PGOPTIONS": "-c default_transaction_read_only=on"})
    assert sir.split() == ["-c", "lock_timeout=" + db.LOCK_TIMEOUT_IMPLICIT, "-c", "idle_in_transaction_session_timeout=" + db.IDLE_TX_TIMEOUT_IMPLICIT,
                           "-c", "default_transaction_read_only=on"], sir
    assert db.optiuni_sesiune({}).split() == ["-c", "lock_timeout=" + db.LOCK_TIMEOUT_IMPLICIT, "-c",
                                              "idle_in_transaction_session_timeout=" + db.IDLE_TX_TIMEOUT_IMPLICIT]


def test_conexiunea_reala_din_pool_cu_pgoptions_read_only_e_read_only(monkeypatch):
    monkeypatch.setenv("PGOPTIONS", "-c default_transaction_read_only=on")
    vechi = db._pool
    db._pool = None
    try:
        try:
            db.init_pool()
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SHOW default_transaction_read_only")
                    citit = cur.fetchone()[0]
                conn.rollback()
        except Exception as e:  # noqa: BLE001
            pytest.skip("baza de test indisponibilă: %s" % e)
        assert citit == "on", citit
    finally:
        if db._pool is not None:
            try:
                db._pool.closeall()
            except Exception:  # noqa: BLE001
                pass
        db._pool = vechi
