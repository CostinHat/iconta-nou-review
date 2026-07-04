# -*- coding: utf-8 -*-
import io, zipfile
import pytest
from core import efactura_import as m

XML = '''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
<cbc:ID>F123</cbc:ID><cbc:IssueDate>2026-02-10</cbc:IssueDate>
<cbc:DueDate>2026-03-10</cbc:DueDate>
<cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
<cac:AccountingSupplierParty><cac:Party>
<cac:PartyTaxScheme><cbc:CompanyID>RO11111111</cbc:CompanyID></cac:PartyTaxScheme>
<cac:PartyLegalEntity><cbc:RegistrationName>FURNIZOR SRL</cbc:RegistrationName></cac:PartyLegalEntity>
</cac:Party></cac:AccountingSupplierParty>
<cac:AccountingCustomerParty><cac:Party>
<cac:PartyTaxScheme><cbc:CompanyID>RO34142700</cbc:CompanyID></cac:PartyTaxScheme>
<cac:PartyLegalEntity><cbc:RegistrationName>KAI PERFORMANCE SRL</cbc:RegistrationName></cac:PartyLegalEntity>
</cac:Party></cac:AccountingCustomerParty>
<cac:TaxTotal><cbc:TaxAmount currencyID="RON">210.00</cbc:TaxAmount></cac:TaxTotal>
<cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount currencyID="RON">1210.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
<cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">2</cbc:InvoicedQuantity>
<cac:Item><cbc:Name>Piese auto</cbc:Name>
<cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
<cac:Price><cbc:PriceAmount currencyID="RON">500.00</cbc:PriceAmount></cac:Price>
</cac:InvoiceLine></Invoice>'''

def test_primita():
    f = m.parseaza_xml(XML, "RO34142700")
    assert f["directie"] == "primita"
    assert f["tert_cui"] == "RO11111111" and f["tert_nume"] == "FURNIZOR SRL"
    assert f["numar"] == "F123" and f["total"] == "1210.00" and f["tva"] == "210.00"
    assert f["linii"][0]["cota_tva"] == "21"

def test_emisa():
    f = m.parseaza_xml(XML, "11111111")
    assert f["directie"] == "emisa"
    assert f["tert_cui"] == "RO34142700"

def test_xml_invalid():
    with pytest.raises(ValueError, match="XML invalid"):
        m.parseaza_xml("<broken", "RO1")

def test_nu_e_invoice():
    with pytest.raises(ValueError, match="Invoice"):
        m.parseaza_xml("<Alt/>", "RO1")

def test_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("factura.xml", XML)
        z.writestr("semnatura_factura.xml", "<sig/>")
        z.writestr("altceva.txt", "x")
    out = m.extrage_fisiere("arhiva.zip", buf.getvalue())
    assert len(out) == 1 and out[0][0] == "factura.xml"

def test_xml_direct():
    out = m.extrage_fisiere("f.xml", b"<Invoice/>")
    assert out == [("f.xml", b"<Invoice/>")]
