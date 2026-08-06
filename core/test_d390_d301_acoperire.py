# -*- coding: utf-8 -*-
"""core/test_d390_d301_acoperire.py — ACOPERIRE C-4 transa 2, items (b) si (c).

(b) D390 P1: achizitie IC de la furnizor UE EXTERN (tert_cui cu prefix UE, ex DE...).
    Codul era deja corect (d390.pull cade c.cui->tert_cui, bug reparat 16.07); acoperirea
    lipsea (niciun partener UE in seed). Gard: o factura primita cu CUI UE -> operatiune tip A.
(c) D301 N1: achizitie IC de bunuri, decont special (N1 neplatitor TVA cu operatiuni IC),
    valoare peste 10.000 EUR (L10, art.317). D301 citeste tabelul d301_operatiuni (NU facturi).
    Gard: un rand tip 1 in d301_operatiuni -> D301 cu baza=round(val*curs) + tva, DUK-valid.
    NB: pragul L10 (10.000 EUR = obligatia de depunere) NU e enforced in aplicatie
    (decizie de produs, GARZI 06.08); aici doar exercitam generatorul pe scenariul N1.
"""
import pytest
from core.common import Perioada
from core import d390 as _d390, d301 as _d301
from core import db as _db, tenant_provisioning as _tp, duk as _duk

_SCHEMA_B = "test_acop_d390_p1"
_SCHEMA_C = "test_acop_d301_n1"

_PROFIL_EXTRA = ("adresa='Str 1', oras='Buc', judet='B', banca='BCR', "
                 "iban='RO49RNCB0000000000000001', telefon='0700000000', "
                 "declarant_nume='Ionescu', declarant_prenume='Ana', declarant_functie='ADMINISTRATOR'")


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


# ---------- (b) D390 P1: achizitie IC de la furnizor UE extern ----------

@pytest.fixture
def conn_d390():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                _make_schema(conn, _SCHEMA_B)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,caen,platitor_tva,tip_decont,operatiuni_ic,"
                            "adresa,oras,judet,banca,iban,telefon,declarant_nume,declarant_prenume,declarant_functie) "
                            "VALUES (1,'P1 PROFIT SRL','95275466','4669',true,'lunar',true,"
                            "'Str 1','Buc','B','BCR','RO49RNCB0000000000000001','0700000000',"
                            "'Ionescu','Ana','ADMINISTRATOR')")
                # achizitie IC de bunuri de la furnizor UE extern (Germania). Fara TVA local (autolichidare).
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,tert_platitor_tva,"
                            "total,tva,taxare_inversa) VALUES ('DE1','2026-05-08','primita','DE136695976',"
                            "'BAUHAUS GMBH',false,15000,0,false)")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d390_p1_achizitie_ic_ue_tip_A(conn_d390):
    """Factura primita cu CUI UE (DE...) -> D390 operatiune tip A (achizitie IC), baza 15000."""
    xml, res = _d390.genereaza(conn_d390, _SCHEMA_B, 2026, 5)
    assert res.rezumat.get("A") == 15000, "achizitia IC (tip A) lipseste; rezumat=%r" % res.rezumat
    assert 'tip="A"' in xml
    r = _duk.valideaza(xml, "d390", an=2026, luna=5)
    assert r["stare"] == "valid", "DUK a respins D390 achizitie IC: %s" % r.get("erori")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d390_p1_cui_ro_NU_e_ic(conn_d390):
    """MUTATIE: daca partenerul ar fi RO (nu UE), NU e operatiune IC -> D390 nu se depune pe zero."""
    with conn_d390.cursor() as cur:
        cur.execute("UPDATE facturi SET tert_cui='RO95275466'")
    with pytest.raises(Exception):
        _d390.genereaza(conn_d390, _SCHEMA_B, 2026, 5)


# ---------- (c) D301 N1: achizitie IC de bunuri, decont special (>10.000 EUR) ----------

@pytest.fixture
def conn_d301():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                _make_schema(conn, _SCHEMA_C)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,caen,platitor_tva,tip_decont,operatiuni_ic,"
                            "adresa,oras,judet,banca,iban,telefon,declarant_nume,declarant_prenume,declarant_functie) "
                            "VALUES (1,'N1 NEPLATITOR SRL','95451848','4791',false,'trimestrial',true,"
                            "'Str 1','Buc','B','BCR','RO49RNCB0000000000000001','0700000000',"
                            "'Ionescu','Ana','ADMINISTRATOR')")
                # achizitie IC de bunuri (tip 1), 10.500 EUR (peste pragul L10 de 10.000), curs BNR.
                cur.execute("INSERT INTO d301_operatiuni (an,luna,tip,nr_doc,data_doc,val_valuta,tip_valuta,curs,tva) "
                            "VALUES (2026,6,1,'INV-DE-77','15.06.2026',10500,'EUR',4.9772,10975)")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d301_n1_achizitie_ic_bunuri(conn_d301):
    """Rand tip 1 in d301_operatiuni -> D301 cu baza=round(10500*4.9772)=52261 + tva, DUK-valid."""
    xml, res = _d301.genereaza(conn_d301, _SCHEMA_C, Perioada(2026, luna=6))
    assert res.totaluri[1][0] == 52261, "baza tip1 gresita; totaluri=%r" % res.totaluri
    assert res.totaluri[1][1] == 10975, "tva tip1 gresita; totaluri=%r" % res.totaluri
    r = _duk.valideaza(xml, "d301", an=2026, luna=6)
    assert r["stare"] == "valid", "DUK a respins D301 achizitie IC: %s" % r.get("erori")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d301_n1_curs_absent_ridica(conn_d301):
    """MUTATIE (gard existent calc_baza): curs absent -> nu se fabrica tacit curs=1, ridica."""
    with conn_d301.cursor() as cur:
        cur.execute("UPDATE d301_operatiuni SET curs=NULL")
    with pytest.raises(Exception):
        _d301.genereaza(conn_d301, _SCHEMA_C, Perioada(2026, luna=6))
