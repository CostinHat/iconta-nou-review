# -*- coding: utf-8 -*-
"""GARD ÎN BROWSER — fereastra firmei, grupată (comanda Costin 05.10.2026 pct.11): „cele peste 20 de carduri se grupează sub câteva
titluri … Fără arbore în fereastra firmei. Un titlu fără niciun card vizibil (drepturi, regim SRL/PFA) nu apare. O singură sursă
pentru grupuri.” Structura sursei o păzește verificatorul (`GRUP_FIRMA`); aici, comportamentul — modulul real, în Chromium.
MUTAȚIE: filtrul grupurilor goale scos din `grupeazaCarduri` -> titlul gol apare -> pică.
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
    p.route("**/tenants/**", lambda r, q: r.fulfill(status=200, content_type="application/json", body="{}"))
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


def test_grupul_fara_card_vizibil_nu_apare(pg):
    r = pg.evaluate("""async () => {
      const m = await import('/static/js/ecrane/firme.js');
      return m.grupeazaCarduri([{ cheie: 'a', grup: 'registre' }, { cheie: 'b', grup: 'zilnic' }, { cheie: 'c', grup: 'zilnic' }])
              .map(([g, t, c]) => [g, c.map((x) => x.cheie)]);
    }""")
    assert r == [["zilnic", ["b", "c"]], ["registre", ["a"]]], r   # ordinea din GRUPURI_FIRMA; fără „raportari/speciale/firma”


@pytest.mark.parametrize("regim", ["dubla", "simpla"])
def test_fereastra_firmei_are_titluri_cu_carduri_si_niciun_arbore(pg, regim):
    r = pg.evaluate("""async (regim) => {
      const m = await import('/static/js/ecrane/firme.js');
      document.body.innerHTML = '';
      const nav = { setFirmaInLucru() {}, deschide(titlu, f) { const d = document.createElement('div'); d.id = 'fereastra'; document.body.appendChild(d); f(d); } };
      m.deschideFirma({ id: 1, nume: 'Firma', cui: '1', regim_contabil: regim }, nav);
      await new Promise((ok) => setTimeout(ok, 300));
      const g = [...document.querySelectorAll('#fereastra .firme-grup')];
      return { titluri: g.map((x) => x.querySelector('h3').innerText.trim()),
               carduri: g.map((x) => x.querySelectorAll('.firme-optiune').length),
               imbricate: document.querySelectorAll('.firme-grup .firme-grup').length,
               inAfaraGrupurilor: [...document.querySelectorAll('#fereastra .firme-optiune')].filter((b) => !b.closest('.firme-grup')).length };
    }""", regim)
    assert r["titluri"] == ["Zilnic", "Registre", "Raportări și declarații", "Operațiuni speciale", "Firma"], r
    assert all(n > 0 for n in r["carduri"]) and r["imbricate"] == 0 and r["inAfaraGrupurilor"] == 0, r
    assert sum(r["carduri"]) == (31 if regim == "dubla" else 22), r   # 32 de carduri: 21 „ambele”, 10 „dubla”, 1 „simpla”
