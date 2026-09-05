# -*- coding: utf-8 -*-
"""GARD D406 checksum CUI/CNP partener + firma proprie (T1, CATALOG_INVALIDITATE.md; 10.08.2026).

Pana la aceasta tura D406 emitea TACIT orice cod fiscal de partener (00+cod) si CUI-ul firmei cu
cifra de control gresita -> DUK "RegistrationNumber/SupplierID format invalid" abia la depunere
(clasa (c), E1/E16). Reparat: valideaza_cui/valideaza_cif (core.identitate, sursa canonica,
read-only) verifica OFFLINE pre-DUK; invalid -> ValueError care NUMESTE partenerul + motivul.

MUTATIE (HEAD 8b74ccb): pull() emitea 00+cod_invalid fara sa ridice -> pytest.raises(ValueError)
  PICA; erori_generare verifica doar prezenta CUI-ului firmei, nu cifra de control.
"""
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_cui_checksum"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _seed(conn, cui_firma="14399840", tert_cui="14399841", tert_nume="BADCO SRL", directie="primita"):
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
        cur.execute("SET search_path TO \"%s\", public" % SCH)
        cur.execute("INSERT INTO firma_profil (id,nume,cui,platitor_tva,tva_la_incasare,tip_decont) VALUES (1,%s,%s,true,false,'L')",
                    ("ZTEST SRL", cui_firma))
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    ("F1", "2026-08-10", directie, 119, 19, tert_cui, tert_nume, directie))


@pytest.fixture
def conn():
    _db.init_pool(); p = _db.pool(); c = p.getconn()
    try:
        yield c
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback(); p.putconn(c)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_partener_cui_checksum_gresit_ridica_numind_partenerul(conn):
    # 14399840 e CUI valid; 14399841 = aceeasi baza cu cifra de control gresita.
    _seed(conn, tert_cui="14399841", tert_nume="BADCO SRL")
    with pytest.raises(ValueError) as ei:
        d406.genereaza(conn, SCH, 2026, 8)
    msg = str(ei.value)
    assert "BADCO SRL" in msg, "eroarea trebuie sa NUMEASCA partenerul: %s" % msg
    assert "control" in msg.lower(), "eroarea trebuie sa dea motivul (cifra de control): %s" % msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_partener_cnp_gresit_ridica_numind_partenerul(conn):
    # 1900101410011 e CNP valid; 1900101410010 = cifra de control gresita.
    _seed(conn, tert_cui="1900101410010", tert_nume="POPESCU PF")
    with pytest.raises(ValueError) as ei:
        d406.genereaza(conn, SCH, 2026, 8)
    assert "POPESCU PF" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_partener_cui_valid_nu_ridica(conn):
    _seed(conn, tert_cui="14399840", tert_nume="GOODCO SRL")
    xml, res = d406.genereaza(conn, SCH, 2026, 8)   # nu trebuie sa ridice
    assert "0014399840" in xml, "partenerul RO valid trebuie emis 00+CUI"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cui_firma_checksum_gresit_ridica(conn):
    _seed(conn, cui_firma="14399841", tert_cui="14399840", tert_nume="GOODCO SRL")
    with pytest.raises(ValueError) as ei:
        d406.genereaza(conn, SCH, 2026, 8)
    assert "CUI firma invalid" in str(ei.value), str(ei.value)
