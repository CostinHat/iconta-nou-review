# -*- coding: utf-8 -*-
"""GARD ÎN BROWSER — blocarea butonului în timpul unei scrieri nu-i distruge conținutul (găsit 08.10.2026, la proba lotului
„Deciziile 08.10”: după „Contează” pe o factură, rândul rămânea „Contează” — și în codul vechi).

CAUZA, măsurată în DOM: `api.js::blocheazaButon` punea „Se lucrează...” prin `textContent` pe butonul apăsat și îl restaura tot
prin `textContent`. Un buton cu ELEMENTE în el (rândul-buton al listei de facturi, cu „Contează” în el; cardurile; iconițele) ieșea
aplatizat la text, iar elementul acțiunii — detașat; ecranul nu-și mai putea pune rezultatul în locul lui.

CE FACE IMPOSIBIL: ca o scriere pornită dintr-un buton cu elemente să-i schimbe structura (copiii rămân aceiași noduri, legați);
butonul de text simplu își păstrează comportamentul („Se lucrează...”, apoi textul lui). Modulul real, în Chromium.
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
    p.route("**/proba-scriere**", lambda r, q: r.fulfill(status=200, content_type="application/json", body='{"ok": true}'))
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


def test_butonul_cu_elemente_isi_pastreaza_structura_si_actiunea_ramane_legata(pg):
    """MUTAȚIE: ramura `b.firstElementChild` scoasă din `blocheazaButon` -> copiii dispar, span-ul e detașat -> pică."""
    r = pg.evaluate("""async () => {
      const { api } = await import('/static/js/api.js');
      document.body.innerHTML = '<button id="rand"><div class="t">FP1 · DANTE</div><span id="act">Contează</span></button>';
      const span = document.getElementById('act');
      let inTimp = null;
      span.addEventListener('click', async () => {
        const p = api.post('/proba-scriere', {});
        inTimp = { copii: document.getElementById('rand').children.length, dezactivat: document.getElementById('rand').disabled };
        await p;
      });
      span.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));   // ca un clic real (api.js ține minte butonul la pointerdown)
      span.click();
      await new Promise((ok) => setTimeout(ok, 400));
      const rand = document.getElementById('rand');
      return { inTimp, copiiDupa: rand.children.length, spanLegat: span.isConnected, dezactivatDupa: rand.disabled,
               ocupat: rand.getAttribute('aria-busy') };
    }""")
    assert r == {"inTimp": {"copii": 2, "dezactivat": True}, "copiiDupa": 2, "spanLegat": True, "dezactivatDupa": False,
                 "ocupat": None}, r


def test_butonul_de_text_simplu_arata_ca_lucreaza_si_isi_reia_textul(pg):
    """Comportamentul vechi, pe forma lui legitimă. MUTAȚIE: restaurarea textului scoasă -> rămâne „Se lucrează...” -> pică."""
    r = pg.evaluate("""async () => {
      const { api } = await import('/static/js/api.js');
      document.body.innerHTML = '<button id="b">Validează</button>';
      const b = document.getElementById('b');
      let inTimp = null;
      b.addEventListener('click', async () => { const p = api.post('/proba-scriere', {}); inTimp = b.textContent; await p; });
      b.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
      b.click();
      await new Promise((ok) => setTimeout(ok, 400));
      return { inTimp, dupa: b.textContent, dezactivat: b.disabled };
    }""")
    assert r == {"inTimp": "Se lucrează...", "dupa": "Validează", "dezactivat": False}, r
