# -*- coding: utf-8 -*-
"""[deficiența 417, retestul Costin 19.10.2026, PRIORITAR] „PDF F1A9 fără trimitere la factura stornată: «Stornare factura F1A nr. 8 din
19.10.2026» (CF art.319 alin.20, art.330), și în XML e-Factura.”

Temei: CF art.330 alin.(1) lit.b): „[...] se emite o factură cu valorile cu semnul minus [...] în care se înscriu numărul și data
facturii corectate”; CF art.319 alin.(20) lit.r): „o referire la alte facturi sau documente emise anterior, atunci când se emit mai multe
facturi ori documente pentru aceeași operațiune” (anaf_surse/cod_fiscal_227_2015_consolidat.txt). În e-Factura: BG-3 (BT-25 numărul,
BT-26 data facturii anterioare) — `cac:BillingReference/cac:InvoiceDocumentReference`, plus mențiunea în BT-22.
Schemă efemeră din template, în tranzacție anulată."""
import io
import xml.etree.ElementTree as ET

import pytest

from core import db as _db, efactura_send as _ef, efactura_trimitere as _et, facturi as _fc, factura_pdf as _pdf
from core import firma_profil_api as _fp, tenant_provisioning as _tp

_SCHEMA = "tenant_test_417_storno"
_NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
       "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
_LINIE = {"descriere": "Marfa B", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "um": "buc", "cont_venit": "707"}


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
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, regim_fiscal, "
                            "platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie, reg_com) VALUES (1,'F1 SRL',"
                            "'14399840','Str Test 1','Sector 1','B','4690','0722000000','BCR','RO49AAAA1B31007593840000','real',true,"
                            "'L','Popescu','Ion','ADMINISTRATOR','J40/1/2020')")
                cur.execute("UPDATE firma_profil SET forma_juridica = 'SRL', capital_subscris = 200, serie_factura = 'F1A', "
                            "metoda_stoc = 'global_valoric' WHERE id = 1")
            yield c
        finally:
            c.rollback()


def _storno(conn):
    from core import facturi_api
    r = facturi_api.creeaza_factura(conn, "F1A8", "2026-10-19", "emisa", [dict(_LINIE)], data_scadenta="2026-11-18",
                                    tert_nume="DANTE INTERNATIONAL SA",
                                    tert_cui="RO14399840", tert_adresa="Str. Test 2", tert_oras="Sector 2", tert_judet="B",
                                    status="emisa")
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET serie = 'F1A' WHERE id = %s", (r["factura_id"],))
    s = facturi_api.storneaza(conn, r["factura_id"])
    return r, s, facturi_api.detalii_factura(conn, s["factura_id"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pdf_stornarii_numeste_factura_stornata(conn):
    from pypdf import PdfReader
    _r, _s, d = _storno(conn)
    assert _fc.mentiune_storno(d) == "Stornare factura F1A nr. 8 din 19.10.2026"
    text = " ".join(" ".join(p.extract_text().split()) for p in PdfReader(io.BytesIO(_pdf.genereaza_pdf(_fp.citeste_profil(conn), d))).pages)
    assert text.count("Stornare factura F1A nr. 8 din 19.10.2026") == 1, text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_xml_efactura_poarta_referinta_bg3_si_mentiunea(conn):
    _r, s, _d = _storno(conn)
    xml, _f = _et.genereaza_din_factura(conn, _SCHEMA, s["factura_id"])
    rad = ET.fromstring(xml.encode("utf-8"))
    ref = rad.findall("cac:BillingReference/cac:InvoiceDocumentReference", _NS)
    assert [(x.findtext("cbc:ID", namespaces=_NS), x.findtext("cbc:IssueDate", namespaces=_NS)) for x in ref] == [("F1A8", "2026-10-19")]
    assert [n.text for n in rad.findall("cbc:Note", _NS)] == ["Stornare factura F1A nr. 8 din 19.10.2026"]
    # ordinea schemei UBL Invoice-2: BillingReference după DocumentCurrencyCode, înaintea părților
    copii = [c.tag.split("}")[1] for c in rad]
    assert copii.index("DocumentCurrencyCode") < copii.index("BillingReference") < copii.index("AccountingSupplierParty"), copii
    # stornarea poartă orașul și județul clientului (BT-52 / BT-54; validatorul FACT1: BR-RO-110 fără ele)
    adr = rad.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress", _NS)
    assert (adr.findtext("cbc:CityName", namespaces=_NS), adr.findtext("cbc:CountrySubentity", namespaces=_NS)) == (
        "SECTOR2", "RO-B"), ET.tostring(adr)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_obisnuita_n_are_trimitere(conn):
    r, _s, _d = _storno(conn)
    from core import facturi_api
    d = facturi_api.detalii_factura(conn, r["factura_id"])
    assert d["storno_din"] is None and _fc.mentiune_storno(d) is None
    xml, _f = _et.genereaza_din_factura(conn, _SCHEMA, r["factura_id"])
    rad = ET.fromstring(xml.encode("utf-8"))
    assert rad.findall("cac:BillingReference", _NS) == [] and rad.findall("cbc:Note", _NS) == []
    assert _ef.INVOICE_TYPE_FACTURA == rad.findtext("cbc:InvoiceTypeCode", namespaces=_NS)
