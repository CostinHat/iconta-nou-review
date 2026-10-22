# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.1 (verbatim în DECIZII „Comanda 11.1”), subagentul Y2: factura primită din XML ajunge nealterată în notă și
în declarații.

  * C80 — reducerile / taxele la nivelul facturii (BG-20 / BG-21) erau ignorate: baza din linii ≠ BT-109, 401 nu închidea BT-112.
  * C81 — factura în valută: TVA-ul în lei de pe factură (BT-111) nu se folosea (TVA × cursul aplicației).
  * C82 — pe o cantitate neîntreagă, valoarea liniei (BT-131) se pierdea la rotunjirea prețului unitar la 2 zecimale.
  * C83 — factura primită în valută nu primea curs la import și nimic nu-l completa: nu se putea conta.

Temei: CF art.299 alin.(1) lit.a (deducerea cere „o factură emisă în conformitate cu prevederile art. 319”); CF art.319 alin.(20) lit.j
(factura cuprinde „suma taxei colectate, exprimate în lei, în funcție de cotele taxei”); CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1)
(cursul comunicat de BNR în ziua anterioară operațiunii). Structură (EN 16931, regulă de validator, nu normă): BR-CO-13, BR-CO-15,
BR-S-08, BR-DEC-23, BR-53.

Pașii, toți pe ecran / pe rutele ecranelor: Date firmă + vectorul fiscal (`pregateste_firma`) -> Facturi -> „Facturi primite” -> „Importă
XML UBL” -> detaliul facturii -> contul 371 -> „Validează” -> nota -> „Validează” pe nota din Registrul jurnal -> Declarații -> D300 / D394
pe luna încheiată. Nimic nu se inserează direct în bază; cursul BNR al facturii în valută vine din cache-ul aplicației / BNR, ca în
producție (`curs_bnr.curs_pentru`), iar testul îl citește din același cache ca să știe ce să aștepte.
Furnizorul: DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md."""
import re
from decimal import Decimal, ROUND_HALF_UP

import pytest

from conftest import firma_noua, perioada_incheiata, sql
from e2e_bloc_a import _api, _card, _ok, pregateste_firma

LUNA = perioada_incheiata("lunar")          # D300 / D394 se generează numai pe o perioadă încheiată (383)
ZI = LUNA.inceput.replace(day=10)


def _ubl(numar, cui, client, moneda="RON", linii=(), reduceri=(), subtotaluri=(), bt109="0", bt110="0", bt112="0", bt111=None):
    """XML-ul e-Factura al furnizorului (UBL 2.1 / CIUS-RO): `linii` = [(cantitate, BT-131, cotă)], `reduceri` = [(taxă?, sumă, cotă, motiv)],
    `subtotaluri` = [(BT-116, BT-117, cotă)], `bt111` = TVA-ul în lei (BT-6 = RON)."""
    cm = 'currencyID="%s"' % moneda
    x = ['<?xml version="1.0" encoding="UTF-8"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
         'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
         'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">',
         "<cbc:ID>%s</cbc:ID><cbc:IssueDate>%s</cbc:IssueDate><cbc:DocumentCurrencyCode>%s</cbc:DocumentCurrencyCode>"
         % (numar, ZI.isoformat(), moneda)]
    if bt111 is not None:
        x.append("<cbc:TaxCurrencyCode>RON</cbc:TaxCurrencyCode>")
    x.append('<cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID><cac:TaxScheme>'
             '<cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>DANTE INTERNATIONAL SA'
             '</cbc:RegistrationName></cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>')
    x.append('<cac:AccountingCustomerParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT'
             '</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>%s</cbc:RegistrationName>'
             '</cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty>' % (cui, client))
    for taxa, suma, cota, motiv in reduceri:
        x.append("<cac:AllowanceCharge><cbc:ChargeIndicator>%s</cbc:ChargeIndicator><cbc:AllowanceChargeReason>%s</cbc:AllowanceChargeReason>"
                 "<cbc:Amount %s>%s</cbc:Amount><cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT"
                 "</cbc:ID></cac:TaxScheme></cac:TaxCategory></cac:AllowanceCharge>" % ("true" if taxa else "false", motiv, cm, suma, cota))
    if bt111 is not None:
        x.append('<cac:TaxTotal><cbc:TaxAmount currencyID="RON">%s</cbc:TaxAmount></cac:TaxTotal>' % bt111)
    x.append("<cac:TaxTotal><cbc:TaxAmount %s>%s</cbc:TaxAmount>" % (cm, bt110))
    for b, t, c in subtotaluri:
        x.append("<cac:TaxSubtotal><cbc:TaxableAmount %s>%s</cbc:TaxableAmount><cbc:TaxAmount %s>%s</cbc:TaxAmount><cac:TaxCategory><cbc:ID>S"
                 "</cbc:ID><cbc:Percent>%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory></cac:TaxSubtotal>"
                 % (cm, b, cm, t, c))
    x.append("</cac:TaxTotal><cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount %s>%s</cbc:TaxExclusiveAmount><cbc:TaxInclusiveAmount %s>%s"
             "</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>" % (cm, bt109, cm, bt112))
    for i, (q, le, c) in enumerate(linii, 1):
        pret = (Decimal(le) / Decimal(q)).quantize(Decimal("0.0001"))
        x.append('<cac:InvoiceLine><cbc:ID>%d</cbc:ID><cbc:InvoicedQuantity unitCode="H87">%s</cbc:InvoicedQuantity><cbc:LineExtensionAmount %s>'
                 "%s</cbc:LineExtensionAmount><cac:Item><cbc:Name>Marfa Y2 %d</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>"
                 "%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory></cac:Item><cac:Price>"
                 "<cbc:PriceAmount %s>%s</cbc:PriceAmount></cac:Price></cac:InvoiceLine>" % (i, q, cm, le, i, c, cm, pret))
    x.append("</Invoice>")
    return "".join(x)


@pytest.fixture()
def firma_y2():
    for f in firma_noua():
        yield f


def _atr(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


def _rezumat2(xml, cota):
    m = re.search(r'<rezumat2\b[^>]*\bcota="%s"[^>]*>' % cota, xml)
    return (_atr(m.group(0), "bazaA"), _atr(m.group(0), "tvaA")) if m else None


def _importa_si_valideaza(patron, firma, tag, xml_doc, ecran_contine=None):
    """Facturi -> „Facturi primite” -> „Importă XML UBL” -> detaliul -> (verifică ecranul) -> contul 371 -> „Validează” -> confirmă.
    Întoarce id-ul facturii și liniile notei ei."""
    s = firma["schema"]
    patron.firma(firma["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg = patron.pg
    pg.click("#fac-primite")
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % tag, "mimeType": "text/xml", "buffer": xml_doc.encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=40000)
    pg.locator(".fac-primita-btn", has_text=tag).click()
    pg.wait_for_selector("#pr-cont", timeout=20000)
    if ecran_contine:
        txt = pg.inner_text(".fereastra:last-of-type")
        for t in ecran_contine:
            assert t in txt, txt[:3000]
    pg.fill("#pr-cont", "371")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    patron.captura("validata_%s" % tag)
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % s, (tag,))[0][0]
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i '
               "ON i.id = l.inregistrare_id WHERE i.factura_id = %%s ORDER BY l.id" % (s, s), (fid,))
    return fid, note


def _valideaza_notele_lunii(patron, firma):
    s, tid = firma["schema"], firma["tenant_id"]
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE status <> \'validata\' AND data >= %%s AND data <= %%s ORDER BY id' % s,
                      (LUNA.inceput, LUNA.sfarsit)):
        _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {}), "validarea notei %s" % nid)


def _xml_declaratie(patron, firma, tip):
    from e2e_bloc_d import _genereaza
    _genereaza(patron, firma, tip, LUNA.an, LUNA.luna)
    patron.captura("pas2_%s" % tip)
    pg = patron.pg
    assert not pg.locator(".fereastra:last-of-type .dec-eroare").count(), patron.fereastra()[:3000]
    return pg.eval_on_selector(".fereastra:last-of-type details.dec-xml pre.dec-xml-pre", "el => el.textContent")


def _cifrele(firma):
    return "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma["schema"])[0][0] if c.isdigit())


def test_def_c80_reducerea_de_document_intra_in_baza_cotei_si_401_inchide_totalul(patron, firma_y2):
    """C80. Pașii: Facturi -> „Facturi primite” -> „Importă XML UBL” (factura: 21% linii 500,00, reducere 50,00, transport 20,00; 11% linii
    300,00, reducere 30,00 — BT-109 740,00, TVA 128,40, BT-112 868,40) -> detaliul arată reducerile și taxa ca linii („Reducere la nivelul
    facturii: Discount comercial”, „Taxă suplimentară la nivelul facturii: Transport”) -> contul 371 -> „Validează”: nota are 371 = 401
    470,00 + 270,00 (nu 500 + 300) și 401 închide 868,40 (nu 928,40) -> notele validate -> D300: rd.24 (R22) 470 / 99, rd.25 (R23) 270 / 30
    -> D394: rezumatul achizițiilor bazaA / tvaA 470 / 99 și 270 / 30."""
    import time as _t
    pregateste_firma(patron, firma_y2, platitor=True, regim_fiscal="profit")
    tag = "E2EC80-%d" % _t.time()
    doc = _ubl(tag, _cifrele(firma_y2), firma_y2["nume"], linii=[(10, "500.00", 21), (6, "300.00", 11)],
               reduceri=[(False, "50.00", 21, "Discount comercial"), (False, "30.00", 11, "Discount comercial"), (True, "20.00", 21, "Transport")],
               subtotaluri=[("470.00", "98.70", 21), ("270.00", "29.70", 11)], bt109="740.00", bt110="128.40", bt112="868.40")
    _fid, note = _importa_si_valideaza(patron, firma_y2, tag, doc, ecran_contine=(
        "Reducere la nivelul facturii: Discount comercial", "Taxă suplimentară la nivelul facturii: Transport"))
    # BR-S-08 / BR-CO-13: baza cotei = liniile − reducerile + taxele; BR-CO-15: 401 = BT-112
    assert sorted(float(n[2]) for n in note if n[0] == "371") == [270.0, 470.0], note
    assert sum(float(n[2]) for n in note if n[1] == "401") == pytest.approx(868.40), note
    # recepția în stoc (validarea pe 371): reducerile intră în costul articolelor (OMFP 1802/2014 pct.76 alin.(1)), nu devin articole,
    # iar fișa de magazie închide nota 371 la ban
    fisa = sql('SELECT a.denumire, m.valoare::text FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id '
               "WHERE m.factura_id = %%s ORDER BY m.id" % (firma_y2["schema"], firma_y2["schema"]), (_fid,))
    assert sorted(v for _d, v in fisa) == ["270.00", "470.00"] and not [d for d, _v in fisa if "Reducere" in d or "Taxă" in d], fisa
    _valideaza_notele_lunii(patron, firma_y2)
    xml = _xml_declaratie(patron, firma_y2, "d300")
    assert (_atr(xml, "R22_1"), _atr(xml, "R22_2"), _atr(xml, "R23_1"), _atr(xml, "R23_2")) == ("470", "99", "270", "30"), xml[:3000]
    x394 = _xml_declaratie(patron, firma_y2, "d394")
    assert (_rezumat2(x394, 21), _rezumat2(x394, 11)) == (("470", "99"), ("270", "30")), x394[:3000]


def test_def_c82_cantitate_neintreaga_baza_liniei_din_xml_la_ban(patron, firma_y2):
    """C82. Pașii: Facturi -> „Facturi primite” -> „Importă XML UBL” (o linie de 3,333 bucăți cu valoarea 100,50 lei — prețul unitar
    30,1530… —, TVA 21,11, total 121,61) -> contul 371 -> „Validează”: nota are 371 = 401 100,50 (nu 3,333 × 30,15 = 100,49) și 401
    închide 121,61 -> nota validată -> D300: rd.24 (R22) baza 101 (100,50; din preț × cantitate ar fi 100)."""
    import time as _t
    pregateste_firma(patron, firma_y2, platitor=True, regim_fiscal="profit")
    tag = "E2EC82-%d" % _t.time()
    doc = _ubl(tag, _cifrele(firma_y2), firma_y2["nume"], linii=[("3.333", "100.50", 21)], subtotaluri=[("100.50", "21.11", 21)],
               bt109="100.50", bt110="21.11", bt112="121.61")
    _fid, note = _importa_si_valideaza(patron, firma_y2, tag, doc)
    assert [n for n in note if n[0] == "371"] == [("371", "401", "100.50")], note   # BR-DEC-23: BT-131 de pe factură, la ban
    assert sum(float(n[2]) for n in note if n[1] == "401") == pytest.approx(121.61), note
    _valideaza_notele_lunii(patron, firma_y2)
    xml = _xml_declaratie(patron, firma_y2, "d300")
    assert (_atr(xml, "R22_1"), _atr(xml, "R22_2")) == ("101", "21"), xml[:3000]


def _curs_bnr_inainte(moneda, zi):
    """Cursul pe care îl pune regula legală (CF art.290 alin.(2), HG 1/2016 pct.35 alin.(1)): cel comunicat de BNR ÎNAINTEA zilei facturii —
    citit din cache-ul aplicației (același pe care îl citește `curs_bnr.curs_pentru`), după ce importul l-a adus."""
    r = sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = %s AND data < %s ORDER BY data DESC LIMIT 1", (moneda, zi))
    return Decimal(str(r[0][0])) if r else None


def _doc_eur(tag, firma):
    """1.000,00 EUR la 21% (TVA 210,00 EUR) + 500,00 EUR la 11% (TVA 55,00 EUR); TVA-ul în lei scris de furnizor (BT-111) 1.300,00 lei."""
    return _ubl(tag, _cifrele(firma), firma["nume"], moneda="EUR", linii=[(1, "1000.00", 21), (1, "500.00", 11)],
                subtotaluri=[("1000.00", "210.00", 21), ("500.00", "55.00", 11)], bt109="1500.00", bt110="265.00", bt112="1765.00",
                bt111="1300.00")


def test_def_c83_factura_primita_in_valuta_primeste_cursul_bnr_la_import_si_se_conteaza(patron, firma_y2):
    """C83. Pașii: Facturi -> „Facturi primite” -> „Importă XML UBL” (factură în EUR) -> contul 371 -> „Validează”: confirmarea „Validată”
    și nota scrisă în lei — înainte, factura în valută importată n-avea curs, contarea o refuza (LIPSA_CURS_LEI), iar nimic nu-l completa.
    Pe factură: cursul comunicat de BNR în ziua dinaintea facturii (CF art.290 alin.(2), HG 1/2016 pct.35 alin.(1)), sursa „bnr”."""
    import time as _t
    pregateste_firma(patron, firma_y2, platitor=True, regim_fiscal="profit")
    tag = "E2EC83-%d" % _t.time()
    fid, note = _importa_si_valideaza(patron, firma_y2, tag, _doc_eur(tag, firma_y2))
    curs, sursa = sql('SELECT curs_bnr, curs_sursa FROM "%s".facturi WHERE id = %%s' % firma_y2["schema"], (fid,))[0]
    asteptat = _curs_bnr_inainte("EUR", ZI)
    assert asteptat is not None and curs is not None and Decimal(str(curs)) == asteptat and sursa == "bnr", (curs, sursa, asteptat)
    baza_21 = (Decimal("1000.00") * asteptat).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert ("371", "401", str(baza_21)) in note, note   # nota în lei: 1.000,00 EUR × cursul BNR


def test_def_c81_tva_ul_in_lei_de_pe_factura_bt111_in_nota_si_d300(patron, firma_y2):
    """C81. Pașii: Facturi -> „Facturi primite” -> „Importă XML UBL” (factură în EUR cu TVA-ul în lei scris de furnizor, BT-111 1.300,00
    lei) -> contul 371 -> „Validează”: nota are 4426 = 401 1.030,19 (21%) și 269,81 (11%) — BT-111 împărțit pe cote, nu 265 EUR × cursul
    BNR —, cu suma 1.300,00 -> nota validată -> D300: rd.24 (R22) TVA 1030, rd.25 (R23) TVA 270 (TVA × curs ar fi dat ~1.040 / ~272)."""
    import time as _t
    pregateste_firma(patron, firma_y2, platitor=True, regim_fiscal="profit")
    tag = "E2EC81-%d" % _t.time()
    _fid, note = _importa_si_valideaza(patron, firma_y2, tag, _doc_eur(tag, firma_y2))
    # CF art.319 alin.(20) lit.j: TVA-ul „exprimat în lei” e cel de pe factură — 1.300 × 210/265 = 1.030,19; 1.300 × 55/265 = 269,81
    assert sorted(n[2] for n in note if n[0] == "4426") == ["1030.19", "269.81"], note
    _valideaza_notele_lunii(patron, firma_y2)
    xml = _xml_declaratie(patron, firma_y2, "d300")
    assert (_atr(xml, "R22_2"), _atr(xml, "R23_2")) == ("1030", "270"), xml[:3000]
