# -*- coding: utf-8 -*-
"""Teste generator e-Factura SEND (core/efactura_send.py) — pe date minime construite
manual (regula CLAUDE.md: test izolat, nu doar pe date reale). Apara regresiile de
structura + rotunjire. Validarea de structura CIUS reala = upload pe TEST (pasul 2)."""
import xml.etree.ElementTree as ET
import pytest

from core import efactura_send as ef

NS = {
    "": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def _factura_minima(**kw):
    f = {"numar": "0007", "serie": "FCT", "data_emitere": "2026-07-18",
         "data_scadenta": "2026-08-17", "moneda": "RON", "tert_nume": "CLIENT SRL",
         "tert_cui": "RO12345678", "tert_adresa": "Str. Exemplu 1, Cluj",
         "taxare_inversa": False, "tip": "factura", "storno_din_id": None}
    f.update(kw)
    return f


def _furnizor(platitor=True):
    return {"nume": "FIRMA MEA SRL", "cui": "40372004", "reg_com": "J12/1/2020",
            "adresa": "Bd. Test 10, Sector 2", "oras": "Bucuresti", "judet": "Bucuresti",
            "cod_postal": "010101", "iban": "RO49AAAA1B31007593840000", "platitor_tva": platitor}


def _client():
    return {"nume": "CLIENT SRL", "cui": "RO12345678", "adresa": "Str. Exemplu 1, Cluj",
            "oras": None, "judet": None, "cod_postal": None}


def _linii():
    # 2 buc x 100.00 @19% + 1 buc x 50.00 @0%
    return [
        {"descriere": "Serviciu A", "um": "buc", "cantitate": 2, "pret_unitar": "100.00", "cota_tva": 19},
        {"descriere": "Serviciu B", "um": "buc", "cantitate": 1, "pret_unitar": "50.00", "cota_tva": 0},
    ]


def test_xml_bine_format_si_structura():
    xml = ef.genereaza_xml(_factura_minima(), _linii(), _furnizor(), _client())
    root = ET.fromstring(xml)  # arunca daca nu e bine format
    assert root.tag.endswith("}Invoice")
    assert root.find("cbc:CustomizationID", NS).text == ef.CUSTOMIZATION_ID
    assert root.find("cbc:ID", NS).text == "FCT0007"          # serie + numar
    assert root.find("cbc:InvoiceTypeCode", NS).text == "380"
    assert root.find("cbc:DocumentCurrencyCode", NS).text == "RON"


def test_sume_si_rotunjire():
    xml = ef.genereaza_xml(_factura_minima(), _linii(), _furnizor(), _client())
    root = ET.fromstring(xml)
    lmt = root.find("cac:LegalMonetaryTotal", NS)
    # net = 2*100 + 1*50 = 250.00 ; TVA = 200*19% = 38.00 ; total = 288.00
    assert lmt.find("cbc:LineExtensionAmount", NS).text == "250.00"
    assert root.find("cac:TaxTotal/cbc:TaxAmount", NS).text == "38.00"
    assert lmt.find("cbc:TaxInclusiveAmount", NS).text == "288.00"


def test_rotunjire_half_up_nu_bankers():
    # 2.125 -> 2.13 (ROUND_HALF_UP), NU 2.12 (bankers/half-even)
    assert str(ef._bani("2.125")) == "2.13"
    assert str(ef._bani("2.135")) == "2.14"


def test_vat_supplier_doar_daca_platitor():
    xml_da = ef.genereaza_xml(_factura_minima(), _linii(), _furnizor(platitor=True), _client())
    xml_nu = ef.genereaza_xml(_factura_minima(), _linii(), _furnizor(platitor=False), _client())
    sup_da = ET.fromstring(xml_da).find("cac:AccountingSupplierParty/cac:Party", NS)
    sup_nu = ET.fromstring(xml_nu).find("cac:AccountingSupplierParty/cac:Party", NS)
    assert sup_da.find("cac:PartyTaxScheme/cbc:CompanyID", NS).text == "RO40372004"
    assert sup_nu.find("cac:PartyTaxScheme", NS) is None


def test_taxare_inversa_neimplementata_v1():
    with pytest.raises(NotImplementedError):
        ef.genereaza_xml(_factura_minima(taxare_inversa=True), _linii(), _furnizor(), _client())


def test_bucuresti_cu_sector_devine_SECTORn():
    xml = ef.genereaza_xml(_factura_minima(), _linii(), _furnizor(), _client())
    sup = ET.fromstring(xml).find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress", NS)
    assert sup.find("cbc:CityName", NS).text == "SECTOR2"          # derivat din 'Sector 2'
    assert sup.find("cbc:CountrySubentity", NS).text == "RO-B"


def test_localitate_stricta_blocheaza_fara_sector():
    # Bucuresti (RO-B) fara sector in oras/adresa -> EDateIncomplete, NU se inventeaza sector
    furn = _furnizor()
    furn["adresa"] = "Bd. Fara Sector 999"   # niciun 'Sector N'
    with pytest.raises(ef.EDateIncomplete):
        ef.genereaza_xml(_factura_minima(), _linii(), furn, _client())


def test_host_o_singura_constanta():
    # host OAuth verificat LIVE 18.07 = api.anaf.ro (webserviceapl = mTLS, TLS handshake fail)
    assert ef.fctel_base("prod") == "https://api.anaf.ro/prod/FCTEL/rest"
    assert ef.fctel_base("test") == "https://api.anaf.ro/test/FCTEL/rest"
    assert ef.fctel_base("orice") == "https://api.anaf.ro/prod/FCTEL/rest"  # fallback prod
    assert "webserviceapl" not in ef.FCTEL_BASE_TPL   # ruta mTLS, nu OAuth
    # validatorul de structura pe host propriu, fara token
    assert "webservicesp.anaf.ro" in ef.FCTEL_VALIDARE_TPL
