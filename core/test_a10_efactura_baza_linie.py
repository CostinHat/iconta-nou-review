# -*- coding: utf-8 -*-
"""[A10, 18.09.2026] Import e-Factura: baza liniei = `LineExtensionAmount` (netul UBL după
`AllowanceCharge` și cu `BaseQuantity` aplicat), nu `cantitate × PriceAmount` brut.

Constatarea A10: `efactura_import.parseaza_xml` citea doar `InvoicedQuantity × PriceAmount`, ignorând
`LineExtensionAmount`, `AllowanceCharge`, `BaseQuantity`. O reducere pe linie sau un preț „la 1000 buc"
supradeclara baza care ajunge în D300/D394 (declarațiile citesc liniile, nu antetul). PICĂ pe codul de
dinainte (baza 1.000 / factor × 1000), TRECE după (baza reală din LineExtensionAmount).
"""
from __future__ import annotations

from decimal import Decimal

from core import efactura_import

_UBL = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>FCT-A10-1</cbc:ID>
  <cbc:IssueDate>2026-09-10</cbc:IssueDate>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>FURNIZOR SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO40372003</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>CLIENT SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount>168</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount>968</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity>10</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount>800</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>100</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Produs cu reducere</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity>50</cbc:InvoicedQuantity>
    <cac:Price><cbc:PriceAmount>1000</cbc:PriceAmount><cbc:BaseQuantity>1000</cbc:BaseQuantity></cac:Price>
    <cac:Item><cbc:Name>Carburant la 1000</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
</Invoice>"""


def _baza(l):
    return Decimal(str(l["cantitate"])) * Decimal(str(l["pret_unitar"]))


def test_baza_liniei_e_line_extension_amount_nu_cantitate_x_pret():
    fact = efactura_import.parseaza_xml(_UBL.encode("utf-8"), "40372003")
    linii = fact["linii"]
    assert len(linii) == 2
    # Linia 1: reducere -> LineExtensionAmount 800, NU 10 x 100 = 1.000.
    assert _baza(linii[0]) == Decimal(800), (
        "baza liniei cu reducere = %s (așteptat 800 din LineExtensionAmount; 1.000 = bug cantitate×preț)"
        % _baza(linii[0]))
    # Linia 2: pret la 1000 buc (BaseQuantity=1000) -> 50 x (1000/1000) = 50, NU 50 x 1000 = 50.000.
    assert _baza(linii[1]) == Decimal(50), (
        "baza liniei cu BaseQuantity=1000 = %s (așteptat 50; 50.000 = bug preț per unitate)"
        % _baza(linii[1]))
