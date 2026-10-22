# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1” pct.20) — subagentul K (integrare): deficiența 444
(„când numele de la ANAF diferă de fișa partenerului, se spune și se propune actualizarea”) pe ultimele două drumuri care verifică
partenerul la ANAF: EMITEREA facturii („Verifică” lângă CUI-ul clientului) și IMPORTUL e-Factura (detaliul facturii primite). NIR-ul și
casa sunt în e2e_lot11_p2.py, ecranul fișelor în e2e_lot11_p.py.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`, Date firmă pe drumul ecranului —
`e2e_bloc_e._completeaza`). DATE DE PORNIRE: fișa partenerului cu numele vechi, pe ruta ecranului Clienți / Furnizori (POST); răspunsul
ANAF e servit de plasă pe server (`anaf_api.CHEIE_SIMULAT`, `<dir>/anaf.json`), deci comparația fișă–ANAF rulează în aplicație.
CUI-urile 14399840 / 2864518 au cifra de control verificată (algoritmul din CLAUDE.md). Mutațiile: frontend_test/e2e/mut_lot11_k.json."""
import time

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _card, _deschide_emiterea
from e2e_lot11_p2 import _anaf, _fisa, _verifica

UBL_DANTE = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>{numar}</cbc:ID><cbc:IssueDate>2026-10-10</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>DANTE SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme></cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>{client}</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO{cui}</cbc:CompanyID></cac:PartyTaxScheme></cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount>21.00</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount>121.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine><cbc:InvoicedQuantity>1</cbc:InvoicedQuantity><cbc:LineExtensionAmount>100</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>100</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Servicii E2E 444</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
</Invoice>"""


@pytest.fixture(scope="module")
def firma_k():
    from e2e_bloc_e import _completeaza
    for f in firma_noua():
        yield _completeaza(f, "global_valoric")


def test_def_444_emiterea_propune_actualizarea_fisei_clientului(patron, firma_k):
    """444 (emiterea facturii). Pașii: fișa clientului „ALTEX SRL” (CUI 2864518) -> Facturi -> „Emite factură” -> CUI 2864518, numele
    scris „ALTEX SRL” -> „Verifică”: numele din ANAF în formular și „Numele de la ANAF diferă: «ALTEX ROMANIA SRL» (în fișă: «ALTEX SRL»).”
    cu „Actualizează fișa cu numele de la ANAF” -> clic -> „ALTEX SRL: numele din fișă e acum «ALTEX ROMANIA SRL»”, fișa are numele de la
    ANAF -> „Verifică” din nou: nicio propunere."""
    _anaf()
    cl = _fisa(firma_k, "clienti", "ALTEX SRL", "2864518")
    # date de pornire, pe ruta ecranului „Configurare emitere” (ca e2e_lot11_d3): firma nouă n-are numerotarea, iar „Emite factură” ar
    # deschide întâi configurarea, nu formularul — testul e despre comparația fișă–ANAF, nu despre configurare
    from e2e_bloc_a import _api, _ok
    _ok(_api(patron, "PUT", "/tenants/%d/facturi/numerotare" % firma_k["tenant_id"], {"serie": "K444", "numar_start": 1}), "numerotarea")
    _deschide_emiterea(patron, firma_k["nume"])
    pg = patron.pg
    pg.fill("#em-cui", "2864518")
    pg.fill("#em-nume", "ALTEX SRL")
    _verifica(pg, "#em-verifica", "#em-cui-stare")
    buton = "#em-anaf-aplica-clienti-%d" % cl
    pg.wait_for_selector(buton, timeout=15000)
    st = pg.inner_text("#em-cui-stare")
    assert "Numele de la ANAF diferă: „ALTEX ROMANIA SRL” (în fișă: „ALTEX SRL”)." in st, st
    assert pg.input_value("#em-nume") == "ALTEX ROMANIA SRL"
    patron.captura("emitere_diferit")
    pg.click(buton)
    pg.wait_for_function("() => (document.querySelector('#em-cui-stare') || {innerText: ''}).innerText.includes('numele din fișă e acum')",
                         timeout=30000)
    assert sql('SELECT nume FROM "%s".clienti WHERE id = %%s' % firma_k["schema"], (cl,)) == [("ALTEX ROMANIA SRL",)]
    patron.captura("emitere_actualizat")
    _verifica(pg, "#em-verifica", "#em-cui-stare")
    assert pg.query_selector("[id^='em-anaf-aplica-']") is None and "diferă" not in pg.inner_text("#em-cui-stare")


def test_def_444_importul_efactura_propune_actualizarea_fisei_furnizorului(patron, firma_k):
    """444 (importul e-Factura). Pașii: fișa furnizorului „DANTE SRL” (CUI 14399840) -> Facturi -> „Facturi primite” -> „Importă XML UBL”
    cu factura furnizorului (BT-31 RO14399840) -> deschide factura importată: „Numele de la ANAF diferă: «DANTE INTERNATIONAL SA» (în fișă:
    «DANTE SRL»).” cu „Actualizează fișa cu numele de la ANAF” -> clic -> „DANTE SRL: numele din fișă e acum «DANTE INTERNATIONAL SA»”, fișa
    are numele de la ANAF."""
    _anaf()
    fz = _fisa(firma_k, "furnizori", "DANTE SRL", "RO14399840")
    tag = "E2E444-%d" % time.time()
    patron.firma(firma_k["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-xml", state="attached", timeout=20000)
    cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma_k["schema"])[0][0] if c.isdigit())
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % tag, "mimeType": "text/xml",
                                   "buffer": UBL_DANTE.format(numar=tag, client=firma_k["nume"], cui=cifre).encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=20000)
    pg.locator(".fac-primita-btn", has_text=tag).click()
    buton = "#pr-anaf-aplica-furnizori-%d" % fz
    pg.wait_for_selector(buton, timeout=20000)
    z = pg.inner_text("#pr-zona")
    assert "Numele de la ANAF diferă: „DANTE INTERNATIONAL SA” (în fișă: „DANTE SRL”)." in z, z
    patron.captura("import_diferit")
    pg.click(buton)
    pg.wait_for_function("() => (document.querySelector('#pr-zona') || {innerText: ''}).innerText.includes('numele din fișă e acum')",
                         timeout=30000)
    assert sql('SELECT nume FROM "%s".furnizori WHERE id = %%s' % firma_k["schema"], (fz,)) == [("DANTE INTERNATIONAL SA",)]
    patron.captura("import_actualizat")
