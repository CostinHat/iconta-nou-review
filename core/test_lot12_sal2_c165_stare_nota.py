# -*- coding: utf-8 -*-
"""[lotul 12, C165] „Contabilizează statul”: starea notei de salarii se citește din NOTĂ, nu din coada de validare.

Găsită de Code la dovezile numerelor vechi (F1, nota 6 „SAL 09/2026”, validată direct — fără element în coadă): ecranul arăta „Nota
există deja în jurnal (…, ciornă).” Propunerea (`salarii_contare.propunere`) poartă acum `nota_status` (`inregistrari.status`), iar ecranul
(`firme.js`, „Contabilizează statul”) spune „e validată” după el. Temei: N/A (starea unui document din aplicație).

CNP-ul de test are cifra de control verificată (algoritmul din CLAUDE.md): 1800101410013.
"""
import pytest

from core import db as _db, salarii_contare
from core.test_lot11_s9_deducere_plafon import _setup

_SCHEMA = "test_lot12_sal2_c165"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                _setup(cur, [{"cnp": "1800101410013", "nume": "IONESCU", "dn": "1980-06-01", "brut": 5000}], schema=_SCHEMA)
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _nota(conn, status):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) VALUES ('2026-09-30', %s, 'salarii', 'salarii', %s)",
                    (salarii_contare.document_ref(2026, 9), status))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("status", ["validata", "ciorna"])
def test_def_c165_propunerea_poarta_starea_din_nota(conn, status):
    """Nota lunii, validată direct (fără element în coadă) sau ciornă: `nota_status` e starea notei. ROȘU înainte: câmpul lipsea, iar
    ecranul deducea „ciornă” din lipsa elementului din coadă."""
    _nota(conn, status)
    p = salarii_contare.propunere(conn, _SCHEMA, 2026, 9)
    assert p["nota_status"] == status, p.get("nota_status")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c165_fara_nota_starea_e_goala(conn):
    p = salarii_contare.propunere(conn, _SCHEMA, 2026, 9)
    assert p["nota_status"] is None, p.get("nota_status")
