# -*- coding: utf-8 -*-
"""core/test_cont_venit_linie.py — #11: contul de venit stabilit PE LINIE de factura.

Garaza ca la contabilizarea unei facturi emise nota se grupeaza pe (cont_venit, cota):
o factura mixta (o linie de serviciu -> 704, o linie de marfa -> 707) produce DOUA credite
distincte de venit, cu bazele corecte. Inainte contul era unic pe firma (COALESCE(
cont_venit_implicit,'707')) si ignora ce contine linia (o factura de servicii primea 707).

Testeaza logica de grupare direct pe factura_linii + core.facturi.factura_emisa (replica a
caii din main.py factura_contabilizeaza), ca sa nu depinda de auth/endpoint. cont_venit e pus
direct pe linii (nu depinde de AI). skipif DB indisponibil.
"""
from decimal import Decimal
import psycopg2.extras as _E
import pytest
from core import db as _db, tenant_provisioning as _tp
from core import facturi as _fc

_SCHEMA = "test_cont_venit_linie"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _make_schema(conn, schema):
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
        cur.execute(_tp.parametrizeaza_template(
            open("tenant_template.sql", encoding="utf-8").read(), schema))
        cur.execute("SET search_path TO %s, public" % schema)


def _note_contabilizare(conn, schema, factura_id):
    """Replica a logicii de grupare din main.py (directie emisa): grupeaza pe (cont_venit, cota)
    si concateneaza notele. Intoarce lista de note (dict debit/credit/suma)."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT * FROM facturi WHERE id=%s", (factura_id,))
        f = cur.fetchone()
        cur.execute("SELECT COALESCE(tva_la_incasare,false) AS b FROM firma_profil WHERE id=1")
        tvai = cur.fetchone()["b"]
        cur.execute("SELECT cont_venit_implicit FROM firma_profil WHERE id=1")
        _cvi = ((cur.fetchone() or {}).get("cont_venit_implicit")) or '707'
        cur.execute("""SELECT COALESCE(NULLIF(cont_venit,''), %s) AS cv, cota_tva,
                              COALESCE(SUM(cantitate*pret_unitar),0) AS baza
                       FROM factura_linii WHERE factura_id=%s
                       GROUP BY cv, cota_tva ORDER BY cv, cota_tva""", (_cvi, factura_id))
        grupuri = [dict(r) for r in cur.fetchall()]
    note = []
    for g in grupuri:
        note += _fc.factura_emisa(Decimal(str(g["baza"] or 0)),
                                  cota=Decimal(str(g["cota_tva"])) / 100,
                                  la_data=str(f["data_emitere"]),
                                  tva_incasare=tvai, cont_venit=g["cv"])
    return note


@pytest.fixture
def conn_schema():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            _make_schema(conn, _SCHEMA)
            with conn.cursor() as cur:
                cur.execute("INSERT INTO firma_profil (id,nume,cui,platitor_tva) "
                            "VALUES (1,'TEST SRL','RO12345678',true)")
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,total,tva) "
                            "VALUES ('F1','2026-08-01','emisa',3630,630) RETURNING id")
                fid = cur.fetchone()[0]
                # linie de serviciu -> 704 (baza 1000); linie de marfa -> 707 (baza 2000)
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva,cont_venit) "
                            "VALUES (%s,'Consultanta tehnica','buc',1,1000,21,'704')", (fid,))
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva,cont_venit) "
                            "VALUES (%s,'Marfuri diverse','buc',4,500,21,'707')", (fid,))
            yield conn, fid
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_mixta_grupeaza_venit_704_si_707(conn_schema):
    conn, fid = conn_schema
    note = _note_contabilizare(conn, _SCHEMA, fid)
    credite = {}
    for n in note:
        credite.setdefault(n["credit"], Decimal(0))
        credite[n["credit"]] += Decimal(str(n["suma"]))
    # baza pe fiecare cont de venit
    assert credite.get("704") == Decimal("1000.00"), "704 (serviciu) gresit: %r" % credite
    assert credite.get("707") == Decimal("2000.00"), "707 (marfa) gresit: %r" % credite
    # TVA colectata pe total baza (3000 * 21%)
    assert credite.get("4427") == Decimal("630.00"), "4427 (TVA) gresit: %r" % credite
    # debitul 4111 = total factura (baza + TVA)
    debit = sum((Decimal(str(n["suma"])) for n in note if n["debit"] == "4111"), Decimal(0))
    assert debit == Decimal("3630.00"), "4111 total gresit: %r" % debit


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_linie_fara_cont_cade_pe_implicit(conn_schema):
    """Linie fara cont_venit -> cade pe cont_venit_implicit al firmei (aici default 707)."""
    conn, fid = conn_schema
    with conn.cursor() as cur:
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                    "VALUES (%s,'Fara cont','buc',1,100,21)", (fid,))
    note = _note_contabilizare(conn, _SCHEMA, fid)
    credite = {}
    for n in note:
        credite.setdefault(n["credit"], Decimal(0))
        credite[n["credit"]] += Decimal(str(n["suma"]))
    # 707 = marfa 2000 + linia fara cont 100 (cazuta pe implicit 707)
    assert credite.get("707") == Decimal("2100.00"), "fallback implicit gresit: %r" % credite
    assert credite.get("704") == Decimal("1000.00"), "704 neschimbat: %r" % credite


def test_venit_mapare_tip_cont():
    """Guard pur pe maparea tip->cont (OMFP 1802/2014), pe care se sprijina auto-detectia din denumire."""
    assert _fc.VENIT["servicii"] == "704"
    assert _fc.VENIT["marfa"] == "707"
    assert _fc.VENIT["produse"] == "701"
