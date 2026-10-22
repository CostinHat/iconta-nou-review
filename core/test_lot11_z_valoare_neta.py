# -*- coding: utf-8 -*-
"""Lotul 11, subagentul Z — clasa C82 în consumatorii rămași: valoarea liniei unei facturi IMPORTATE e BT-131 din XML-ul e-Factura
(`factura_linii.valoare_neta`), nu cantitate × prețul unitar ținut la 2 zecimale. Consumatorii de aici: exportul SAGA, exportul WinMentor,
alocarea plății pe cote la TVA la încasare (`tva_incasare.aloca_pe_cote`, prin `d300._pull_la_incasare`), detaliul facturii
(`facturi_api.detalii_factura`, ecranul) și PDF-ul facturii (`factura_pdf.genereaza_pdf`). Facturile făcute în aplicație (valoare_neta
NULL) rămân pe regula de până acum.

Cazul: 3,333 bucăți, BT-131 = 100,50 lei (preț 30,1530…); prețul păstrat la 2 zecimale (30,15) × 3,333 = 100,48995 -> 100,49. TVA 21%:
100,50 × 21% = 21,105 -> 21,11 (din 100,49: 21,10).

Temei (structură, regulă de validator EN 16931 — nu normă; `EN16931-model.sch`): BR-DEC-23 „The allowed maximum number of decimals for the
Invoice line net amount (BT-131) is 2.”; BR-S-08 (baza cotei = Σ BT-131 ale liniilor cu acea cotă). Normă: CF art.319 alin.(20) lit.g
(factura cuprinde „[...] valoarea fiecărei operațiuni [...]” — valoarea liniei e cea de pe factură) și CF art.282 alin.(8) (încasarea
„include și taxa aferentă” — alocarea pe cote după valoarea facturată).
Schemă efemeră din tenant_template, în tranzacție anulată."""
import io
import os
import re
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import db as _db
from core import efactura_import as _ef
from core import tenant_provisioning as _tp

_SCHEMA = "tenant_test_lot11_z"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_D = Decimal
_CUI_FIRMA, _CUI_TERT = "9010105", "14399840"   # cifra de control verificată în `test_cui_de_test_valid`


def _saga(xml):
    """XML-ul SAGA parsat: ([(Valoare, TVA) pe fiecare <Linie>], (TotalValoare, TotalTVA, Total) din <Sumar>) — pe ELEMENTE, nu pe sub-șir."""
    r = ET.fromstring(xml)
    s = r.find(".//Sumar")
    return ([(ln.findtext("Valoare"), ln.findtext("TVA")) for ln in r.iter("Linie")],
            (s.findtext("TotalValoare"), s.findtext("TotalTVA"), s.findtext("Total")))


def _winmentor(txt, cheie):
    """Valorile cheii `cheie` din fișierul WinMentor (rânduri `cheie=valoare`), în ordine — pe CÂMP, nu pe sub-șir."""
    return [v for k, v in (ln.split("=", 1) for ln in txt.splitlines() if ln.count("=")) if k == cheie]


def _cui_valid(cui):   # CLAUDE.md „Date de test — CUI/CNP”: algoritmul oficial al cifrei de control
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def test_cui_de_test_valid():
    assert _cui_valid(_CUI_FIRMA) and _cui_valid(_CUI_TERT)


def _xml(numar, furnizor, client, linii, bt109, bt110, bt112, subtotaluri):
    """XML e-Factura minim (UBL 2.1 / CIUS-RO): `linii` = [(cantitate, BT-131, cotă)], `subtotaluri` = [(BT-116, BT-117, cotă)]."""
    cm = 'currencyID="RON"'
    parte = ('<cac:%s><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>'
             '</cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>%s</cbc:RegistrationName></cac:PartyLegalEntity></cac:Party>'
             '</cac:%s>')
    x = ['<?xml version="1.0" encoding="UTF-8"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
         'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
         'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">',
         "<cbc:ID>%s</cbc:ID><cbc:IssueDate>2026-07-10</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>" % numar,
         parte % ("AccountingSupplierParty", furnizor[0], furnizor[1], "AccountingSupplierParty"),
         parte % ("AccountingCustomerParty", client[0], client[1], "AccountingCustomerParty"),
         "<cac:TaxTotal><cbc:TaxAmount %s>%s</cbc:TaxAmount>" % (cm, bt110)]
    for b, t, c in subtotaluri:
        x.append("<cac:TaxSubtotal><cbc:TaxableAmount %s>%s</cbc:TaxableAmount><cbc:TaxAmount %s>%s</cbc:TaxAmount><cac:TaxCategory><cbc:ID>S"
                 "</cbc:ID><cbc:Percent>%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory></cac:TaxSubtotal>"
                 % (cm, b, cm, t, c))
    x.append("</cac:TaxTotal><cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount %s>%s</cbc:TaxExclusiveAmount><cbc:TaxInclusiveAmount %s>%s"
             "</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>" % (cm, bt109, cm, bt112))
    for i, (q, le, c) in enumerate(linii, 1):
        pret = (_D(le) / _D(q)).quantize(_D("0.0001"))
        x.append('<cac:InvoiceLine><cbc:ID>%d</cbc:ID><cbc:InvoicedQuantity unitCode="H87">%s</cbc:InvoicedQuantity><cbc:LineExtensionAmount %s>'
                 "%s</cbc:LineExtensionAmount><cac:Item><cbc:Name>Marfa Z %d</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>"
                 "%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory></cac:Item><cac:Price>"
                 "<cbc:PriceAmount %s>%s</cbc:PriceAmount></cac:Price></cac:InvoiceLine>" % (i, q, cm, le, i, c, cm, pret))
    x.append("</Invoice>")
    return "".join(x)


_FIRMA, _TERT = (_CUI_FIRMA, "Z SRL"), (_CUI_TERT, "DANTE INTERNATIONAL SA")
_C82 = dict(linii=[("3.333", "100.50", 21)], bt109="100.50", bt110="21.11", bt112="121.61", subtotaluri=[("100.50", "21.11", 21)])
#: factura EMISĂ de firmă, venită din XML (`/import-efactura`): furnizorul e firma
XML_EMISA = _xml("Z-EMISA-1", _FIRMA, _TERT, **_C82)
#: factura PRIMITĂ de la furnizor
XML_PRIMITA = _xml("Z-PRIMITA-1", _TERT, _FIRMA, **_C82)


# ── alocarea plății pe cote (pur) ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_aloca_pe_cote_ia_valoarea_liniei_de_pe_factura():
    from core import tva_incasare as _tvi
    # 1.000 de șuruburi cu BT-131 = 4,00 lei (preț 0,004 -> 0,00 la 2 zecimale) la 21% + un serviciu 100,00 la 11%: 4,84 + 111,00 = 115,84
    linii = [("1000", "0.00", 21, "4.00"), ("1", "100.00", 11, "100.00")]
    r = {d["cota"]: d["suma"] for d in _tvi.aloca_pe_cote(_D("115.84"), linii, None)}
    # CF art.282 alin.(8): încasarea „include și taxa aferentă” — se împarte după valoarea facturată a cotei (BT-131 × (100 + cotă) / 100)
    assert (r[21].quantize(_D("0.01")), r[11].quantize(_D("0.01"))) == (_D("4.84"), _D("111.00")), r   # din cantitate × preț: 0,00 / 115,84


def test_aloca_pe_cote_fara_valoare_de_pe_factura_ramane_pe_cantitate_ori_pret():
    from core import tva_incasare as _tvi
    # factura făcută în aplicație: tuplul (cantitate, preț, cotă) și valoare_neta NULL dau aceeași alocare ca până acum
    vechi = _tvi.aloca_pe_cote(_D("100"), [("3", "19.99", 21), ("1.333", "1.50", 11)], None)
    nou = _tvi.aloca_pe_cote(_D("100"), [("3", "19.99", 21, None), ("1.333", "1.50", 11, None)], None)
    assert vechi == nou
    g21, g11 = _D("3") * _D("19.99") * 121 / 100, _D("1.333") * _D("1.50") * 111 / 100
    assert {d["cota"]: d["suma"] for d in vechi} == {21: _D(100) * g21 / (g21 + g11), 11: _D(100) * g11 / (g21 + g11)}


# ── pe o schemă efemeră ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_z():
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
                    "capital_subscris, telefon) VALUES (1,'Z SRL',%s,'Str Test 1','Bucuresti','B','4690','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'lunar',false,'2025-01-01','Popescu','Ion','ADMINISTRATOR','SRL',200,'0712345678')",
                    (_CUI_FIRMA,))
            yield conn
        finally:
            conn.rollback()


def _importa(conn, xml, linie1=(_D("3.333"), _D("30.15"), _D("100.50"))):
    """Drumul importului (`uc_tenants._factura_importata`, același pentru `/import-efactura` și validarea facturii primite)."""
    from core import uc_tenants
    f = _ef.parseaza_xml(xml.encode(), _CUI_FIRMA)
    with conn.cursor() as cur:
        fid, nou = uc_tenants._factura_importata(cur, _SCHEMA, f)
        assert nou
        cur.execute("SELECT cantitate, pret_unitar, valoare_neta FROM factura_linii WHERE factura_id = %s ORDER BY id LIMIT 1", (fid,))
        assert cur.fetchone() == linie1   # prețul la 2 zecimale; BT-131 păstrat exact (Y2)
    return fid


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pull_la_incasare_da_alocarii_valoarea_liniei(conn_z, monkeypatch):
    """`d300._pull_la_incasare` duce valoarea liniei de pe factură (`repo_d300.select_facturi` -> `valoare_neta`) până la alocare. Citirea
    liniilor e cea reală, pe schema efemeră; numai decontarea perioadei și regimul facturii sunt date de test."""
    from core import contare_facturi as _cf, d300, tva_incasare as _tvi
    xml = _xml("Z-INC-1", _FIRMA, _TERT, linii=[("1000", "4.00", 21), ("1", "100.00", 11)], bt109="104.00", bt110="11.84",
               bt112="115.84", subtotaluri=[("4.00", "0.84", 21), ("100.00", "11.00", 11)])
    fid = _importa(conn_z, xml, linie1=(_D("1000.000"), _D("0.00"), _D("4.00")))   # 4,00 / 1.000 = 0,004 -> prețul 0,00
    monkeypatch.setattr(d300._repo, "select_inregistrari", lambda cur, st, i, s: [{"fid": fid, "settled": _D("115.84"), "directie": "emisa"}])
    monkeypatch.setattr(_tvi, "regim", lambda cur, schema, f: _tvi.REGIM_INCASARE)
    with _cf.cursor_dict(conn_z) as cur:
        out = d300._pull_la_incasare(cur, "2026-07-01", "2026-08-01")
    r = {d["cota"]: d["suma"].quantize(_D("0.01")) for d in out[0]["decontari"]}
    assert r == {21: _D("4.84"), 11: _D("111.00")}, r   # CF art.282 alin.(8); din cantitate × preț: {21: 0,00, 11: 115,84}
    print("TVA la încasare, alocarea pe cote:", {k: str(v) for k, v in r.items()})


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_la_incasare_deducerea_platii_pe_cotele_valorilor_din_xml(conn_z):
    """De capăt, pe schema efemeră: firma în sistemul TVA la încasare din 01.07.2026; factura primită importată (1.000 de șuruburi cu BT-131
    4,00 lei la 21% + un serviciu de 100,00 lei la 11%), contată; plata integrală prin bancă (115,84); notele validate; D300 pe iulie."""
    from core import contare_facturi as _cf, d300, reconciliere_api
    from core.common import Perioada
    with conn_z.cursor() as cur:
        cur.execute("UPDATE firma_profil SET tva_la_incasare = true WHERE id = 1")
        cur.execute("INSERT INTO tva_incasare_perioade (de_la) VALUES ('2026-07-01')")
    xml = _xml("Z-INC-2", _TERT, _FIRMA, linii=[("1000", "4.00", 21), ("1", "100.00", 11)], bt109="104.00", bt110="11.84",
               bt112="115.84", subtotaluri=[("4.00", "0.84", 21), ("100.00", "11.00", 11)])
    fid = _importa(conn_z, xml, linie1=(_D("1000.000"), _D("0.00"), _D("4.00")))
    with conn_z.cursor() as cur:
        cur.execute("UPDATE facturi SET tert_platitor_tva = true, tert_oras = 'Bucuresti', tert_judet = 'B' WHERE id = %s", (fid,))
    with _cf.cursor_dict(conn_z) as cur:
        _cf.contabilizeaza(cur, _SCHEMA, fid, automat=True, cont_cheltuiala="628")
    with conn_z.cursor() as cur:   # plata din extrasul de bancă, legată de factură (reconcilierea bancară)
        cur.execute("INSERT INTO extras_linii (data, descriere, suma, tip) VALUES ('2026-07-20', 'plata Z-INC-2', 115.84, 'plata') RETURNING id")
        lid = cur.fetchone()[0]
    reconciliere_api.conteaza(conn_z, _SCHEMA, lid, alocari=[{"factura_id": fid, "suma": _D("115.84")}])
    with conn_z.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata', document_ref = COALESCE(NULLIF(document_ref, ''), 'Z') WHERE status <> 'validata'")
    xml_d300, res = d300.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=7))
    from core import duk
    v = duk.valideaza(xml_d300, "d300", an=2026, luna=7)
    assert v["stare"] == "valid", v   # validatorul oficial D300 (DUK)
    # CF art.297 alin.(3) (deducerea amânată până la plată) + art.282 alin.(8) (plata „include și taxa aferentă”), pe valoarea facturată a
    # cotelor: 21% bază 4,00 / TVA 0,84 -> 4 / 1; 11% bază 100,00 / TVA 11,00 -> 100 / 11. Din cantitate × preț: 21% nimic, 11% 104 / 11.
    assert (res.R.get("R22_1"), res.R.get("R22_2"), res.R.get("R23_1"), res.R.get("R23_2")) == (4, 1, 100, 11), res.R
    print("D300 la încasare (R22_1, R22_2, R23_1, R23_2):", (res.R.get("R22_1"), res.R.get("R22_2"), res.R.get("R23_1"), res.R.get("R23_2")))
    from core import d394
    x394, _r394 = d394.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=7))
    ded = {c: re.search(r'\btvaDed%d="(\d+)"' % c, x394) for c in (21, 11)}
    # OPANAF 2194/2025 (D394) pct.5.2 — tvaDed: TVA-ul dedus la plată, pe cote (aceeași alocare ca D300): 21% 1, 11% 11 (din cantitate × preț:
    # 0 și 11)
    assert {c: m and m.group(1) for c, m in ded.items()} == {21: "1", 11: "11"}, x394[:2000]
    v4 = duk.valideaza(x394, "d394", an=2026, luna=7)
    assert v4["stare"] == "valid", v4
    print("D394 la încasare tvaDed21 / tvaDed11:", ded[21].group(1), "/", ded[11].group(1))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_export_saga_al_facturii_emise_importate_are_valoarea_din_xml(conn_z):
    from core import export_saga as _xs
    fid = _importa(conn_z, XML_EMISA)
    assert _xs.facturi_emise_luna(conn_z, _SCHEMA, 2026, 7) == [fid]   # intră în exportul lunii (butonul „Export SAGA lună”)
    firma, factura, linii = _xs.date_factura(conn_z, _SCHEMA, fid)
    xml = _xs.xml_factura(firma, factura, linii)
    linii_xml, sumar = _saga(xml)
    # BR-DEC-23: Valoare = BT-131 100,50 (nu 3,333 × 30,15 = 100,49); TVA-ul liniei 100,50 × 21% = 21,105 -> 21,11 (nu 21,10)
    assert linii_xml == [("100.50", "21.11")], xml
    assert sumar == ("100.50", "21.11", "121.61"), xml[-400:]   # BR-S-08: baza = Σ BT-131; total = 100,50 + 21,11
    print("SAGA:", linii_xml, sumar)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_export_winmentor_al_facturii_emise_importate_are_tva_ul_din_valoarea_din_xml(conn_z):
    from core import export_saga as _xs, export_winmentor as _wm
    fid = _importa(conn_z, XML_EMISA)
    firma, factura, linii = _xs.date_factura(conn_z, _SCHEMA, fid)
    txt = _wm.facturi_txt(firma, [(factura, linii)], 2026, 7)
    # BR-DEC-23: TVA-ul liniei din BT-131: 100,50 × 21% = 21,11 (din 3,333 × 30,15: 21,10)
    assert _winmentor(txt, "Item_1_TVA") == ["21.11"], txt
    print("WinMentor:", [ln for ln in txt.splitlines() if ln.startswith("Item_")])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_detaliul_si_pdf_ul_facturii_primite_importate_au_valoarea_din_xml(conn_z):
    from core import facturi_api, factura_pdf as _pdf, firma_profil_api as _fp
    fid = _importa(conn_z, XML_PRIMITA)
    f = facturi_api.detalii_factura(conn_z, fid)
    assert f["linii"][0]["valoare_neta"] == _D("100.50"), f["linii"]   # ecranul arată valoarea liniei din ea (facturi_ecran.js)
    from pypdf import PdfReader
    text = re.sub(r"\s+", " ", "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(_pdf.genereaza_pdf(_fp.citeste_profil(conn_z), f))).pages))
    # CF art.319 alin.(20) lit.g / BR-DEC-23: valoarea liniei și baza cotei = 100,50 (nu 100,49)
    assert "100,49" not in text and re.search(r"Bază 21% 100,50", text), text[:1500]
    print("PDF:", re.search(r"Marfa Z 1.{0,80}", text).group(0), "|", re.search(r"Bază 21%.{0,40}", text).group(0))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_facuta_in_aplicatie_ramane_pe_cantitate_ori_pret(conn_z):
    """valoare_neta NULL (factura făcută în aplicație): exporturile, detaliul și PDF-ul — cantitate × preț la ban, ca până acum."""
    from core import export_saga as _xs, export_winmentor as _wm
    fid = _importa(conn_z, XML_EMISA)
    with conn_z.cursor() as cur:
        cur.execute("UPDATE factura_linii SET valoare_neta = NULL WHERE factura_id = %s", (fid,))
    firma, factura, linii = _xs.date_factura(conn_z, _SCHEMA, fid)
    assert _saga(_xs.xml_factura(firma, factura, linii))[0] == [("100.49", "21.10")]   # 3,333 × 30,15 = 100,48995 -> 100,49; × 21% = 21,10
    assert _winmentor(_wm.facturi_txt(firma, [(factura, linii)], 2026, 7), "Item_1_TVA") == ["21.10"]


# ── ecranul de detaliu (static/js/ecrane/facturi_ecran.js), pe node ─────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not __import__("shutil").which("node"), reason="node lipsește")
def test_ecranul_de_detaliu_arata_valoarea_liniei_din_xml():
    """`detaliiFactura`: valoarea liniei și baza cotei din `valoare_neta` (cum vine din API: număr JSON), altfel cantitate × preț."""
    import json
    import subprocess
    em = io.open(os.path.join(_RAD, "static", "js", "ecrane", "emitere_ecran.js"), encoding="utf-8").read()
    fe = io.open(os.path.join(_RAD, "static", "js", "ecrane", "facturi_ecran.js"), encoding="utf-8").read()
    m = re.search(r"const _BI = BigInt[^\n]*\nfunction _zec\(.*?\nexport function tvaDocument\(linii\) \{.*?\n\}\n", em, re.S)
    d = re.search(r"  const _deCalcul = .*?;\n", fe, re.S)
    assert m and d, "tvaDocument / _deCalcul au dispărut"
    cazuri = [{"cantitate": 3.333, "pret_unitar": 30.15, "cota_tva": 21, "valoare_neta": 100.5},
              {"cantitate": 3.333, "pret_unitar": 30.15, "cota_tva": 21, "valoare_neta": None}]
    js = (m.group(0).replace("export function", "function") + d.group(0) +
          "const c = %s; console.log(JSON.stringify(c.map((l) => [tvaDocument([_deCalcul(l, 0)]).baza, "
          "tvaDocument([_deCalcul(l, Number(l.cota_tva))]).pe_cote[21]])));" % json.dumps(cazuri))
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    # BR-DEC-23 / BR-S-08: importată -> linia 100,50, baza 21% 100,50, TVA 21,11; făcută în aplicație -> 100,49 / 21,10 (ca până acum)
    assert json.loads(r.stdout) == [[100.5, {"baza": 100.5, "tva": 21.11}], [100.49, {"baza": 100.49, "tva": 21.1}]], r.stdout


# ── GARDA: orice citire a liniilor care ia cantitate + preț aduce și valoarea de pe factură ─────────────────────────────────────────────
#: cititorii care iau `cantitate` și `pret_unitar` din `factura_linii` FĂRĂ `valoare_neta`, fiecare cu motivul pentru care nu primesc o
#: linie de factură importată (sau nu-i folosesc valoarea). Un cititor nou fără `valoare_neta` și fără motiv aici oprește poarta.
FARA_VALOARE_NETA = {
    "core/rapoarte_comerciale_api.py": "profitul pe produs: numai liniile cu `articol_id`; importul nu-l scrie (`repo_main.insert_factura_linii`)",
    "core/repo_borderou.py": "borderoul de achiziție: document al aplicației, fără XML",
    "core/repo_control_incrucisat.py": "controlul cotei standard: raportul TVA / bază, nu valoarea liniei",
    # [lotul 11, C86] `repo_efactura.linii_pentru_ubl` citește acum `valoare_neta` (stornarea unei facturi venite din XML poartă −BT-131), deci a
    # ieșit din listă
}
_SELECT_LINII = re.compile(r"SELECT\b(?:(?!SELECT\b).){0,900}?factura_linii\b", re.S)


def _cititori_fara_valoare_neta():
    """Pe CUVINTE din SQL (identificatori), nu pe sub-șir: `cantitate_veche` nu e coloana `cantitate`."""
    import glob
    out = set()
    for f in glob.glob(os.path.join(_RAD, "core", "*.py")) + [os.path.join(_RAD, "main.py")]:
        b = os.path.basename(f)
        if b.startswith(("test_", "migrare_")):
            continue
        src = io.open(f, encoding="utf-8").read()
        for m in _SELECT_LINII.finditer(src):
            coloane = set(re.findall(r"\w+", m.group(0).rsplit("FROM", 1)[0]))
            if coloane >= {"cantitate", "pret_unitar"} and not set(re.findall(r"\w+", m.group(0))) & {"valoare_neta"}:
                out.add("%s:%d" % (os.path.relpath(f, _RAD), src.count("\n", 0, m.start()) + 1))
    return out


def test_citirile_liniilor_aduc_valoarea_de_pe_factura():
    noi = sorted(x for x in _cititori_fara_valoare_neta() if x.split(":")[0] not in FARA_VALOARE_NETA)
    assert not noi, ("[lotul 11, C82] o citire din `factura_linii` ia cantitate × preț fără `valoare_neta` (BT-131 de pe factura importată): "
                     "adaug-o și folosește `tva_calcul.net_linie(cantitate, pret_unitar, valoare_neta)`, sau scrie motivul în "
                     "FARA_VALOARE_NETA: %s" % noi)
    # lista se strânge: un fișier scos din listă (citirea lui a primit `valoare_neta`) iese și de aici. Anti-vacuu: lista nu e goală, deci
    # egalitatea cere ca scanul să VADĂ cititorii ei (un regex rupt, care nu mai găsește niciun SELECT, pică aici)
    assert FARA_VALOARE_NETA
    assert {x.split(":")[0] for x in _cititori_fara_valoare_neta()} == set(FARA_VALOARE_NETA), _cititori_fara_valoare_neta()
