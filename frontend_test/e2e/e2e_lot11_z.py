# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.1 (verbatim în DECIZII „Comanda 11.1”), subagentul Z: clasa C82 în consumatorii rămași — valoarea liniei
unei facturi IMPORTATE e BT-131 din XML-ul e-Factura (`factura_linii.valoare_neta`), nu cantitate × prețul unitar ținut la 2 zecimale.

  * detaliul facturii (ecranul) și PDF-ul ei;
  * exporturile SAGA și WinMentor ale lunii;
  * TVA la încasare: plata facturii se împarte pe cote după valoarea liniilor de pe factură (D300 / D394).

Pașii, pe ecran / pe rutele ecranelor: Date firmă (+ „Aplică sistemul TVA la încasare”) -> Facturi -> „Facturi primite” -> „Importă XML
UBL” -> validarea facturii -> „Istoric facturi” -> „← luna” -> factura -> „PDF factură” / „Export SAGA lună” / „Export WinMentor lună” ->
Casă -> plata furnizorului -> „Validează” pe note -> Declarații -> D300 / D394 pe luna încheiată.
DATE DE PORNIRE fără ecran (declarate, regula lui 429): factura EMISĂ venită din XML intră numai prin `POST /tenants/{id}/import-efactura`
(ruta internă de încărcare manuală, fără buton — `main.py`, R70); testul o cheamă din pagină, cu sesiunea contului, ca orice cerere a
aplicației. Ridicarea de numerar din bancă (ca plata să încapă în casă) se scrie pe ruta formularului Casă (`POST casa/operatiuni`).
Furnizorul / clientul: DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md.

Temei: CF art.319 alin.(20) lit.g (factura cuprinde valoarea operațiunii — cea de pe factură); CF art.282 alin.(8) („fiecare încasare totală
sau parțială se consideră că include și taxa aferentă”); CF art.297 alin.(3) (firma în sistem: deducerea amânată până la plată). Structură
(EN 16931, regulă de validator, nu normă): BR-DEC-23 „The allowed maximum number of decimals for the Invoice line net amount (BT-131) is 2.”"""
import io
import re
import zipfile

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, _pdf_ok, _pdf_text, pregateste_firma
from e2e_lot11_t import _regimul_din_date_firma
from e2e_lot11_y2 import LUNA, ZI, _atr, _cifrele, _importa_si_valideaza, _ubl, _valideaza_notele_lunii, _xml_declaratie


@pytest.fixture()
def firma_z():
    for f in firma_noua():
        yield f


def _ubl_emisa(numar, cui_firma, nume_firma, linii, bt109, bt110, bt112, subtotaluri):
    """XML-ul e-Factura al unei facturi EMISE de firmă (furnizorul = firma, clientul = DANTE), în luna încheiată."""
    x = _ubl(numar, cui_firma, nume_firma, linii=linii, subtotaluri=subtotaluri, bt109=bt109, bt110=bt110, bt112=bt112)
    furnizor = re.search(r"<cac:AccountingSupplierParty>.*?</cac:AccountingSupplierParty>", x).group(0)
    client = re.search(r"<cac:AccountingCustomerParty>.*?</cac:AccountingCustomerParty>", x).group(0)
    inv = lambda s, din, in_: s.replace("<cac:%s>" % din, "<cac:%s>" % in_).replace("</cac:%s>" % din, "</cac:%s>" % in_)   # noqa: E731
    return x.replace(furnizor, "\0F").replace(client, "\0C").replace(
        "\0F", inv(client, "AccountingCustomerParty", "AccountingSupplierParty")).replace(
        "\0C", inv(furnizor, "AccountingSupplierParty", "AccountingCustomerParty"))


def _importa_emisa(patron, firma, nume, xml_doc):
    """`POST /tenants/{id}/import-efactura` (ruta internă, fără ecran), din pagină, cu sesiunea contului — multipart, ca un formular."""
    r = patron.pg.evaluate("""async ([c, n, x]) => {
        const fd = new FormData(); fd.append('fisiere', new Blob([x], {type: 'text/xml'}), n);
        const t = sessionStorage.getItem('iconta_token');
        const r = await fetch(c, {method: 'POST', headers: {Authorization: 'Bearer ' + t}, body: fd});
        return {status: r.status, json: await r.json()};
    }""", ["/tenants/%d/import-efactura" % firma["tenant_id"], nume + ".xml", xml_doc])
    j = _ok(r, "importul facturii emise")
    assert j.get("importate") == 1 and not j.get("erori"), j
    return sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % firma["schema"], (nume,))[0][0]


def _istoric_luna(patron, firma):
    """Facturi -> „Istoric facturi” -> „← luna” până la luna încheiată (titlul arată luna)."""
    patron.firma(firma["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg = patron.pg
    pg.click("#fac-istoric")
    pg.wait_for_selector("#fac-prev", timeout=25000)
    import datetime as _dt
    azi = _dt.date.today()
    for _ in range((azi.year - LUNA.an) * 12 + azi.month - LUNA.luna):
        pg.click("#fac-prev")
        pg.wait_for_timeout(400)
        pg.wait_for_selector("#fac-prev", timeout=25000)


def _descarca_zip(patron, buton):
    with patron.pg.expect_download(timeout=60000) as dl:
        patron.pg.click(buton)
    return zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))


def test_def_c82_detaliul_si_pdf_ul_facturii_primite_arata_valoarea_liniei_din_xml(patron, firma_z):
    """C82 (detaliul și PDF-ul). Pașii: Facturi -> „Facturi primite” -> „Importă XML UBL” (o linie de 3,333 bucăți cu valoarea 100,50 lei —
    prețul unitar 30,1530… —, TVA 21,11) -> contul 371 -> „Validează” -> „Istoric facturi” -> „← luna” -> factura: rândul liniei arată
    valoarea 100,50 RON și „Bază 21%” 100,50 RON (nu 3,333 × 30,15 = 100,49) -> „PDF factură”: aceleași 100,50."""
    import time as _t
    pregateste_firma(patron, firma_z, platitor=True, regim_fiscal="profit")
    tag = "E2EZD-%d" % _t.time()
    doc = _ubl(tag, _cifrele(firma_z), firma_z["nume"], linii=[("3.333", "100.50", 21)], subtotaluri=[("100.50", "21.11", 21)],
               bt109="100.50", bt110="21.11", bt112="121.61")
    fid, _note = _importa_si_valideaza(patron, firma_z, tag, doc)
    _istoric_luna(patron, firma_z)
    pg = patron.pg
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=25000)
    pg.click(".fac-frand-btn[data-id='%s']" % fid)
    pg.wait_for_selector("#fd-pdf", timeout=25000)
    patron.captura("detaliul")
    rand = pg.locator("tr:has(td.fd-td-den)").first.inner_text()
    baza = [t for t in pg.locator(".fd-tot-rand").all_inner_texts() if t.startswith("Bază 21%")]
    # CF art.319 alin.(20) lit.g / BR-DEC-23: valoarea liniei = BT-131 de pe factură
    assert rand.strip().endswith("100,50 RON") and "100,49" not in rand, rand
    assert [re.sub(r"\s+", " ", t) for t in baza] == ["Bază 21% 100,50 RON"], baza
    with pg.expect_response(lambda r: r.url.endswith("/facturi/%s/pdf" % fid), timeout=30000) as rr:
        pg.click("#fd-pdf")
    text, _titlu = _pdf_text(_pdf_ok(patron, rr))
    assert "Bază 21% 100,50" in text and "100,49" not in text, text[:1500]


def test_def_c82_exporturile_saga_si_winmentor_au_valoarea_liniei_din_xml(patron, firma_z):
    """C82 (exporturile). Pașii: factura EMISĂ de firmă venită din XML (3,333 bucăți, BT-131 100,50 lei, TVA 21,11; ruta internă de import —
    date de pornire, vezi antetul) -> Facturi -> „Istoric facturi” -> „← luna” -> „Export SAGA lună”: linia are Valoare 100.50 și TVA 21.11
    (nu 100.49 / 21.10), totalul 121.61 -> „Export WinMentor lună”: Item_1_TVA=21.11 (nu 21.10)."""
    import time as _t
    pregateste_firma(patron, firma_z, platitor=True, regim_fiscal="profit")
    tag = "E2EZX-%d" % _t.time()
    doc = _ubl_emisa(tag, _cifrele(firma_z), firma_z["nume"], linii=[("3.333", "100.50", 21)], subtotaluri=[("100.50", "21.11", 21)],
                     bt109="100.50", bt110="21.11", bt112="121.61")
    fid = _importa_emisa(patron, firma_z, tag, doc)
    assert sql('SELECT directie FROM "%s".facturi WHERE id = %%s' % firma_z["schema"], (fid,))[0][0] == "emisa"
    _istoric_luna(patron, firma_z)
    patron.pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=25000)   # luna încheiată e pe ecran, cu factura în listă
    z = _descarca_zip(patron, "#fac-saga-luna")
    xml = "".join(z.read(n).decode("utf-8") for n in z.namelist() if n.endswith(".xml") and re.sub(r"\W", "", tag) in n)
    patron.captura("export_saga")
    # BR-DEC-23: Valoare = BT-131; TVA-ul liniei 100,50 × 21% = 21,105 -> 21,11
    assert "<Valoare>100.50</Valoare><TVA>21.11</TVA>" in xml and "<Total>121.61</Total>" in xml, xml[:3000]
    z = _descarca_zip(patron, "#fac-winmentor-luna")
    txt = z.read([n for n in z.namelist() if n.lower().startswith("facturi")][0]).decode("cp1250")
    assert "Item_1_TVA=21.11" in txt, txt


def test_def_c82_tva_la_incasare_plata_se_imparte_pe_valorile_liniilor_din_xml(patron, firma_z):
    """C82 (TVA la încasare). Pașii: Date firmă -> „Aplică sistemul TVA la încasare”: Da, de la prima zi a lunii încheiate -> Facturi ->
    „Facturi primite” -> „Importă XML UBL” (1.000 de șuruburi cu BT-131 4,00 lei la 21% — prețul 0,004, ținut 0,00 — + un serviciu de
    100,00 lei la 11%; TVA 0,84 + 11,00; total 115,84) -> contul 371 -> „Validează” (deducerea amânată pe 4428, CF art.297 alin.(3)) ->
    Casă: ridicare de la bancă 200 lei, apoi „Plată furnizor” 115,84 lei cu factura bifată -> „Validează” pe note -> D300 pe luna încheiată:
    rd.24 (R22) 4 / 1 și rd.25 (R23) 100 / 11 (din cantitate × preț: 21% nimic, 11% 104 / 11) -> D394: tvaDed21 1, tvaDed11 11."""
    import time as _t
    s, tid = firma_z["schema"], firma_z["tenant_id"]
    pregateste_firma(patron, firma_z, platitor=True, regim_fiscal="profit")
    _regimul_din_date_firma(patron, firma_z, LUNA.inceput)
    tag = "E2EZI-%d" % _t.time()
    doc = _ubl(tag, _cifrele(firma_z), firma_z["nume"], linii=[("1000", "4.00", 21), ("1", "100.00", 11)],
               subtotaluri=[("4.00", "0.84", 21), ("100.00", "11.00", 11)], bt109="104.00", bt110="11.84", bt112="115.84")
    fid, note = _importa_si_valideaza(patron, firma_z, tag, doc)
    assert sql('SELECT cantitate::text, pret_unitar::text, valoare_neta::text FROM "%s".factura_linii WHERE factura_id = %%s ORDER BY id'
               % s, (fid,))[0] == ("1000.000", "0.00", "4.00")
    # numerarul din care se plătește (ruta formularului Casă)
    _ok(_api(patron, "POST", "/tenants/%d/casa/operatiuni" % tid, {"data": ZI.isoformat(), "categorie": "ridicare_banca", "suma": 200,
                                                                     "document": "CEC Z"}), "ridicarea de numerar")
    pg = patron.pg
    patron.firma(firma_z["nume"])
    pg.click("#fa-casa")
    pg.wait_for_selector("#c-toggle", timeout=20000)
    pg.click("#c-toggle")
    pg.fill("#c-data", ZI.isoformat())
    pg.select_option("#c-cat", "plata_furnizor")
    pg.fill("#c-suma", "115.84")
    pg.fill("#c-cui", "14399840")
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % fid, timeout=20000)
    pg.check("#c-facturi [data-cf='%d']" % fid)
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('115,84')", timeout=20000)
    patron.captura("plata")
    _valideaza_notele_lunii(patron, firma_z)
    xml = _xml_declaratie(patron, firma_z, "d300")
    # CF art.297 alin.(3) + art.282 alin.(8): plata se împarte după valoarea facturată a cotelor (BT-131 × (100 + cotă) / 100)
    assert (_atr(xml, "R22_1"), _atr(xml, "R22_2"), _atr(xml, "R23_1"), _atr(xml, "R23_2")) == ("4", "1", "100", "11"), xml[:3000]
    x394 = _xml_declaratie(patron, firma_z, "d394")
    # OPANAF 2194/2025 (D394) pct.5.2 — tvaDed: TVA-ul dedus la plată, pe cote
    assert (_atr(x394, "tvaDed21"), _atr(x394, "tvaDed11")) == ("1", "11"), x394[:3000]
