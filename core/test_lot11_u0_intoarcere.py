# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 445 (comanda Costin 11.1 pct.21, verbatim): „orice buton «Deschide X» dintr-un refuz întoarce în formularul de
plecare, cu datele intacte.”

Temei: N/A — regulă de interfață (DS cap.9 v2.99, „Fereastra deschisă dintr-un refuz întoarce la formular”).

CE FACE IMPOSIBIL (codul REAL din `navigator.js` și `ecran_destinatie.js`, în Chromium):
  1. formularul în care omul doar a ales (nimic tastat) redesenat de la zero la întoarcere — valorile și refuzul afișat pierdute;
  2. X din fereastra-destinație care aruncă tot drumul (pagina principală), cu formularul;
  3. destinația fără numele formularului de plecare („Înapoi la <formular>”), inclusiv pentru butonul pus automat lângă refuz.
"""
import functools
import http.server
import os
import socketserver
import threading

import pytest

from core.test_emitere_randuri_dinamice import _lanseaza_chromium

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def pg():
    from playwright.sync_api import sync_playwright
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    p = b.new_page()
    p.route("**/notificari**", lambda r, q: r.fulfill(status=200, content_type="application/json", body='{"necitite": 0, "notificari": []}'))
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.add_style_tag(url="/static/stil.css")
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


_PORNIRE = """async () => {
  document.body.innerHTML = '<div id="rad"></div>';
  const { creeazaNavigator } = await import('/static/js/navigator.js');
  const dest = await import('/static/js/ecrane/ecran_destinatie.js');
  // destinația reală ar citi serverul; aici numai fereastra ei, cu ce i-a dat butonul
  dest.ECRANE.produse.deschide = (nav, t, inapoiLa) => nav.deschide('Produse', (c) => { c.innerHTML = '<p id="dest">' + inapoiLa + '</p>'; });
  const nav = creeazaNavigator(document.getElementById('rad'), () => {});
  window.NAV = nav;
  nav.deschide('Emite factură', (c) => {
    c.innerHTML = '<select id="f-cota"><option value="">— alege —</option><option value="21">21%</option></select>' +
      '<input id="f-data" type="date"><div class="msg-eroare" id="f-refuz">Articolul nu are cotă TVA în Produse.</div><span id="f-z"></span>';
  });
  // omul alege (în probă: din cod, deci fără „tastare” — cazul pe care navigatorul îl redesena de la zero)
  document.getElementById('f-cota').value = '21';
  document.getElementById('f-data').value = '2026-10-21';
  document.getElementById('f-refuz').dataset.semn = 'acelasi-element';
  dest.butonSpreEcran(document.getElementById('f-z'), 'produse', nav, 7, { clasa: 'buton-secundar' });
  return true;
}"""


def _stare(pg):
    return pg.evaluate("""() => ({ cota: (document.getElementById('f-cota') || {}).value, data: (document.getElementById('f-data') || {}).value,
        refuz: (document.getElementById('f-refuz') || {dataset: {}}).dataset.semn || null, acasa: !document.querySelector('.fereastra') })""")


def test_inapoi_din_destinatie_readuce_formularul_neatins_cu_alegerile_si_refuzul(pg):
    """1 + 3. MUTAȚIE: `const p = _dePastrat(dinRefuz);` -> `_dePastrat();` -> formularul redesenat, cota „” -> pică.
    MUTAȚIE: `inapoiLa` implicit scos din `butonSpreEcran` -> destinația primește null -> pică."""
    pg.evaluate(_PORNIRE)
    pg.click("[data-ecran-destinatie=produse]")
    assert pg.inner_text("#dest") == "Emite factură"                                   # 3: destinația știe unde întoarce
    assert pg.get_attribute(".fereastra .nav-inapoi", "aria-label") == "Înapoi la Emite factură"
    assert pg.inner_text(".fereastra .nav-inapoi") == "←\nÎnapoi la Emite factură"   # textul întreg al butonului (săgeata, apoi eticheta)
    pg.click(".fereastra .nav-inapoi")
    assert _stare(pg) == {"cota": "21", "data": "2026-10-21", "refuz": "acelasi-element", "acasa": False}   # 445: „cu datele intacte”


def test_x_din_destinatie_intoarce_la_formular_nu_pe_pagina_principala(pg):
    """2. MUTAȚIE: X-ul înapoi la `nav.acasa()` și în fereastra din refuz -> pagina principală, formularul pierdut -> pică."""
    pg.evaluate(_PORNIRE)
    pg.click("[data-ecran-destinatie=produse]")
    pg.click(".fereastra .nav-x")
    assert _stare(pg) == {"cota": "21", "data": "2026-10-21", "refuz": "acelasi-element", "acasa": False}
    pg.click(".fereastra .nav-x")                                                       # X pe formular: pagina principală, ca înainte
    assert _stare(pg)["acasa"] is True


def test_fereastra_deschisa_altfel_nu_se_schimba(pg):
    """Deschiderea obișnuită (nu dintr-un refuz): săgeata „Înapoi” simplă, X duce la pagina principală (DS cap.9, neschimbat)."""
    pg.evaluate(_PORNIRE)
    pg.evaluate("() => window.NAV.deschide('Altceva', (c) => { c.innerHTML = '<p>x</p>'; })")
    assert pg.get_attribute(".fereastra .nav-inapoi", "aria-label") == "Înapoi"
    pg.click(".fereastra .nav-x")
    assert _stare(pg)["acasa"] is True
