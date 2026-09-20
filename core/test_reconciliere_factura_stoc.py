# -*- coding: utf-8 -*-
"""GARD (reconciliere factură->stoc, 21.09.2026): validarea unei facturi PRIMITE de marfă creează ȘI
intrarea cantitativă în fișa de magazie, legată prin `factura_id` — o singură recepție = notă contabilă
(din factură: 371=401, 4426=401) + cantitate (fișa de magazie). Fără asta, 371-contabil urca dar fișa nu
se mișca (divergență GL<->fișă = finding SPV<->stoc, DECIZII 20.09). `intrare_din_factura` e cantitate-DOAR
(NU dublează nota, care vine din factură) și idempotentă pe factura_id.

CE FACE IMPOSIBIL:
  * ca o factură primită de marfă (cont de stoc) să lase fișa de magazie nemișcată (divergență silențioasă);
  * ca a doua chemare să creeze a doua intrare (idempotență pe factura_id);
  * ca articolul existent să fie duplicat (potrivire pe denumire);
  * ca hook-ul din validarea facturii primite să dispară (test structural).
RED-PROOF: fără `factura_id` în INSERT / fără logica de intrare, testele pică (mutație verificată manual).

CE NU FACE, declarat: nu testează calculul CMP (aia e `test_stocuri_cv.py`), nici D300 (aia e `test_d300.py`);
verifică DOAR că recepția mișcă și fișa, o singură dată, pe articolul potrivit.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import facturi_api as _fa
from core import stocuri_cv_api as _cv

_SCH = "efemer_reconc_fact_stoc"

LINII_MARFA = [{"descriere": "Marfa A", "cantitate": 20, "pret_unitar": 50, "cota_tva": 21}]


@pytest.fixture()
def conn():
    """Schemă efemeră din tenant_template.sql, curățată la ieșire. Nicio scriere pe date reale."""
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, email, telefon,
                           caen, declarant_nume, declarant_prenume, declarant_functie, platitor_tva)
                           VALUES (1,'RECONC SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722','4711',
                                   'P','I','ADMIN', true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _factura_marfa(conn):
    r = _fa.creeaza_factura(conn, "F-001", "2099-09-20", "primita", LINII_MARFA,
                            tert_nume="Furnizor SRL", tert_cui="RO14399840")
    return r["factura_id"] if isinstance(r, dict) else r


def _fisa(conn, cont="371"):
    with conn.cursor() as cur:
        cur.execute("""SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate ELSE -cantitate END),0),
                              COALESCE(SUM(CASE WHEN tip='intrare' THEN valoare ELSE -valoare END),0)
                       FROM miscari_stoc m JOIN articole a ON a.id=m.articol_id
                       WHERE a.cont_stoc=%s""", (cont,))
        return cur.fetchone()


def test_intrare_din_factura_misca_fisa(conn):
    fid = _factura_marfa(conn)
    assert _fisa(conn)[0] == 0                       # fișa e goală înainte
    r = _cv.intrare_din_factura(conn, _SCH, fid, "371", "2099-09-20")
    conn.commit()
    assert r["linii"] == 1
    cant, val = _fisa(conn)
    assert cant == Decimal("20")                     # 20 buc intrate
    assert val == Decimal("1000.00")                 # 20 x 50 = valoarea notei 371=401 (fără divergență)
    with conn.cursor() as cur:
        cur.execute("SELECT factura_id FROM miscari_stoc WHERE tip='intrare'")
        assert cur.fetchone()[0] == fid              # legat de factură


def test_intrare_din_factura_idempotent(conn):
    fid = _factura_marfa(conn)
    _cv.intrare_din_factura(conn, _SCH, fid, "371", "2099-09-20"); conn.commit()
    r2 = _cv.intrare_din_factura(conn, _SCH, fid, "371", "2099-09-20"); conn.commit()
    assert r2["stare"] == "deja_intrat" and r2["linii"] == 0
    assert _fisa(conn)[0] == Decimal("20")           # NU s-a dublat


def test_intrare_din_factura_potriveste_articol_existent(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) "
                    "VALUES ('Marfa A','buc','371','607') RETURNING id")
        aid = cur.fetchone()[0]
    conn.commit()
    fid = _factura_marfa(conn)
    _cv.intrare_din_factura(conn, _SCH, fid, "371", "2099-09-20"); conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM articole WHERE lower(denumire)='marfa a'")
        assert cur.fetchone()[0] == 1                # un singur articol (potrivit, nu duplicat)
        cur.execute("SELECT articol_id FROM miscari_stoc WHERE tip='intrare'")
        assert cur.fetchone()[0] == aid


class _ConnProxy:
    """Conexiunea reală, cu commit/rollback INERTE: tot rămâne în tranzacția probei (rollback la teardown)."""
    def __init__(self, real): object.__setattr__(self, "_real", real)
    def __getattr__(self, n): return getattr(self._real, n)
    def commit(self): pass
    def rollback(self): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False


_XML_MARFA = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>F-9</cbc:ID><cbc:IssueDate>2099-09-20</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>Furnizor SRL</cbc:RegistrationName></cac:PartyLegalEntity>
  <cac:PartyTaxScheme><cbc:CompanyID>RO420002008</cbc:CompanyID></cac:PartyTaxScheme></cac:Party></cac:AccountingSupplierParty>
 <cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>F SRL</cbc:RegistrationName></cac:PartyLegalEntity>
  <cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID></cac:PartyTaxScheme></cac:Party></cac:AccountingCustomerParty>
 <cac:TaxTotal><cbc:TaxAmount currencyID="RON">210.00</cbc:TaxAmount></cac:TaxTotal>
 <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount currencyID="RON">1210.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">20</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">1000.00</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Marfa A</cbc:Name><cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">50.00</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
</Invoice>"""


def test_validarea_facturii_de_marfa_misca_fisa_end_to_end(monkeypatch):
    """GARD pe HOOK (funcțional, nu pe text): `factura_primita_valideaza` cu cont de stoc creează ȘI
    intrarea în fișa de magazie. Tot în tranzacția probei (commit inert), rollback la final — nimic scurs."""
    import contextlib
    import hashlib
    from core import db as _db, uc_tenants
    from psycopg2.extras import RealDictCursor
    _db.init_pool()
    SCH = "efemer_reconc_hook"
    c = _db.pool().getconn()
    try:
        with c.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('EF RECONC') RETURNING id"); fid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_reconc@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,)); uid = cur.fetchone()["id"]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'EF RECONC SRL','14399840',%s,true) RETURNING id", (SCH, fid)); tid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (uid, tid))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute('INSERT INTO "%s".firma_profil (id,nume,cui,platitor_tva) VALUES (1,%%s,%%s,true)' % SCH, ("EF RECONC SRL", "RO14399840"))
            cur.execute('INSERT INTO "%s".efactura_primite (id_mesaj_anaf,cif_emitent,cif_beneficiar,tip,xml_brut,xml_sha256,status,importat_la) '
                        "VALUES ('EF-1','RO420002008','RO14399840','factura',%%s,%%s,'descarcata',now()) RETURNING id" % SCH,
                        (_XML_MARFA, hashlib.sha256(_XML_MARFA.encode()).hexdigest())); pid = cur.fetchone()["id"]

        @contextlib.contextmanager
        def _fake(schema=None):
            with c.cursor() as cc:
                cc.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield _ConnProxy(c)
        monkeypatch.setattr(_db, "get_conn", _fake)
        ctx = {"uid": uid, "rol": "admin_firma", "accounting_firm_id": fid}
        r = uc_tenants.factura_primita_valideaza(tid, pid, {"cont": "371", "destinatii": ["taxabil"], "tert_tara": "RO"}, ctx)
        assert r["stare"] == "validata"
        with c.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("SELECT COALESCE(SUM(cantitate),0), COALESCE(SUM(valoare),0) FROM miscari_stoc WHERE tip='intrare'")
            cant, val = cur.fetchone()
            assert cant == Decimal("20"), "validarea facturii de marfă NU a mișcat fișa (hook lipsă): cant=%s" % cant
            assert val == Decimal("1000.00")
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback()                       # anulează TOT (schema + rândurile publice) — nimic scurs
        _db.pool().putconn(c)
