# -*- coding: utf-8 -*-
"""[deficiența 418, comanda Costin 9.3, 19.10.2026] Import e-Factura XML (F1, DNT-TEST-1019):
  a) „Aplicația spune «Furnizorul e înregistrat în scopuri de TVA — din XML nu se află» și cere statutul de mână. Statutul se află din XML
     (CompanyID cu prefix RO în PartyTaxScheme/VAT) și din verificarea ANAF [...]; TVA la încasare se verifică în registrul ANAF.”
  b) „Un singur cont pentru toată factura [...] Fiecare linie trebuie să se poată conta pe contul ei.”
Temei: CF art.316 (înregistrarea în scopuri de TVA, codul cu prefixul RO); EN 16931 BT-31 (codul de TVA al vânzătorului, BR-S-02);
HG 1/2016 titlul VII pct.67 alin.(6) (regimul furnizorului „la data emiterii unei facturi”); OMFP 1802/2014 (funcțiunea conturilor 371 /
6028: marfa intră în stoc, materialul consumabil e cheltuială). ANAF e SIMULAT (niciodată real în teste).
Schemă efemeră din template, în tranzacție anulată."""
import contextlib
import hashlib
import io
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

from core import anaf_api, db as _db, efactura_import as _ef, tenant_provisioning as _tprov

STATUT_FURNIZOR_REAL = True   # ANAF îl simulează testul însuși (core/conftest.py)

_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>DNT-TEST-1019</cbc:ID><cbc:IssueDate>2026-10-19</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>DANTE INTERNATIONAL SA</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
 <cac:AccountingCustomerParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO9010105</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>F1 SRL</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingCustomerParty>
 <cac:TaxTotal><cbc:TaxAmount currencyID="RON">143.52</cbc:TaxAmount></cac:TaxTotal>
 <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount currencyID="RON">827.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">10</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">483.50</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Marfa A</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">48.35</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">5</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">200.00</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Carte tehnica</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">40.00</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
</Invoice>"""


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _anaf(platitor, incasare):
    def interogare(cuii, data_interogare=None):
        return [{"cui": "".join(ch for ch in c if ch.isdigit()), "gasit": True, "platitor_tva": platitor, "tva_la_incasare": incasare}
                for c in cuii]
    return interogare


def _jos(*a, **k):
    raise OSError("ANAF simulat indisponibil")


# ── a) statutul furnizorului ─────────────────────────────────────────────────────────────────────────────
def test_codul_de_tva_al_furnizorului_se_citeste_din_xml():
    f = _ef.parseaza_xml(_XML.encode(), "RO9010105")
    assert (f["directie"], f["tert_cui"], f["furnizor_cod_tva"]) == ("primita", "RO14399840", "RO14399840")


def test_statutul_vine_din_anaf_la_data_facturii():
    st = anaf_api.statut_furnizori([("RO14399840", "2026-10-19", "RO14399840")], interogare=_anaf(True, True))
    assert st == {("RO14399840", "2026-10-19"): {
        "platitor_tva": True, "sursa_platitor": "ANAF, registrul contribuabililor la 19.10.2026",
        "tva_la_incasare": True, "sursa_incasare": "ANAF, Registrul persoanelor care aplică TVA la încasare, la 19.10.2026"}}, st


def test_fara_anaf_ramane_xml_ul_iar_ce_nu_transeaza_se_cere():
    st = anaf_api.statut_furnizori([("RO14399840", "2026-10-19", "RO14399840"), ("123", "2026-10-19", None)], interogare=_jos)
    assert st[("RO14399840", "2026-10-19")] == {"platitor_tva": True, "tva_la_incasare": None, "sursa_incasare": None,
                                                 "sursa_platitor": "XML-ul facturii: codul de TVA RO14399840 al furnizorului (BT-31)"}
    assert st[("123", "2026-10-19")] == {"platitor_tva": None, "sursa_platitor": None, "tva_la_incasare": None, "sursa_incasare": None}


# ── b) contul pe linie, de capăt la capăt ────────────────────────────────────────────────────────────────
class _ConnProxy:
    def __init__(self, real): object.__setattr__(self, "_real", real)
    def __getattr__(self, n): return getattr(self._real, n)
    def commit(self): pass
    def rollback(self): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_validarea_conteaza_fiecare_linie_pe_contul_ei_si_ia_statutul_din_anaf(monkeypatch):
    """Marfa A pe 371 (contul facturii; intră în stoc), Carte tehnica pe 6028 (contul liniei; nu intră în stoc); statutul furnizorului
    (plătitor, TVA la încasare) din ANAF simulat — corpul cererii nu-l mai poartă."""
    from core import uc_tenants
    _db.init_pool()
    SCH = "efemer_418_import"
    c = _db.pool().getconn()
    try:
        with c.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('EF 418') RETURNING id"); fid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_418@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,)); uid = cur.fetchone()["id"]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'F1 SRL','9010105',%s,true) RETURNING id", (SCH, fid)); tid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (uid, tid))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute('INSERT INTO "%s".firma_profil (id,nume,cui,platitor_tva) VALUES (1,%%s,%%s,true)' % SCH, ("F1 SRL", "RO9010105"))
            cur.execute('INSERT INTO "%s".efactura_primite (id_mesaj_anaf,cif_emitent,cif_beneficiar,tip,xml_brut,xml_sha256,status,importat_la) '
                        "VALUES ('EF-418','RO14399840','RO9010105','factura',%%s,%%s,'descarcata',now()) RETURNING id" % SCH,
                        (_XML, hashlib.sha256(_XML.encode()).hexdigest())); pid = cur.fetchone()["id"]

        @contextlib.contextmanager
        def _fake(schema=None):
            with c.cursor() as cc:
                cc.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield _ConnProxy(c)
        monkeypatch.setattr(_db, "get_conn", _fake)
        monkeypatch.setattr(anaf_api, "valideaza_cui", _anaf(True, False))
        ctx = {"uid": uid, "rol": "admin_firma", "accounting_firm_id": fid}
        r = uc_tenants.factura_primita_valideaza(tid, pid, {"cont": "371", "destinatii": ["taxabil", "taxabil"], "conturi": ["", "6028"],
                                                            "tert_tara": "RO"}, ctx)
        assert r["stare"] == "validata", r
        with c.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("SELECT tert_platitor_tva, furnizor_tva_incasare FROM facturi WHERE id = %s", (r["factura_id"],))
            assert cur.fetchone() == (True, False)                                   # din ANAF, nu din cerere
            cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                        "WHERE i.factura_id = %s ORDER BY l.cont_debit", (r["factura_id"],))
            assert cur.fetchall() == [("371", "401", Decimal("483.50")), ("4426", "401", Decimal("42.00")),
                                      ("4426", "401", Decimal("101.54")), ("6028", "401", Decimal("200.00"))]
            cur.execute("SELECT a.denumire, m.cantitate, m.valoare FROM miscari_stoc m JOIN articole a ON a.id = m.articol_id ORDER BY m.id")
            assert cur.fetchall() == [("Marfa A", Decimal("10.000"), Decimal("483.50"))]   # cartea nu intră în stoc
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback()
        _db.pool().putconn(c)
