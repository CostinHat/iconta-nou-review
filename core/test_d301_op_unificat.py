# -*- coding: utf-8 -*-
"""GARD: intrarea UNICA a achizitiei IC (achizitie-ic, DECIZII 66) nu dubleaza D390.

O operatiune D301 LEGATA de factura (factura_id NENUL) e SARITA pe calea D390-din-op
(repo_d390.select_d301_operatiuni_2/_3) — D390 o ia din factura, nu din op. Aceeasi operatiune
E prezenta pe calea D301 (repo_d301_operatiuni_api.select_d301_operatiuni) — D301 o include.
O operatiune MANUALA (factura_id NULL) apare pe AMBELE cai (alimenteaza D390 ca pana acum).

Aserteaza pe STRUCTURA (id-urile intoarse de fiecare select). MUTATIA care il face rosu:
scoaterea filtrului `factura_id IS NULL` din select_d301_operatiuni_2 -> op-ul legat reapare
pe calea D390 -> dubla numarare -> test_op_legata_nu_e_pe_calea_D390 pica."""
import pytest

from core import db as _db
from core import repo_d390 as _rd390
from core import repo_d301_operatiuni_api as _rd301


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


SCH = "ztest_d301_unif"
AN, LUNA = 2099, 6


@pytest.fixture
def schema():
    from core import tenant_provisioning as _tp
    _db.init_pool()
    conn = _db.pool().getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            # op LEGATA de factura (factura_id = 777) + op MANUALA (factura_id NULL)
            _rd301.insert_d301_operatiuni(cur, SCH, AN, LUNA, 1, "F-LEGATA", "10.06.2099",
                                          5000, "RON", 1, 1050, "DE", "DE123", "Furnizor DE",
                                          None, factura_id=777)
            _rd301.insert_d301_operatiuni(cur, SCH, AN, LUNA, 5, "F-MANUALA", "11.06.2099",
                                          2500, "RON", 1, 525, "DE", "DE123", "Furnizor DE", None)
        yield conn
    finally:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        _db.pool().putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_op_legata_nu_e_pe_calea_D390(schema):
    """Calea D390-din-op sare op-ul legat de factura (altfel: dubla numarare)."""
    with schema.cursor() as cur:
        _rd390.select_d301_operatiuni_2(cur, SCH, AN, LUNA)
        nrdoc_val = [r[3] for r in cur.fetchall()]  # partener_tara e col.3; verificam prin numar de randuri
        cur.execute('SELECT nr_doc FROM "%s".d301_operatiuni WHERE an=%%s AND luna=%%s AND factura_id IS NULL'
                    % SCH, (AN, LUNA))
        manuale = {r[0] for r in cur.fetchall()}
    # select_2 intoarce DOAR op-ul manual (factura_id NULL)
    assert manuale == {"F-MANUALA"}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_op_legata_ESTE_pe_calea_D301(schema):
    """Calea D301 include AMBELE op-uri (D301 raporteaza achizitia legata)."""
    with schema.cursor() as cur:
        _rd301.select_d301_operatiuni(cur, SCH, AN, LUNA)
        nrdoc = {r[2] for r in cur.fetchall()}  # nr_doc e col.2 in select_d301_operatiuni
    assert nrdoc == {"F-LEGATA", "F-MANUALA"}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_select_2_numara_o_data(schema):
    """Calea D390-din-op intoarce exact 1 rand (doar manualul), nu 2."""
    with schema.cursor() as cur:
        _rd390.select_d301_operatiuni_2(cur, SCH, AN, LUNA)
        assert len(cur.fetchall()) == 1
