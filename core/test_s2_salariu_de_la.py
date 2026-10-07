# -*- coding: utf-8 -*-
"""GARD S2 (retest Costin 07.10 seara, pct.2) — „La «Salariu», câmpul «de la» e precompletat cu data de azi (07.10.2026), deși se
lucrează pe 09/2026. Dacă rămâne precompletat, implicit trebuie să fie prima zi a lunii lucrate.”

Montează modulul real (`firme.js` -> `ecranSalariati`) în chromium headless, cu ruta statului interceptată, mută statul o lună
înapoi și deschide „Salariu”: câmpul „de la” trebuie să fie prima zi a lunii AFIȘATE. Pe DOM, nu pe sursă.
MUTAȚIE: `value="${azi}"` pus înapoi -> câmpul arată data de azi -> pică.
"""
import datetime
import functools
import http.server
import json
import os
import socketserver
import threading
from urllib.parse import urlparse

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  await m.ecranSalariati(document.getElementById('mount'), { inapoiPas(){}, deschide(){}, mergi(){} }, { id: 1 });
  return true;
}"""


def _handler(route, request):
    if urlparse(request.url).path == "/tenants/1/stat-plata":
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"stat": [
            {"id": 7, "nume": "POP ION", "salariu_baza": 5000, "brut": 5000, "net": 2925, "elemente": [], "compozitie": []}]}))
        return
    route.fulfill(status=200, content_type="application/json", body="{}")


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD)

    class _Srv(socketserver.TCPServer):
        allow_reuse_address = True

    srv = _Srv(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = pw.chromium.launch()
    pg = br.new_page()
    pg.route("**/tenants/**", _handler)
    pg.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield pg
    finally:
        br.close(); pw.stop(); srv.shutdown()


def test_salariul_de_la_porneste_cu_prima_zi_a_lunii_afisate(pagina):
    pg = pagina
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
    pg.wait_for_selector("[data-salariu]")
    pg.click("#sp-prev"); pg.wait_for_selector("[data-salariu]")
    pg.click("[data-salariu]"); pg.wait_for_selector("#salariu-data")
    azi = datetime.date.today()
    prima_lunii_trecute = (azi.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
    assert pg.input_value("#salariu-data") == prima_lunii_trecute.isoformat()   # luna lucrată (afișată), ziua 1
