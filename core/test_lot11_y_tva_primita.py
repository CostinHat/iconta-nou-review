# -*- coding: utf-8 -*-
"""Lotul 11, C79 — TVA-ul deductibil al facturii PRIMITE e cel de pe factura furnizorului, nu recalculul din baze.

Defectul (fixture-ul din `core/test_418_import_efactura.py`): XML-ul e-Factura spune TVA 143,52 lei, nota de contare scria 143,54 lei
(483,50 + 200,00) × 21%. Pe XML-ul cu defalcarea BG-23 (rotunjită de furnizor pe linii), aceeași clasă: nota și D300 luau recalculul.

Temei:
  * CF art.299 alin.(1) lit.a: „pentru taxa datorată sau achitată, aferentă bunurilor care i-au fost ori urmează să îi fie livrate [...]
    să dețină o factură emisă în conformitate cu prevederile art. 319” — deducerea se face pe baza facturii;
  * CF art.319 alin.(20) lit.j: factura cuprinde „indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei, în funcție
    de cotele taxei” — taxa e cea scrisă pe factură, pe cote;
  * EN 16931 (legarea UBL a e-Factura): defalcarea TVA BG-23 = `cac:TaxTotal/cac:TaxSubtotal` (BT-116 baza, BT-117 TVA-ul, BT-118 categoria,
    BT-119 cota); BT-110 = `TaxTotal/TaxAmount` în moneda documentului; BR-CO-18 „An Invoice shall at least have one VAT breakdown group”.
Schemă efemeră din tenant_template, în tranzacție anulată; ANAF nu se cheamă."""
import ast
import io
import os
import re
from decimal import Decimal

import pytest

from core import db as _db
from core import efactura_import as _ef
from core import tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "tenant_test_lot11_y_c79"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Factura furnizorului cu două cote; TVA-ul ei pe cote e rotunjit de furnizor (pe linii), deci diferă de recalculul din baze:
#:   21%: baza 101,17 + 101,16 = 202,33; recalcul 202,33 × 21% = 42,4893 -> 42,49; pe factură 42,51 (+0,02)
#:   11%: baza 150,05;                    recalcul 150,05 × 11% = 16,5055 -> 16,51; pe factură 16,49 (−0,02)
#: BT-110 = 42,51 + 16,49 = 59,00 (recalcul 59,00 — totalul coincide, cotele nu). CUI furnizor 14399840 (DANTE INTERNATIONAL SA,
#: cifra de control verificată în `test_cui_de_test_valid`), cumpărător 9010105 (cifră de control verificată acolo).
_XML_DOUA_COTE = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>Y-C79-1</cbc:ID><cbc:IssueDate>2026-07-10</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>DANTE INTERNATIONAL SA</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
 <cac:AccountingCustomerParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO9010105</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>Y C79 SRL</cbc:RegistrationName></cac:PartyLegalEntity>
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
  <cac:Item><cbc:Name>Marfa A</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">101.17</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">101.16</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Marfa B</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">101.16</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
 <cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="RON">150.05</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Carte</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>11</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  <cac:Price><cbc:PriceAmount currencyID="RON">150.05</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
</Invoice>"""


def _xml(**inloc):
    x = _XML_DOUA_COTE
    for a, b in inloc.items():
        x = x.replace(a, b)
    return x


def _cui_valid(cui):   # CLAUDE.md „Date de test — CUI/CNP”: algoritmul oficial al cifrei de control
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def test_cui_de_test_valid():
    assert _cui_valid("14399840") and _cui_valid("9010105")


# ── parserul: TVA-ul facturii pe cote ───────────────────────────────────────────────────────────────────────
def test_parserul_citeste_defalcarea_bg23_a_furnizorului():
    f = _ef.parseaza_xml(_XML_DOUA_COTE.encode(), "9010105")
    assert f["tva"] == "59.00"
    # EN 16931 BG-23: BT-118 categoria, BT-119 cota, BT-116 baza, BT-117 TVA-ul — cum le-a scris furnizorul
    assert [(c["categorie"], c["cota"], c["baza"], c["tva"], c["sursa"]) for c in f["tva_cote"]] == [
        ("S", "21", "202.33", "42.51", "BG-23"), ("S", "11", "150.05", "16.49", "BG-23")]


def test_bt110_e_cel_din_moneda_documentului_nu_primul_taxtotal():
    """EN 16931 / UBL: BT-110 = `TaxTotal/TaxAmount` în moneda documentului (BT-5); BT-111 = alt `TaxTotal`, în moneda de contabilizare a
    TVA-ului, fără defalcare — ordinea lor nu e impusă. Înainte, parserul lua primul `TaxTotal`."""
    x = _xml(**{"RON": "EUR", "<cac:TaxTotal><cbc:TaxAmount currencyID=\"EUR\">59.00":
                "<cbc:TaxCurrencyCode>RON</cbc:TaxCurrencyCode><cac:TaxTotal><cbc:TaxAmount currencyID=\"RON\">293.00</cbc:TaxAmount>"
                "</cac:TaxTotal><cac:TaxTotal><cbc:TaxAmount currencyID=\"EUR\">59.00"})
    f = _ef.parseaza_xml(x.encode(), "9010105")
    assert (f["moneda"], f["tva"]) == ("EUR", "59.00")
    assert [c["tva"] for c in f["tva_cote"]] == ["42.51", "16.49"]


def test_fara_bg23_bt110_merge_pe_singura_cota_iar_pe_doua_cote_nu_se_ghiceste():
    fara = re.sub(r"<cac:TaxSubtotal>.*?</cac:TaxSubtotal>", "", _XML_DOUA_COTE, flags=re.S)
    assert _ef.tva_cote_din_xml(fara) == []          # două cote, fără defalcare: împărțirea ar fi ghicită
    o_cota = fara.replace("<cbc:Percent>11</cbc:Percent>", "<cbc:Percent>21</cbc:Percent>")
    # baza: BT-109 (totalul fără TVA de pe factură)
    assert _ef.tva_cote_din_xml(o_cota) == [{"categorie": "S", "cota": "21", "baza": "352.38", "tva": "59.00", "sursa": "BT-110"}]
    fara_109 = o_cota.replace('<cbc:TaxExclusiveAmount currencyID="RON">352.38</cbc:TaxExclusiveAmount>', "")
    assert _ef.tva_cote_din_xml(fara_109)[0]["baza"] == "352.38"   # Σ BT-131: 101,17 + 101,16 + 150,05


def test_sablonul_poarta_blocul_migrarii():
    """Sursa unică a structurii: blocul din tenant_template.sql = `migrare_factura_tva_cote.bloc_template()`."""
    from core import migrare_factura_tva_cote as _m
    assert _m.bloc_template() in io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()


def test_importul_trece_numai_prin_factura_importata():
    """GARDA: orice drum de PRODUCȚIE care introduce o factură din XML (`_factura_din_parsat`) trece prin `uc_tenants._factura_importata`,
    care îi salvează și TVA-ul pe cote — altfel factura nouă s-ar conta pe recalcul. Permise: învelișul `_factura_importata` și învelișul
    HTTP din `main.py` (folosit de scripturi / teste)."""
    gasite = []
    for d in ("core", ""):
        for nume in sorted(os.listdir(os.path.join(_RAD, d) if d else _RAD)):
            if not nume.endswith(".py") or nume.startswith("test_") or nume == "conftest.py":
                continue
            cale = os.path.join(_RAD, d, nume) if d else os.path.join(_RAD, nume)
            arbore = ast.parse(io.open(cale, encoding="utf-8").read())
            for fn in ast.walk(arbore):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for n in ast.walk(fn):
                    if isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) == "_factura_din_parsat":
                        gasite.append((os.path.join(d, nume) if d else nume, fn.name))
    permise = {("core/uc_tenants.py", "_factura_importata"), ("main.py", "_factura_din_parsat")}
    assert set(gasite) <= permise, sorted(set(gasite) - permise)
    assert ("core/uc_tenants.py", "_factura_importata") in gasite


# ── contarea și D300, pe o schemă efemeră ───────────────────────────────────────────────────────────────────
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
def conn_c79():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
                    "tva_la_incasare, platitor_tva_anaf_inceput, declarant_nume, declarant_prenume, declarant_functie, forma_juridica, "
                    "capital_subscris, telefon) VALUES (1,'Y C79 SRL','9010105','Str Test 1','Bucuresti','B','4690','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'lunar',false,'2025-01-01','Popescu','Ion','ADMINISTRATOR','SRL',200,'0712345678')")
            yield _FaraCommit(conn)
        finally:
            conn.rollback()


def _importa_si_conteaza(conn, xml):
    from core import contare_facturi as _cf, uc_tenants
    f = _ef.parseaza_xml(xml.encode(), "9010105")
    with conn.cursor() as cur:
        fid, nou = uc_tenants._factura_importata(cur, _SCHEMA, f)
        assert nou
        cur.execute("UPDATE facturi SET tert_platitor_tva = true WHERE id = %s", (fid,))
    with _cf.cursor_dict(conn) as cur:
        _cf.contabilizeaza(cur, _SCHEMA, fid, automat=True, cont_cheltuiala="371")
    with conn.cursor() as cur:
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s ORDER BY l.id", (fid,))
        return fid, [(a, b, Decimal(c)) for a, b, c in cur.fetchall()]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nota_si_d300_iau_tva_ul_de_pe_factura_furnizorului(conn_c79):
    from core import d300, duk
    fid, note = _importa_si_conteaza(conn_c79, _XML_DOUA_COTE)
    tva = [(a, b, s) for a, b, s in note if a == "4426"]
    # CF art.299 alin.(1) lit.a + art.319 alin.(20) lit.j: TVA-ul cotei de pe factură — 42,51 (nu recalculul 42,49) și 16,49 (nu 16,51)
    assert tva == [("4426", "401", Decimal("16.49")), ("4426", "401", Decimal("42.51"))], note   # în ordinea cotelor
    # nota se închide pe totalul facturii (BT-112 411,38): baze 352,38 + TVA 59,00
    assert sum(s for a, b, s in note if b == "401") == Decimal("411.38"), note
    with conn_c79.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata', document_ref = COALESCE(NULLIF(document_ref, ''), 'Y-C79-1') "
                    "WHERE status <> 'validata'")
    xml, res = d300.genereaza(conn_c79, _SCHEMA, Perioada(2026, luna=7))
    # D300 rd.24 (R22) / rd.25 (R23), col.2 = TVA-ul deductibil de pe facturi: 42,51 -> 43 (recalculul 42,49 -> 42); 16,49 -> 16 (nu 17)
    assert (res.R.get("R22_1"), res.R.get("R22_2"), res.R.get("R23_1"), res.R.get("R23_2")) == (202, 43, 150, 16), res.R
    # a doua cale (d300_reconciliere, SQL propriu) ajunge la aceleași cifre — altfel `genereaza` ar fi refuzat decontul
    assert duk.valideaza(xml, "d300", an=2026, luna=7)["stare"] == "valid", duk.valideaza(xml, "d300", an=2026, luna=7)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a_doua_cale_d300_citeste_singura_tva_ul_facturii(conn_c79):
    """`d300_reconciliere` nu importă `contare_facturi` / `repo_efactura` (calea 2 e independentă), dar ajunge la TVA-ul facturii."""
    from core import d300_reconciliere as _rec
    _importa_si_conteaza(conn_c79, _XML_DOUA_COTE)
    import datetime as _dt
    _col, ded = _rec._agrega_independent(conn_c79, _dt.date(2026, 7, 1), _dt.date(2026, 8, 1))
    assert ded == {21: (202, 43), 11: (150, 16)}, ded   # CF art.299 alin.(1) lit.a: TVA-ul de pe factură
    mod = {n.module for n in ast.walk(ast.parse(io.open(_rec.__file__, encoding="utf-8").read())) if isinstance(n, ast.ImportFrom)}
    assert not mod & {"core.contare_facturi", "core.repo_efactura", "core.efactura_import"}, mod


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cotele_defalcarii_altele_decat_ale_liniilor_se_refuza_numit(conn_c79):
    """Defalcarea cu o cotă pe care nu stă nicio linie: TVA-ul de dedus nu se poate împărți pe cote fără a ghici -> refuz numit (contarea o
    face omul), nu recalcul tăcut."""
    from core import contare_facturi as _cf, uc_tenants
    x = _XML_DOUA_COTE.replace("<cbc:Percent>11</cbc:Percent><cac:TaxScheme>", "<cbc:Percent>9</cbc:Percent><cac:TaxScheme>")
    f = _ef.parseaza_xml(x.encode(), "9010105")
    with conn_c79.cursor() as cur:
        fid, _n = uc_tenants._factura_importata(cur, _SCHEMA, f)
    with _cf.cursor_dict(conn_c79) as cur, pytest.raises(_cf.RefuzContare) as e:
        _cf.contabilizeaza(cur, _SCHEMA, fid, automat=True, cont_cheltuiala="371")
    assert e.value.cod == "TVA_FACTURA_ALTE_COTE" and "9%" in e.value.mesaj and "11%" in e.value.mesaj, e.value.mesaj


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_introdusa_fara_xml_ramane_pe_tva_ul_scris_pe_ea(conn_c79):
    """Factura primită introdusă în aplicație (fără XML): TVA-ul scris pe ea e cel al aplicației, din linii (`facturi.tva`) — nota îl ia."""
    from core import contare_facturi as _cf, facturi_api
    r = facturi_api.creeaza_factura(conn_c79, "Y-MAN-1", "2026-07-11", "primita",
                                    [{"descriere": "Marfa", "cantitate": 1, "pret_unitar": "202.33", "cota_tva": 21}],
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="14399840", status="importata", tert_platitor_tva=True)
    fid = r["factura_id"]
    with _cf.cursor_dict(conn_c79) as cur:
        assert _cf.tva_facturii_pe_cote(cur, _SCHEMA, {"id": fid}, [{"cota_tva": 21}]) is None
        cur.execute("SELECT tva FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone()["tva"] == Decimal("42.49")
