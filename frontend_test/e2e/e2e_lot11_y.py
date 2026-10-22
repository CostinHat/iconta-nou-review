# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.1 (verbatim în DECIZII „Comanda 11.1”), subagentul Y: C79 — contarea facturii PRIMITE recalcula TVA-ul
deductibil din baze în loc să-l ia de pe factura furnizorului (XML 143,52 lei, nota 143,54 lei).

Temei: CF art.299 alin.(1) lit.a (deducerea cere „o factură emisă în conformitate cu prevederile art. 319”); CF art.319 alin.(20) lit.j
(factura cuprinde „suma taxei colectate, exprimate în lei, în funcție de cotele taxei”). În XML-ul e-Factura: defalcarea BG-23 (BT-117 pe
fiecare BT-119).

Pașii, toți pe ecran / pe rutele ecranelor: Date firmă + vectorul fiscal (`pregateste_firma`) -> Facturi -> „Facturi primite” -> „Importă
XML UBL” (factura furnizorului cu două cote, TVA-ul rotunjit de furnizor pe linii) -> detaliul facturii -> contul 371 -> „Validează” -> nota
-> „Validează” pe nota din Registrul jurnal -> Declarații -> D300 pe luna încheiată. Nimic nu se inserează direct în bază.
Furnizorul: DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md."""
import re

import pytest

from conftest import firma_noua, perioada_incheiata, sql
from e2e_bloc_a import _api, _card, _ok, pregateste_firma

LUNA = perioada_incheiata("lunar")          # D300 se generează numai pe o perioadă încheiată (383)
ZI = LUNA.inceput.replace(day=10)

#: 21%: baza 101,17 + 101,16 = 202,33 — recalcul 42,49, pe factură 42,51; 11%: baza 150,05 — recalcul 16,51, pe factură 16,49
UBL_C79 = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>{numar}</cbc:ID><cbc:IssueDate>{data}</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>DANTE INTERNATIONAL SA</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
 <cac:AccountingCustomerParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO{cui}</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>{client}</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingCustomerParty>
 <cac:TaxTotal><cbc:TaxAmount currencyID="RON">59.00</cbc:TaxAmount>
  <cac:TaxSubtotal><cbc:TaxableAmount currencyID="RON">202.33</cbc:TaxableAmount><cbc:TaxAmount currencyID="RON">42.51</cbc:TaxAmount>
   <cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>
  </cac:TaxSubtotal>
  <cac:TaxSubtotal><cbc:TaxableAmount currencyID="RON">150.05</cbc:TaxableAmount><cbc:TaxAmount currencyID="RON">16.49</cbc:TaxAmount>
   <cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>11</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>
  </cac:TaxSubtotal></cac:TaxTotal>
 <cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount currencyID="RON">352.38</cbc:TaxExclusiveAmount>
  <cbc:TaxInclusiveAmount currencyID="RON">411.38</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">101.17</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Marfa A C79</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">101.17</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">101.16</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Marfa B C79</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">101.16</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">150.05</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Carte C79</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>11</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">150.05</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
</Invoice>"""


@pytest.fixture()
def firma_y():
    for f in firma_noua():
        yield f


def _atr(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


def test_def_c79_nota_si_d300_iau_tva_ul_de_pe_factura_furnizorului(patron, firma_y):
    """C79. Pașii: Facturi -> „Facturi primite” -> „Importă XML UBL” (factura furnizorului: 21% TVA 42,51 pe baza 202,33; 11% TVA 16,49 pe
    baza 150,05) -> detaliul -> contul 371 -> „Validează” -> confirmă: nota are 4426 = 401 42,51 și 4426 = 401 16,49 — TVA-ul de pe factură,
    nu recalculul 42,49 / 16,51 —, iar 401 închide totalul facturii 411,38 -> „Validează” pe notă -> Declarații -> D300 pe luna încheiată:
    rd.24 (R22) TVA 43, rd.25 (R23) TVA 16 (recalculul ar fi dat 42 / 17) și decontul trece de a doua cale (d300_reconciliere)."""
    import time as _t
    from e2e_bloc_d import _genereaza
    s, tid = firma_y["schema"], firma_y["tenant_id"]
    pregateste_firma(patron, firma_y, platitor=True, regim_fiscal="profit")
    tag = "E2EC79-%d" % _t.time()
    cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % s)[0][0] if c.isdigit())
    patron.firma(firma_y["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg = patron.pg
    pg.click("#fac-primite")
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % tag, "mimeType": "text/xml", "buffer": UBL_C79.format(
        numar=tag, data=ZI.isoformat(), client=firma_y["nume"], cui=cifre).encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=40000)
    pg.locator(".fac-primita-btn", has_text=tag).click()
    pg.wait_for_selector("#pr-cont", timeout=20000)
    pg.fill("#pr-cont", "371")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    patron.captura("validata")
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % s, (tag,))[0][0]
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i '
               "ON i.id = l.inregistrare_id WHERE i.factura_id = %%s ORDER BY l.id" % (s, s), (fid,))
    # CF art.299 alin.(1) lit.a + art.319 alin.(20) lit.j: TVA-ul cotei de pe factura furnizorului
    assert [n for n in note if n[0] == "4426"] == [("4426", "401", "16.49"), ("4426", "401", "42.51")], note
    assert sum(float(n[2]) for n in note if n[1] == "401") == pytest.approx(411.38), note   # BT-112 al facturii
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE status <> \'validata\' AND data >= %%s AND data <= %%s ORDER BY id' % s,
                      (LUNA.inceput, LUNA.sfarsit)):
        _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {}), "validarea notei %s" % nid)
    _genereaza(patron, firma_y, "d300", LUNA.an, LUNA.luna)
    patron.captura("pas2_d300")
    assert not pg.locator(".fereastra:last-of-type .dec-eroare").count(), patron.fereastra()[:3000]
    xml = pg.eval_on_selector(".fereastra:last-of-type details.dec-xml pre.dec-xml-pre", "el => el.textContent")
    # D300 rd.24 / rd.25, col.2 = TVA-ul deductibil de pe facturi (42,51 -> 43; 16,49 -> 16)
    assert (_atr(xml, "R22_1"), _atr(xml, "R22_2"), _atr(xml, "R23_1"), _atr(xml, "R23_2")) == ("202", "43", "150", "16"), xml[:3000]
