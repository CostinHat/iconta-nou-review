# -*- coding: utf-8 -*-
"""Lotul 11, subagentul Y2 — factura primită din XML ajunge NEALTERATĂ în contare și în declarații (C79 în D394 / D406, C80, C81, C82, C83).

  * C79 (clasa, în D394 și D406): TVA-ul deductibil e cel de pe factura furnizorului (BG-23, `factura_tva_cote`), nu recalculul din baze —
    D394 tvaA și D406 Σ TaxAmount pe factură = TVA-ul facturii = 4426 din notă.
  * C80: reducerile / taxele la nivelul facturii (BG-20 / BG-21) intră în baza cotei lor: baza liniilor = BT-109, 401 = BT-112.
  * C81: factura în valută — TVA-ul în lei de pe factură (BT-111) e TVA-ul notei și al declarațiilor; fără BT-111, TVA × curs.
  * C82: valoarea liniei (BT-131) se păstrează exact; pe o cantitate neîntreagă cantitate × preț (2 zecimale) pierdea banul.
  * C83: factura în valută primește cursul BNR la import (regula `curs_bnr.REGULA_OPERATIUNE`); fără curs, contarea îl reîncearcă.

Temei:
  * CF art.299 alin.(1) lit.a: deducerea cere ca beneficiarul „să dețină o factură emisă în conformitate cu prevederile art. 319”;
  * CF art.319 alin.(20) lit.j: factura cuprinde „indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei, în funcție
    de cotele taxei”;
  * CF art.290 alin.(2): „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...] valabil
    la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”; HG 1/2016 pct.35 alin.(1): „prin ultimul curs de schimb
    comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară”.
  * Structură (regulă de validator EN 16931, nu normă — `EN16931-model.sch`): BR-CO-13 „Invoice total amount without VAT (BT-109) = Σ Invoice
    line net amount (BT-131) - Sum of allowances on document level (BT-107) + Sum of charges on document level (BT-108).”; BR-CO-15 „Invoice
    total amount with VAT (BT-112) = Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110).”; BR-DEC-23 „The allowed
    maximum number of decimals for the Invoice line net amount (BT-131) is 2.”; BR-53 „If the VAT accounting currency code (BT-6) is
    present, then the Invoice total VAT amount in accounting currency (BT-111) shall be provided.”
Schemă efemeră din tenant_template, în tranzacție anulată; ANAF și BNR nu se cheamă (cursul: `facturi_api.curs_automat` înlocuit)."""
import datetime as _dt
import io
import os
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import db as _db
from core import efactura_import as _ef
from core import tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "tenant_test_lot11_y2"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_D = Decimal
_CUI_FURN, _CUI_FIRMA = "14399840", "9010105"   # cifra de control verificată în `test_cui_de_test_valid`


def _cui_valid(cui):   # CLAUDE.md „Date de test — CUI/CNP”: algoritmul oficial al cifrei de control
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def test_cui_de_test_valid():
    assert _cui_valid(_CUI_FURN) and _cui_valid(_CUI_FIRMA)


def xml_factura(numar, data="2026-07-10", moneda="RON", linii=(), reduceri=(), subtotaluri=(), bt109=None, bt110=None, bt112=None,
                bt111=None):
    """Un XML e-Factura minim (UBL 2.1 / CIUS-RO): `linii` = [(cantitate, BT-131, cotă)], `reduceri` = [(taxă?, sumă, cotă, motiv)],
    `subtotaluri` = [(BT-116, BT-117, cotă)], `bt111` = TVA-ul în lei (cu BT-6 = RON)."""
    cm = 'currencyID="%s"' % moneda
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
         'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
         'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">',
         "<cbc:ID>%s</cbc:ID><cbc:IssueDate>%s</cbc:IssueDate><cbc:DocumentCurrencyCode>%s</cbc:DocumentCurrencyCode>" % (numar, data, moneda)]
    if bt111 is not None:
        x.append("<cbc:TaxCurrencyCode>RON</cbc:TaxCurrencyCode>")
    x.append('<cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT'
             '</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>DANTE INTERNATIONAL SA'
             '</cbc:RegistrationName></cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>' % _CUI_FURN)
    x.append('<cac:AccountingCustomerParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT'
             '</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>Y2 SRL</cbc:RegistrationName>'
             '</cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty>' % _CUI_FIRMA)
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
    x.append("</cac:TaxTotal>")
    x.append("<cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount %s>%s</cbc:TaxExclusiveAmount><cbc:TaxInclusiveAmount %s>%s"
             "</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>" % (cm, bt109, cm, bt112))
    for i, (q, le, c) in enumerate(linii, 1):
        pret = (_D(le) / _D(q)).quantize(_D("0.0001"))
        x.append('<cac:InvoiceLine><cbc:ID>%d</cbc:ID><cbc:InvoicedQuantity unitCode="H87">%s</cbc:InvoicedQuantity>'
                 "<cbc:LineExtensionAmount %s>%s</cbc:LineExtensionAmount><cac:Item><cbc:Name>Marfa %d</cbc:Name><cac:ClassifiedTaxCategory>"
                 "<cbc:ID>S</cbc:ID><cbc:Percent>%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory>"
                 "</cac:Item><cac:Price><cbc:PriceAmount %s>%s</cbc:PriceAmount></cac:Price></cac:InvoiceLine>" % (i, q, cm, le, i, c, cm, pret))
    x.append("</Invoice>")
    return "".join(x)


#: C79 — TVA-ul furnizorului diferă de recalcul cu ±0,02 pe cotă (21%: 202,33 × 21% = 42,49, pe factură 42,51; 11%: 150,05 × 11% = 16,51,
#: pe factură 16,49). BT-110 = 59,00, BT-112 = 411,38.
XML_C79 = xml_factura("Y2-C79-1", linii=[(1, "101.17", 21), (1, "101.16", 21), (1, "150.05", 11)],
                      subtotaluri=[("202.33", "42.51", 21), ("150.05", "16.49", 11)], bt109="352.38", bt110="59.00", bt112="411.38")

#: C80 — reducere de document pe ambele cote + o taxă de transport pe 21%: BR-S-08 / BR-CO-13
#:   21%: linii 500,00 − reducere 50,00 + transport 20,00 = 470,00 (BT-116), TVA 98,70
#:   11%: linii 300,00 − reducere 30,00 = 270,00, TVA 29,70; BT-109 = 740,00, BT-110 = 128,40, BT-112 = 868,40
XML_C80 = xml_factura("Y2-C80-1", linii=[(10, "500.00", 21), (6, "300.00", 11)],
                      reduceri=[(False, "50.00", 21, "Discount comercial"), (False, "30.00", 11, "Discount comercial"),
                                (True, "20.00", 21, "Transport")],
                      subtotaluri=[("470.00", "98.70", 21), ("270.00", "29.70", 11)], bt109="740.00", bt110="128.40", bt112="868.40")

#: C82 — cantitate neîntreagă: BT-131 = 100,50 la 3,333 bucăți (preț 30,1530…); prețul la 2 zecimale (30,15) × 3,333 = 100,48995 -> 100,49,
#: iar în D300 (lei întregi) 100 în loc de 101. TVA 21,11 (100,50 × 21% = 21,105), BT-112 121,61.
XML_C82 = xml_factura("Y2-C82-1", linii=[("3.333", "100.50", 21)], subtotaluri=[("100.50", "21.11", 21)],
                      bt109="100.50", bt110="21.11", bt112="121.61")

#: C81 — factură în EUR cu BT-111: 1.000,00 EUR la 21% (TVA 210,00 EUR) + 500,00 EUR la 11% (TVA 55,00 EUR); BT-110 265,00 EUR; TVA-ul în
#: lei scris de furnizor (BT-111) 1.300,00 lei, cu cursul lui — nu 265,00 × cursul BNR al aplicației (4,9750 -> 1.318,38).
_CURS = _D("4.9750")
XML_C81 = xml_factura("Y2-C81-1", moneda="EUR", linii=[(1, "1000.00", 21), (1, "500.00", 11)],
                      subtotaluri=[("1000.00", "210.00", 21), ("500.00", "55.00", 11)], bt109="1500.00", bt110="265.00", bt112="1765.00",
                      bt111="1300.00")


# ── parserul (pur) ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_c80_reducerile_de_document_sunt_linii_pe_cota_lor():
    f = _ef.parseaza_xml(XML_C80.encode(), _CUI_FIRMA)
    doc = [(l["cota_tva"], l["valoare_neta"]) for l in f["linii"] if l.get("nivel_document")]
    assert doc == [("21", "-50.00"), ("11", "-30.00"), ("21", "20.00")], f["linii"]
    # BR-CO-13: Σ liniilor (cu reducerile / taxele de document) = BT-109
    assert sum(_D(l["valoare_neta"]) for l in f["linii"]) == _D("740.00")


def test_c82_valoarea_liniei_din_xml_se_pastreaza():
    f = _ef.parseaza_xml(XML_C82.encode(), _CUI_FIRMA)
    assert f["linii"][0]["valoare_neta"] == "100.50"    # BR-DEC-23: BT-131 e suma la ban de pe factură
    from core import tva_calcul as _tc
    assert _tc.net_linie("3.333", "30.15") == _D("100.49")                # prețul la 2 zecimale pierde banul
    assert _tc.net_linie("3.333", "30.15", "100.50") == _D("100.50")      # valoarea de pe factură, exactă


def test_c81_bt111_se_citeste_numai_cu_bt6_ron():
    f = _ef.parseaza_xml(XML_C81.encode(), _CUI_FIRMA)
    assert (f["moneda"], f["tva"], f["tva_lei_xml"]) == ("EUR", "265.00", "1300.00")   # BT-110 în EUR, BT-111 în lei (BR-53)
    assert _ef.parseaza_xml(XML_C79.encode(), _CUI_FIRMA)["tva_lei_xml"] is None     # RON: nu există BT-111 separat


def test_c81_bt111_se_imparte_pe_cote_proportional_si_suma_e_exacta():
    from core import tva_calcul as _tc
    lei = _tc.tva_lei_pe_cote({_D(21): (None, _D("210.00")), _D(11): (None, _D("55.00"))}, _CURS, tva_lei_document="1318.20")
    # CF art.319 alin.(20) lit.j: TVA-ul în lei e al facturii: 1.318,20 × 210/265 = 1.044,61; 1.318,20 × 55/265 = 273,59; Σ = BT-111
    assert lei == {_D(21): _D("1044.61"), _D(11): _D("273.59")} and sum(lei.values()) == _D("1318.20"), lei


# ── pe o schemă efemeră ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def conn_y2():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
                    "tva_la_incasare, platitor_tva_anaf_inceput, declarant_nume, declarant_prenume, declarant_functie, forma_juridica, "
                    "capital_subscris, telefon) VALUES (1,'Y2 SRL',%s,'Str Test 1','Bucuresti','B','4690','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'lunar',false,'2025-01-01','Popescu','Ion','ADMINISTRATOR','SRL',200,'0712345678')",
                    (_CUI_FIRMA,))
            yield _FaraCommit(conn)
        finally:
            conn.rollback()


@pytest.fixture
def curs_fix(monkeypatch):
    """Cursul BNR al operațiunii, fără rețea: `facturi_api.curs_automat` (sursa unică a regulii, `curs_bnr.curs_pentru`) înlocuit."""
    from core import facturi_api
    stare = {"r": (_CURS, _dt.date(2026, 7, 9), "bnr")}
    monkeypatch.setattr(facturi_api, "curs_automat", lambda conn, moneda, zi: stare["r"])
    return stare


def _importa(conn, xml, conteaza=True):
    from core import contare_facturi as _cf, uc_tenants
    f = _ef.parseaza_xml(xml.encode(), _CUI_FIRMA)
    with conn.cursor() as cur:
        fid, nou = uc_tenants._factura_importata(cur, _SCHEMA, f)
        assert nou
        cur.execute("UPDATE facturi SET tert_platitor_tva = true, tert_oras = 'Bucuresti', tert_judet = 'B' WHERE id = %s", (fid,))
    if conteaza:
        with _cf.cursor_dict(conn) as cur:
            _cf.contabilizeaza(cur, _SCHEMA, fid, automat=True, cont_cheltuiala="371")
    return fid


def _note(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s ORDER BY l.id", (fid,))
        return [(a, b, _D(c)) for a, b, c in cur.fetchall()]


def _valideaza_notele(conn):
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata', document_ref = COALESCE(NULLIF(document_ref, ''), 'Y2') "
                    "WHERE status <> 'validata'")


def _tva_a(res):
    return {c: (int(v["bazaA"]), int(v["tvaA"])) for c, v in res.rezumat2.items() if v.get("bazaA") or v.get("tvaA")}


def _purchase(xml):
    """{InvoiceNo: [(TaxPercentage, InvoiceLine Amount, TaxAmount)]} din PurchaseInvoices (D406)."""
    loc = lambda t: t.rsplit("}", 1)[-1]   # noqa: E731
    rad = ET.fromstring(xml.encode("utf-8"))
    out = {}
    for s in rad.iter():
        if loc(s.tag) != "PurchaseInvoices":
            continue
        for inv in s:
            if loc(inv.tag) != "Invoice":
                continue
            nr = next(e.text for e in inv if loc(e.tag) == "InvoiceNo")
            for ln in inv:
                if loc(ln.tag) != "InvoiceLine":
                    continue
                am = next(e for e in ln if loc(e.tag) == "InvoiceLineAmount")
                amount = next(e.text for e in am if loc(e.tag) == "Amount")
                tx = next(e for e in ln if loc(e.tag) == "TaxInformation")
                out.setdefault(nr, []).append((_D(next(e.text for e in tx if loc(e.tag) == "TaxPercentage")), _D(amount),
                                               _D(next(e.text for e in next(e for e in tx if loc(e.tag) == "TaxAmount") if loc(e.tag) == "Amount"))))
    return out


def _duk(xml, tip, luna=7):
    from core import duk
    v = duk.valideaza(xml, tip, an=2026, luna=luna, timeout=240)
    if v.get("stare") == "gri":
        pytest.skip("validator %s indisponibil: %s" % (tip, v.get("temei")))
    return v


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c79_d394_tvaA_e_tva_ul_facturii_si_duk_valid(conn_y2):
    from core import d394
    _importa(conn_y2, XML_C79)
    _valideaza_notele(conn_y2)
    xml, res = d394.genereaza(conn_y2, _SCHEMA, Perioada(2026, luna=7))
    # CF art.299 alin.(1) lit.a + art.319 alin.(20) lit.j: tvaA = TVA-ul cotei de pe factură — 42,51 -> 43 (recalcul 42,49 -> 42), 16,49 -> 16
    assert _tva_a(res) == {21: (202, 43), 11: (150, 16)}, res.rezumat2
    v = _duk(xml, "d394")
    print("C79 D394 rezumat2 (bazaA, tvaA):", _tva_a(res), "| DUK D394:", v.get("stare"))
    assert v["stare"] == "valid", v


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c79_d406_purchaseinvoices_suma_taxamount_e_tva_ul_facturii_si_duk_valid(conn_y2):
    from core import d406
    _importa(conn_y2, XML_C79)
    _valideaza_notele(conn_y2)
    xml, _res = d406.genereaza(conn_y2, _SCHEMA, 2026, 7)
    linii = _purchase(xml)["Y2-C79-1"]
    pe_cota = {}
    for c, _a, t in linii:
        pe_cota[c] = pe_cota.get(c, _D(0)) + t
    # Σ TaxAmount pe cotă = TVA-ul cotei de pe factură (= 4426 din notă), nu recalculul pe linii (21,25 + 21,24 = 42,49 / 16,51)
    assert pe_cota == {_D(21): _D("42.51"), _D(11): _D("16.49")}, linii
    v = _duk(xml, "d406")
    print("C79 D406 PurchaseInvoices (cotă, Amount, TaxAmount):", [tuple(str(x) for x in l) for l in linii], "| DUK D406:", v.get("stare"))
    assert v["stare"] == "valid", v


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c80_reducerea_de_document_intra_in_baza_cotei_si_401_inchide_bt112(conn_y2):
    from core import d300, d394, duk
    fid = _importa(conn_y2, XML_C80)
    note = _note(conn_y2, fid)
    # BR-CO-15: 401 = BT-112 868,40 (înainte: baza liniilor 800,00 + TVA 128,40 = 928,40)
    assert sum(s for a, b, s in note if b == "401") == _D("868.40"), note
    # BR-S-08: baza cotei = liniile − reducerile + taxele: 371 = 470,00 + 270,00
    assert sum(s for a, b, s in note if a == "371") == _D("740.00"), note
    _valideaza_notele(conn_y2)
    xml, res = d300.genereaza(conn_y2, _SCHEMA, Perioada(2026, luna=7))
    # D300 rd.24 / rd.25: baza 470 / 270, TVA-ul facturii 98,70 -> 99 / 29,70 -> 30
    assert (res.R.get("R22_1"), res.R.get("R22_2"), res.R.get("R23_1"), res.R.get("R23_2")) == (470, 99, 270, 30), res.R
    assert duk.valideaza(xml, "d300", an=2026, luna=7)["stare"] == "valid"
    _x394, r394 = d394.genereaza(conn_y2, _SCHEMA, Perioada(2026, luna=7))
    assert _tva_a(r394) == {21: (470, 99), 11: (270, 30)}, r394.rezumat2
    assert _duk(_x394, "d394")["stare"] == "valid"
    from core import d406
    x406, _r406 = d406.genereaza(conn_y2, _SCHEMA, 2026, 7)
    l406 = _purchase(x406)["Y2-C80-1"]
    # SAF-T: liniile facturii, cu reducerile / taxa de document pe cota lor — Σ Amount = BT-109 740,00, Σ TaxAmount = BT-110 128,40
    assert (sum(a for _c, a, _t in l406), sum(t for _c, _a, t in l406)) == (_D("740.00"), _D("128.40")), l406
    v406 = _duk(x406, "d406")
    assert v406["stare"] == "valid", v406
    print("C80 nota:", [(a, b, str(x)) for a, b, x in note], "| D300 R22/R23:", (res.R.get("R22_1"), res.R.get("R22_2"),
          res.R.get("R23_1"), res.R.get("R23_2")), "| D394:", _tva_a(r394))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c82_cantitate_neintreaga_baza_din_xml_la_ban(conn_y2):
    from core import d300, d406
    fid = _importa(conn_y2, XML_C82)
    with conn_y2.cursor() as cur:
        cur.execute("SELECT cantitate, pret_unitar, valoare_neta FROM factura_linii WHERE factura_id = %s", (fid,))
        assert cur.fetchone() == (_D("3.333"), _D("30.15"), _D("100.50"))   # prețul rămâne la 2 zecimale; BT-131 păstrat exact
    note = _note(conn_y2, fid)
    assert ("371", "401", _D("100.50")) in note and sum(s for a, b, s in note if b == "401") == _D("121.61"), note   # nu 100,49
    _valideaza_notele(conn_y2)
    _x, res = d300.genereaza(conn_y2, _SCHEMA, Perioada(2026, luna=7))
    assert (res.R.get("R22_1"), res.R.get("R22_2")) == (101, 21), res.R   # 100,50 -> 101 (din preț × cantitate: 100,49 -> 100)
    xml, _r = d406.genereaza(conn_y2, _SCHEMA, 2026, 7)
    assert _purchase(xml)["Y2-C82-1"] == [(_D(21), _D("100.50"), _D("21.11"))]   # InvoiceLine Amount = BT-131, nu 100,49
    print("C82 nota:", [(a, b, str(x)) for a, b, x in note], "| D300 R22:", (res.R.get("R22_1"), res.R.get("R22_2")),
          "| D406:", [tuple(str(x) for x in l) for l in _purchase(xml)["Y2-C82-1"]])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c81_c83_valuta_curs_la_import_si_tva_ul_bt111_in_nota_d300_d394(conn_y2, curs_fix):
    from core import d300, d394, duk
    fid = _importa(conn_y2, XML_C81)
    with conn_y2.cursor() as cur:
        cur.execute("SELECT curs_bnr, curs_sursa, tva_lei, total_lei FROM facturi WHERE id = %s", (fid,))
        # C83: cursul BNR al operațiunii pus la import (CF art.290 alin.(2)); C81: TVA-ul în lei = BT-111, total = 1.500 × 4,9750 + BT-111
        assert cur.fetchone() == (_D("4.9750"), "bnr", _D("1300.00"), _D("8762.50"))
    tva = sorted(s for a, b, s in _note(conn_y2, fid) if a == "4426")
    # CF art.319 alin.(20) lit.j: TVA-ul în lei de pe factură, pe cote (1.300 × 210/265 = 1.030,19; × 55/265 = 269,81), nu 265 × 4,9750
    assert tva == [_D("269.81"), _D("1030.19")], tva
    _valideaza_notele(conn_y2)
    xml, res = d300.genereaza(conn_y2, _SCHEMA, Perioada(2026, luna=7))
    # rd.24 / rd.25: baza 1.000 × 4,9750 = 4.975 / 2.488 (2.487,50); TVA-ul BT-111 pe cote 1.030 / 270 (TVA × curs ar fi 1.045 / 274);
    # a doua cale (d300_reconciliere, SQL propriu) a ajuns la aceleași cifre — altfel `genereaza` ar fi refuzat
    assert (res.R.get("R22_1"), res.R.get("R22_2"), res.R.get("R23_1"), res.R.get("R23_2")) == (4975, 1030, 2488, 270), res.R
    assert duk.valideaza(xml, "d300", an=2026, luna=7)["stare"] == "valid"
    _x394, r394 = d394.genereaza(conn_y2, _SCHEMA, Perioada(2026, luna=7))
    assert _tva_a(r394) == {21: (4975, 1030), 11: (2488, 270)}, r394.rezumat2
    print("C81/C83 4426:", [str(x) for x in tva], "| D300:", (res.R.get("R22_1"), res.R.get("R22_2"), res.R.get("R23_1"),
          res.R.get("R23_2")), "| D394:", _tva_a(r394))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c81_fara_bt111_tva_ul_e_tva_x_curs(conn_y2, curs_fix):
    x = XML_C81.replace('<cbc:TaxCurrencyCode>RON</cbc:TaxCurrencyCode>', "").replace(
        '<cac:TaxTotal><cbc:TaxAmount currencyID="RON">1300.00</cbc:TaxAmount></cac:TaxTotal>', "").replace("Y2-C81-1", "Y2-C81-2")
    fid = _importa(conn_y2, x)
    with conn_y2.cursor() as cur:
        cur.execute("SELECT tva_lei FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone()[0] == _D("1318.38")   # fără BT-111: 265,00 × 4,9750, ca la emitere (`facturi_api.sume_lei`)
    assert sorted(s for a, b, s in _note(conn_y2, fid) if a == "4426") == [_D("273.63"), _D("1044.75")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c83_bnr_indisponibil_la_import_contarea_spune_ce_se_face_si_reia_cursul(conn_y2, curs_fix):
    from core import contare_facturi as _cf
    curs_fix["r"] = {"ok": False, "cod": "CURS_INDISPONIBIL", "mesaj": "Cursul BNR nu e disponibil momentan."}
    fid = _importa(conn_y2, XML_C81, conteaza=False)
    with conn_y2.cursor() as cur:
        cur.execute("SELECT curs_bnr, tva_lei FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone() == (None, None)   # fără curs nu se ghicește nimic
    with _cf.cursor_dict(conn_y2) as cur, pytest.raises(_cf.RefuzContare) as e:
        _cf.contabilizeaza(cur, _SCHEMA, fid, automat=False, cont_cheltuiala="371")
    assert e.value.cod == "LIPSA_CURS_LEI" and e.value.detalii["iesire"] == "reincearca_contarea", e.value.detalii
    # mesajul EXACT: factura numită, motivul BNR transmis, regula legală și ce face contabilul (CF art.290 alin.(2): cursul din ziua
    # dinaintea facturii)
    assert e.value.mesaj == (
        "Factură Y2-C81-1 din 10.07.2026 e în EUR și n-are încă curs BNR: Cursul BNR nu e disponibil momentan. Cursul se pune singur, pe "
        "regula legală (cursul comunicat de BNR în ziua dinaintea facturii, CF art.290 alin.(2)), la următoarea contare — apasă din nou "
        "„Contabilizează” când BNR răspunde."), e.value.mesaj
    curs_fix["r"] = (_CURS, _dt.date(2026, 7, 9), "bnr")   # BNR răspunde: aceeași contare pune cursul și scrie nota
    with _cf.cursor_dict(conn_y2) as cur:
        _cf.contabilizeaza(cur, _SCHEMA, fid, automat=False, cont_cheltuiala="371")
    assert sum(s for a, b, s in _note(conn_y2, fid) if a == "4426") == _D("1300.00")


def test_sablonul_poarta_blocul_migrarii():
    """Sursa unică a structurii: blocul din tenant_template.sql = `migrare_valoare_neta_linie.bloc_template()`."""
    from core import migrare_valoare_neta_linie as _m
    assert _m.bloc_template() in io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()


def test_migrarea_citeste_bt131_din_xml_in_ordinea_liniilor():
    from core import migrare_valoare_neta_linie as _m
    assert _m.valori_din_xml(XML_C80) == ["500.00", "300.00"]   # numai `cac:InvoiceLine` (reducerile de document nu erau linii)


# ── recepția în stoc a facturii primite (C80 / C82): fișa de magazie = nota 371, la ban ─────────────────────────────────────────────────
def _fisa(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT a.denumire, m.cantitate, m.valoare FROM miscari_stoc m JOIN articole a ON a.id = m.articol_id "
                    "WHERE m.factura_id = %s ORDER BY m.id", (fid,))
        return [(d, _D(q), _D(v)) for d, q, v in cur.fetchall()]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c80_reducerea_de_document_se_imparte_pe_articolele_cotei_nu_devine_articol(conn_y2):
    from core import stocuri_cv_api as _cv
    # 21%: două articole 100,00 + 200,00 și o reducere de document 10,00; 11%: un articol 300,00 cu reducerea 30,00
    x = xml_factura("Y2-C80-S", linii=[(1, "100.00", 21), (2, "200.00", 21), (6, "300.00", 11)],
                    reduceri=[(False, "10.00", 21, "Rabat"), (False, "30.00", 11, "Rabat")],
                    subtotaluri=[("290.00", "60.90", 21), ("270.00", "29.70", 11)], bt109="560.00", bt110="90.60", bt112="650.60")
    fid = _importa(conn_y2, x)
    _cv.intrare_din_factura(conn_y2, _SCHEMA, fid, "371", "2026-07-10")
    fisa = _fisa(conn_y2, fid)
    # OMFP 1802/2014 pct.76 alin.(1): reducerile comerciale de pe factură reduc costul de achiziție — împărțite proporțional pe articolele
    # cotei (10,00 × 100/300 = 3,33; ultima linie ia restul 6,67), niciun articol „Reducere”
    assert fisa == [("Marfa 1", _D(1), _D("96.67")), ("Marfa 2", _D(2), _D("193.33")), ("Marfa 3", _D(6), _D("270.00"))], fisa
    assert sum(v for _d, _q, v in fisa) == sum(s for a, b, s in _note(conn_y2, fid) if a == "371") == _D("560.00")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c82_fisa_de_magazie_are_valoarea_liniei_din_xml(conn_y2):
    from core import stocuri_cv_api as _cv
    fid = _importa(conn_y2, XML_C82)
    _cv.intrare_din_factura(conn_y2, _SCHEMA, fid, "371", "2026-07-10")
    assert _fisa(conn_y2, fid) == [("Marfa 1", _D("3.333"), _D("100.50"))]   # BT-131, ca nota 371 (nu 3,333 × 30,15 = 100,49)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_datele_existente_migrarea_completeaza_din_xml_bt131_si_reducerile_de_document(conn_y2):
    """Comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”. O factură importată ÎNAINTE de reparație (liniile fără
    BT-131, fără reducerile de document) se completează din XML-ul ei păstrat; nota contării nu se atinge, dar factura se numește."""
    from core import migrare_valoare_neta_linie as _m
    fid_c80 = _importa(conn_y2, XML_C80)                 # contată: are nota
    fid_c82 = _importa(conn_y2, XML_C82, conteaza=False)
    with conn_y2.cursor() as cur:   # starea de dinainte de reparație: importul vechi nu scria nici BT-131, nici liniile de document
        cur.execute("DELETE FROM factura_linii WHERE nivel_document")
        cur.execute("UPDATE factura_linii SET valoare_neta = NULL")
    rez = _m.aplica(conn_y2, _SCHEMA)
    assert (rez["linii_bt131"], rez["linii_document"], rez["sarite"]) == (3, 3, []), rez
    assert [f for f, _n in rez["cu_nota"]] == [fid_c80], rez        # nota scrisă pe baza fără reducere: numită, nu rescrisă
    with conn_y2.cursor() as cur:
        cur.execute("SELECT factura_id, valoare_neta, nivel_document FROM factura_linii ORDER BY id")
        linii = cur.fetchall()
    assert [(f, v) for f, v, nd in linii if f == fid_c82] == [(fid_c82, _D("100.50"))]   # BR-DEC-23: BT-131 de pe factură
    assert sorted(v for f, v, nd in linii if f == fid_c80 and nd) == [_D("-50.00"), _D("-30.00"), _D("20.00")]   # BR-CO-13
    assert _m.aplica(conn_y2, _SCHEMA)["linii_document"] == 0   # idempotentă
