# -*- coding: utf-8 -*-
"""GARD ÎN BROWSER — ecranul Stocuri (comanda Costin 05.10.2026 pct.10): „ecranul se deschide cu situația stocului (articol, UM,
cantitate, CMP, valoare), formularele (NIR, mișcări, coduri, nivel minim) stau sub ea, la cerere; Rețete apare doar la firmele
HoReCa.” Ecranul real (`firme.ecranStocuri`) montat în Chromium, rutele simulate.
MUTAȚII: `hidden` scos de pe `#cv-zona` -> formularele deschise de la început -> pică; condiția `reteteVizibile` scoasă -> Rețete
la o firmă non-HoReCa -> pică; situația scoasă -> pică.
"""
import functools
import http.server
import json
import os
import socketserver
import threading

import pytest

from core.test_emitere_randuri_dinamice import _lanseaza_chromium

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTS = [{"id": 1, "denumire": "Pâine albă", "um": "buc", "stoc": "110.000", "valoare": "220.00", "cmp": "2.0000"},
        {"id": 2, "denumire": "Făină", "um": "kg", "stoc": "12.500", "valoare": "37.50", "cmp": "3.0000"}]
MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  await m.ecranStocuri(document.getElementById('mount'), { deschide(){}, inapoi(){}, inapoiPas(){} }, { id: 1 });
  return true;
}"""


def _pagina(br, port, horeca):
    def h(route, request):
        url = request.url.split("?")[0]
        if url.endswith("/stocuri/articole"):
            corp = {"articole": ARTS, "retete_vizibile": horeca}
        elif url.endswith("/stocuri/nir"):
            corp = {"nir": []}
        elif url.endswith("/stocuri/locatii"):
            corp = {"locatii": []}
        elif url.endswith("/retete"):
            corp = {"retete": []}
        else:
            corp = {}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))
    pg = br.new_page()
    pg.route("**/tenants/**", h)
    pg.goto("http://127.0.0.1:%d/static/" % port)
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
    pg.wait_for_selector("#s-situatie-tabel", timeout=15000)
    pg.wait_for_selector("#cv-zona #cv-art", state="attached", timeout=15000)
    return pg


@pytest.fixture(scope="module")
def br():
    from playwright.sync_api import sync_playwright
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    try:
        yield b, srv.server_address[1]
    finally:
        b.close(); pw.stop(); srv.shutdown()


def test_situatia_stocului_e_prima_si_formularele_la_cerere(br):
    b, port = br
    pg = _pagina(b, port, horeca=False)
    randuri = pg.eval_on_selector_all("#s-situatie-tabel tbody tr", "e => e.map(r => [...r.cells].map(c => c.innerText.trim()))")
    assert randuri == [["Pâine albă", "buc", "110", "2,00", "220,00"], ["Făină", "kg", "12,5", "3,00", "37,50"]]
    assert pg.eval_on_selector("#s-situatie-tabel tfoot", "e => e.innerText.replace(/\\s+/g, ' ').trim()") == "Total valoare stoc 257,50"
    # situația stă DEASUPRA formularelor; formularele sunt închise la deschidere
    assert pg.evaluate("() => !!(document.querySelector('#s-situatie').compareDocumentPosition(document.querySelector('#sn-toggle')) & Node.DOCUMENT_POSITION_FOLLOWING)")
    assert pg.eval_on_selector("#cv-zona", "e => e.hidden") and pg.eval_on_selector("#sn-zona", "e => e.hidden")
    pg.click("#cv-toggle")
    assert not pg.eval_on_selector("#cv-zona", "e => e.hidden")
    assert pg.query_selector("#rt-lista") is None, "Rețete la o firmă care nu e HoReCa"
    pg.close()


def test_retetele_apar_la_firma_horeca(br):
    b, port = br
    pg = _pagina(b, port, horeca=True)
    assert pg.query_selector("#rt-lista") is not None
    pg.close()
