# -*- coding: utf-8 -*-
"""Garda anti-ruptura seed<->control (plimbare vizuala 14.08.2026).

Cauza-radacina comuna a constatarilor 2/3/5: fiecare capat (seed/generator vs control) a fost testat
separat, cu conventia LUI; nimic nu rula legatura. Aici acoperim legatura:
 #2 tip_decont litera ('T'/'L', cum scrie seedul) -> controlul emite D300/D394 (nu gri 'necompletat').
 #3 achizitie IC inregistrata ca FACTURA la un neplatitor -> controlul emite D301 (nu doar tabelul manual).
"""
import datetime
import pytest
from core import control_fiscal_api as cf
from core import db as _db, tenant_provisioning as _tp


# ---------- #2: controlul accepta tip_decont ca LITERA (conventia seedului) ----------

@pytest.mark.parametrize("litera,cuvant", [("T", "trimestrial"), ("L", "lunar")])
def test_control_accepta_tip_decont_litera_ca_seedul(litera, cuvant):
    """Seedul (date_test/seed/transa2_coerenta_tva.py) scrie tip_decont='T'/'L'. Controlul folosea
    egalitate stricta pe cuvant -> D300/D394 cadeau pe gri la TOTI cei 7 platitori. Litera trebuie
    acceptata identic cu cuvantul intreg (ca generatoarele, prin perioada_tva_tip)."""
    vec = {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": litera,
           "operatiuni_ic": False, "partida_simpla": False}
    out = cf.declaratii_datorate(vec, are_salariati=False, azi=datetime.date(2026, 2, 1))
    tipuri = {d["tip"] for d in out["datorate"]}
    neclar = {n["tip"] for n in out["neclar"]}
    assert "d300" in tipuri, "%s (litera): D300 respins ca 'necompletat' -> %r" % (cuvant, neclar)
    assert "d394" in tipuri, "%s (litera): D394 respins ca 'necompletat'" % cuvant
    # cuvantul intreg (calea de productie) da acelasi rezultat
    vec["tip_decont"] = cuvant
    out2 = cf.declaratii_datorate(vec, are_salariati=False, azi=datetime.date(2026, 2, 1))
    assert {d["tip"] for d in out2["datorate"]} >= {"d300", "d394"}, "%s (cuvant) difera de litera" % cuvant


# ---------- #3: achizitie IC ca FACTURA la neplatitor -> D301 (nu doar d301_operatiuni) ----------

_SCHEMA = "test_ruptura_d301_factura"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_neplatitor_factura_ic():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,caen,platitor_tva,tip_decont,operatiuni_ic,"
                            "adresa,oras,judet,banca,iban,telefon,declarant_nume,declarant_prenume,declarant_functie) "
                            "VALUES (1,'N1 NEPLATITOR SRL','95451848','4791',false,'trimestrial',true,"
                            "'Str 1','Buc','B','BCR','RO49RNCB0000000000000001','0700000000',"
                            "'Ionescu','Ana','ADMINISTRATOR')")
                # achizitie IC de bunuri de la furnizor UE, inregistrata ca FACTURA (flux normal) -
                # NIMIC in d301_operatiuni. Inainte de fix: controlul spunea "nicio operatiune IC inregistrata".
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,tert_platitor_tva,"
                            "total,tva,taxare_inversa) VALUES ('DE9','2026-06-15','primita','DE136695976',"
                            "'BAUHAUS GMBH',false,15000,0,false)")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d301_neplatitor_factura_ic_declanseaza(conn_neplatitor_factura_ic):
    """Neplatitor cu achizitie IC ca factura (fara rand in d301_operatiuni) -> control emite D301 datorat."""
    vec = {"platitor_tva": False, "operatiuni_ic": True, "regim_fiscal": "profit", "partida_simpla": False}
    out = cf.declaratii_fapt(conn_neplatitor_factura_ic, _SCHEMA, vec, azi=datetime.date(2026, 8, 14))
    datorate = [(d["tip"], d["an"], d["luna"]) for d in out["datorate"]]
    motive_neapl = " ".join(n["motiv"] for n in out["neaplicabile"] if n["tip"] == "d301")
    assert ("d301", 2026, 6) in datorate, (
        "D301 nu s-a declansat din factura IC; datorate=%r; neaplicabil=%r" % (datorate, motive_neapl))
