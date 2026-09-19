# -*- coding: utf-8 -*-
"""A12b — destinatia TVA per LINIE, aleasa de contabil la validarea unei facturi primite din SPV.

Temei: CF art.300 alin.(5) — pro-rata se aplica DOAR achizitiilor cu destinatie MIXTA (folosite si
pentru operatiuni cu drept de deducere, si pentru operatiuni fara). O achizitie pur taxabila se
deduce integral (alin.3); una scutita nu se deduce (alin.4). Fara clasificarea per linie, D300
prorata TOT (bugul A12). A12a a adaugat coloana `factura_linii.destinatie_tva`; A12b o LEAGA de UI:
contabilul o alege la validare, iar `factura_primita_valideaza` o aplica pe liniile importate din XML,
IN ORDINE (destinatii[i] <-> linia i).

Probe end-to-end pe schema efemera din template (gated DB): XML real cu 2 linii -> valideaza cu
`destinatii` -> factura_linii poarta destinatia pe linia corecta, in ordine. + mutatie + calibrari."""
import io
import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import repo_facturi

_SCH = "efemer_a12b_dest"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
pytestmark = pytest.mark.skipif(not _DB, reason="DB indisponibil")

# XML real cu DOUA linii distincte (baza 800 / baza 50), ca sa se vada corespondenta de ORDINE.
_UBL = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>FCT-A12B-1</cbc:ID>
  <cbc:IssueDate>2026-09-10</cbc:IssueDate>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>FURNIZOR SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO40372003</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>GARDA SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount>178.50</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount>1028.50</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity>10</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount>800</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>80</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Linia intai</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity>1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount>50</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>50</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Linia a doua</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
</Invoice>"""


@pytest.fixture()
def conn():
    """Schema efemera din tenant_template.sql, curatata la iesire. Nicio scriere pe date reale."""
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, email,
                           telefon, caen, declarant_nume, declarant_prenume, declarant_functie,
                           platitor_tva)
                           VALUES (1,'GARDA SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722',
                                   '4690','P','I','ADMIN', true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


_MSG = [0]


def _primita(conn):
    _MSG[0] += 1
    with conn.cursor() as cur:
        cur.execute("INSERT INTO efactura_primite (id_mesaj_anaf, cif_emitent, cif_beneficiar, "
                    "xml_brut, xml_sha256, status) VALUES (%s,'RO40372003','RO14399840',%s,%s,"
                    "'descarcata') RETURNING id",
                    ("MSG-A12B-%d" % _MSG[0], _UBL, "sha-%d" % _MSG[0]))
        return cur.fetchone()[0]


def _valideaza(conn, monkeypatch, pid, corp):
    import main
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    return main.factura_primita_valideaza(1, pid, corp, {"uid": 1})


def _dest_linii(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT destinatie_tva FROM factura_linii WHERE factura_id=%s ORDER BY id", (fid,))
        return [r[0] for r in cur.fetchall()]


# ── PROBA: destinatia aleasa la validare ajunge pe linia corecta, in ordine ──
def test_A12b_destinatia_per_linie_ajunge_in_ordine(conn, monkeypatch):
    pid = _primita(conn)
    conn.commit()
    r = _valideaza(conn, monkeypatch, pid, {"cont": "628", "destinatii": ["mixt", "scutit"]})
    fid = r["factura_id"]
    conn.commit()
    dest = _dest_linii(conn, fid)
    assert dest == ["mixt", "scutit"], (  # art.300 alin.(5): doar linia MIXTA intra in prorata
        "destinatia per linie in ordinea liniilor din XML: asteptat [mixt, scutit], gasit %r" % dest)


# ── CALIBRARE: fara alegere -> implicit taxabil (deducere integrala, art.300 alin.3), NU prorata ──
def test_A12b_default_taxabil_cand_nu_se_alege(conn, monkeypatch):
    pid = _primita(conn)
    conn.commit()
    r = _valideaza(conn, monkeypatch, pid, {"cont": "628"})  # fara destinatii
    conn.commit()
    dest = _dest_linii(conn, r["factura_id"])
    assert dest == ["taxabil", "taxabil"], (
        "fara clasificare, achizitia se deduce integral (default sigur), NU prorata: gasit %r" % dest)


# ── CALIBRARE NEGATIVA: o destinatie in afara setului inchis e refuzata, nu scrisa tacit ──
def test_A12b_destinatie_invalida_refuzata(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva) "
                    "VALUES ('F-INV','2026-09-10','primita',100,21) RETURNING id")
        fid = cur.fetchone()[0]
        from core.repo_main import insert_factura_linii
        insert_factura_linii(cur, _SCH, fid, {"descriere": "x", "cantitate": 1,
                                              "pret_unitar": 100, "cota_tva": 21})
        with pytest.raises(ValueError, match="destinatie"):
            repo_facturi.actualizeaza_destinatii_linii(cur, _SCH, fid, ["inventata"])
    conn.rollback()


# ── MUTATIE (probata in raport): daca aplicarea NU respecta ordinea liniilor, testul de ordine PICA.
#    Nu se poate strica codul aici (ar strica poarta); se documenteaza in raport prin
#    inversarea destinatiilor: [scutit, mixt] ar da dest == [scutit, mixt], deci assert-ul de mai sus
#    prinde orice pierdere de corespondenta pozitionala.
def test_A12b_ordinea_inversa_da_rezultat_invers(conn, monkeypatch):
    """Cealalta directie a probei de ordine: inversand alegerea, si rezultatul se inverseaza.
    Fara ea, un cod care ar scrie mereu prima valoare pe toate liniile ar trece testul de mai sus."""
    pid = _primita(conn)
    conn.commit()
    r = _valideaza(conn, monkeypatch, pid, {"cont": "628", "destinatii": ["scutit", "mixt"]})
    conn.commit()
    assert _dest_linii(conn, r["factura_id"]) == ["scutit", "mixt"]
