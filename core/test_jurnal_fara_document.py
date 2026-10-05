# -*- coding: utf-8 -*-
"""GARD ÎN BROWSER — Registrul jurnal: o ciornă fără document justificativ se vede ÎNAINTE de validare, iar „Validează” pe ea
cere confirmare (comanda Costin 05.10.2026 pct.6: „validatorul trebuie să vadă lipsa înainte să apese”).

Pe COMPORTAMENT, nu pe sursă (`core/test_garzi_pe_text.py`): ecranul real (`firme.ecranJurnal`) montat în Chromium, cu
rutele simulate; se numără cererile de validare trimise. MUTAȚIE: confirmarea scoasă din ascultătorul „Validează” -> cererea
pleacă la primul clic -> pică.
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
NOTE = [
    {"id": 7, "nr_curent": 1, "data": "2026-10-05", "numar": None, "descriere": "Comision bancar", "sursa": "banca",
     "status": "ciorna", "factura_id": None, "document_ref": None, "document": None,
     "linii": [{"debit": "627", "credit": "5121", "suma": 12.5, "centru_cost_id": None, "centru_nume": None}]},
    {"id": 8, "nr_curent": 2, "data": "2026-10-05", "numar": None, "descriere": "Încasare", "sursa": "banca",
     "status": "ciorna", "factura_id": 3, "document_ref": "Extras bancar x.csv din 05.10.2026", "document": "Extras bancar x.csv din 05.10.2026",
     "linii": [{"debit": "5121", "credit": "4111", "suma": 121.0, "centru_cost_id": None, "centru_nume": None}]},
]

MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  await m.ecranJurnal(document.getElementById('mount'), { deschide(){}, inapoi(){}, setInapoi(){} }, { id: 1, nume: "Firma" });
  return true;
}"""


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    validari = []

    def h(route, request):
        url = request.url.split("?")[0]
        if url.endswith("/valideaza"):
            validari.append(url)
            return route.fulfill(status=200, content_type="application/json", body='{"ok": true}')
        corp = {"note": NOTE, "total_debit": 133.5, "total_credit": 133.5, "note_fara_document": 1} if url.endswith("/jurnal") \
            else {"centre": []} if url.endswith("/centre-cost") else {"blocate": []}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))

    pg = br.new_page()
    pg.route("**/tenants/**", h)
    pg.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
    pg.wait_for_selector('[data-val="7"]', timeout=15000)
    try:
        yield pg, validari
    finally:
        br.close(); pw.stop(); srv.shutdown()


def test_lipsa_documentului_se_vede_pe_rand_inainte_de_validare(pagina):
    pg, _ = pagina
    # exact o casetă de avertizare, pe rândul notei fără document (nota 8 are extrasul)
    assert pg.eval_on_selector_all(".jn-fara-doc", "e => e.length") == 1
    assert pg.eval_on_selector('[data-val="7"]', "b => !!b.closest('.pf-frand').querySelector('.jn-fara-doc')")
    assert not pg.eval_on_selector('[data-val="8"]', "b => !!b.closest('.pf-frand').querySelector('.jn-fara-doc')")


def test_validarea_fara_document_cere_confirmare_iar_cu_document_nu(pagina):
    pg, validari = pagina
    pg.click('[data-val="7"]')
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=5000)
    assert validari == [], "validarea a plecat fără confirmare"
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => true")
    pg.wait_for_timeout(300)
    assert len(validari) == 1 and validari[0].endswith("/jurnal/7/valideaza")
    pg.wait_for_selector('[data-val="8"]', timeout=5000)
    pg.click('[data-val="8"]')
    pg.wait_for_timeout(300)
    assert len(validari) == 2 and validari[1].endswith("/jurnal/8/valideaza"), "nota cu document nu cere confirmare"
