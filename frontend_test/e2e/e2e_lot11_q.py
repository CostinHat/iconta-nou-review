# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.1 (verbatim în DECIZII „Comanda 11.1”), subagentul Q — C86: factura EMISĂ venită din XML-ul e-Factura
(importată, deci emisă și transmisă deja în SPV de alt program).

  * detaliul ei nu mai oferă „Trimite în SPV”: în locul butonului stă motivul („a venit din e-Factura: e deja transmisă în SPV”), fără
    „netrimisă în SPV · termen … (depășit)”; ruta `POST /facturi/{id}/trimite-spv` refuză numit (409, `FACTURA_DIN_EFACTURA`);
  * „Stornează” -> „Confirm stornarea”: stornarea are pe linie −100,50 (−BT-131), nota −100,50 / −21,11 (nu 3,333 × 30,15 = −100,49 /
    −21,10), iar detaliul stornării arată −100,50 și oferă „Trimite în SPV” (stornarea e o factură nouă, emisă în aplicație).

DATE DE PORNIRE fără ecran (declarate, regula lui 429): factura EMISĂ venită din XML intră numai prin `POST /tenants/{id}/import-efactura`
(ruta internă de încărcare manuală, fără buton — `main.py`, R70); testul o cheamă din pagină, cu sesiunea contului (`e2e_lot11_z._importa_emisa`).
Clientul: DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md.

Temei: OUG 120/2021 art.4 alin.(3) „Factura electronică se transmite de către emitent în sistemul național privind factura electronică RO
e-Factura.”, alin.(6) „Exemplarul original al facturii electronice se consideră fișierul de tip XML însoțit de sigiliul electronic al
Ministerului Finanțelor.” (a doua încărcare = dublura în SPV, regulă de produs); CF art.330 alin.(1) lit.b) — stornarea cuprinde „valorile cu
semnul minus” ale facturii inițiale. Structură (EN 16931, regulă de validator, nu normă): BR-DEC-23 (BT-131 cu cel mult 2 zecimale)."""
import re
from decimal import Decimal

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _api, _card, pregateste_firma
from e2e_lot11_y2 import _cifrele
from e2e_lot11_z import _importa_emisa, _istoric_luna, _ubl_emisa

ETICHETA = "a venit din e-Factura: e deja transmisă în SPV"   # `efactura_trimitere.ETICHETA_DIN_EFACTURA`


@pytest.fixture()
def firma_q():
    for f in firma_noua():
        yield f


def _deschide(patron, fid):
    pg = patron.pg
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=25000)
    pg.click(".fac-frand-btn[data-id='%s']" % fid)
    pg.wait_for_selector("#fd-pdf", timeout=25000)


def test_def_c86_factura_emisa_din_xml_nu_se_trimite_in_spv_iar_stornarea_ia_valoarea_din_xml(patron, firma_q):
    """C86. Pașii: factura EMISĂ de firmă venită din XML (3,333 bucăți, BT-131 100,50 lei, TVA 21,11, total 121,61; ruta internă de import —
    date de pornire, vezi antetul) -> Facturi -> „Istoric facturi” -> „← luna” -> factura: fără „Trimite în SPV”, cu motivul în locul lui,
    fără „netrimisă în SPV” -> (ruta trimiterii refuză numit) -> „Stornează” -> „Confirm stornarea” -> „Storno creat” -> „Istoric facturi”
    (luna curentă) -> stornarea: linia −100,50 RON, „Trimite în SPV” oferit; nota stornării −100,50 / −21,11."""
    import time as _t
    s, tid = firma_q["schema"], firma_q["tenant_id"]
    pregateste_firma(patron, firma_q, platitor=True, regim_fiscal="profit")
    tag = "E2EQ86-%d" % _t.time()
    doc = _ubl_emisa(tag, _cifrele(firma_q), firma_q["nume"], linii=[("3.333", "100.50", 21)], subtotaluri=[("100.50", "21.11", 21)],
                     bt109="100.50", bt110="21.11", bt112="121.61")
    fid = _importa_emisa(patron, firma_q, tag, doc)
    assert sql('SELECT directie, xml IS NOT NULL FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0] == ("emisa", True)
    _istoric_luna(patron, firma_q)
    _deschide(patron, fid)
    pg = patron.pg
    patron.captura("detaliul_din_xml")
    antet = pg.inner_text(".fd-antet")
    # OUG 120/2021 art.4 alin.(3)/(6): transmisă de emitent — nu se mai oferă a doua trimitere, iar motivul stă în locul butonului
    assert pg.locator("#fd-spv").count() == 0, antet
    assert pg.inner_text("#fd-spv-motiv").strip() == ETICHETA, antet
    assert "netrimis" not in antet and "termen de transmitere" not in antet, antet
    # serverul refuză și el, numit (nu „conectează SPV”)
    r = _api(patron, "POST", "/tenants/%d/facturi/%d/trimite-spv" % (tid, fid), {})
    assert r["status"] == 409, r
    assert "a venit din e-Factura" in str(r["json"]) and "FACTURA_DIN_EFACTURA" in str(r["json"]), r
    assert sql('SELECT count(*) FROM "%s".efactura_trimiteri WHERE factura_id = %%s' % s, (fid,))[0][0] == 0

    # stornarea, din ecran
    pg.click("#fd-storno")
    pg.wait_for_selector("#fd-storno-ok", timeout=20000)
    pg.click("#fd-storno-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-storno-rez') || {}).innerText && "
                         "document.querySelector('#fd-storno-rez').innerText.includes('Storno creat')", timeout=30000)
    patron.captura("storno_creat")
    sid = sql('SELECT id FROM "%s".facturi WHERE storno_din_id = %%s' % s, (fid,))[0][0]
    linii = sql('SELECT cantitate::text, valoare_neta::text FROM "%s".factura_linii WHERE factura_id = %%s' % s, (sid,))
    # CF art.330 alin.(1) lit.b): valorile facturii inițiale cu semnul minus — −BT-131, nu 3,333 × 30,15 = −100,49
    assert linii == [("-3.333", "-100.50")], linii
    note = sql('SELECT l.suma FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id WHERE i.factura_id = %%s'
               % (s, s), (sid,))
    assert sorted(abs(Decimal(str(x[0]))) for x in note) == [Decimal("21.11"), Decimal("100.50")], note

    # detaliul stornării (luna curentă): −100,50 pe linie, iar stornarea (factură nouă a aplicației) pleacă în SPV
    patron.firma(firma_q["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    pg.wait_for_selector("#fac-prev", timeout=25000)
    _deschide(patron, sid)
    patron.captura("detaliul_stornarii")
    rand = pg.locator("tr:has(td.fd-td-den)").first.inner_text()
    assert re.search(r"[-−]\s?100,50 RON\s*$", rand.strip()) and "100,49" not in rand, rand
    assert pg.locator("#fd-spv").count() == 1 and pg.locator("#fd-spv-motiv").count() == 0
