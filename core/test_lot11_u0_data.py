# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 441 (comanda Costin 11.1 pct.17, verbatim): „orice câmp de dată opțional se poate goli.”

Temei: N/A — regulă de interfață (DS cap.6 v2.99, „Câmpul de dată opțional se poate goli”).

Inventarul lotului 11 (60 de câmpuri `type="date"`): serverul scrie NULL pentru câmpul opțional trimis gol (`value || null`), dar
câmpul browserului nu are un „golește” la vedere — în Chromium, ștergerea unei părți lasă „--.10.2026” pe ecran.

CE FACE IMPOSIBIL (codul REAL din `api.js` și `stil.css`, în Chromium):
  1. un câmp de dată opțional, oriunde ar fi desenat (și după desenare, prin observator), fără butonul „×” la vedere când are valoare;
  2. butonul care golește fără să anunțe ecranul (`input` + `change`) — ecranul ar trimite valoarea veche;
  3. butonul pe un câmp obligatoriu (`required`, `.oblig` în etichetă, `data-obligatoriu`) sau needitabil;
  4. eroarea câmpului pusă lângă „×” în loc de sub câmp; un rând în plus în formular (înălțimea cutiei = a câmpului).
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
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.add_style_tag(url="/static/stil.css")
    p.evaluate("async () => { window.U0 = await import('/static/js/api.js'); }")
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


_FORMULAR = """() => {
  document.body.innerHTML = `<div class="fereastra-corp">
    <label class="camp"><span class="camp-eticheta">Data încetării</span><input id="d-opt" class="camp-input" type="date" value="2026-10-31"></label>
    <label class="camp"><span class="camp-eticheta">Data emiterii<span class="oblig">*</span></span><input id="d-oblig" class="camp-input" type="date" value="2026-10-21"></label>
    <label class="camp"><span class="camp-eticheta">Data</span><input id="d-req" class="camp-input" type="date" required value="2026-10-21"></label>
    <label class="camp"><span class="camp-eticheta">Data PIF</span><input id="d-ro" class="camp-input" type="date" readonly value="2026-10-21"></label>
    <label class="camp"><span class="camp-eticheta">Scadența</span><input id="d-gol" class="camp-input" type="date"></label>
  </div>`;
  return new Promise((r) => setTimeout(r, 50));
}"""


def test_campul_optional_are_golește_iar_cel_obligatoriu_nu(pg):
    """1 + 3. MUTAȚIE: observatorul din api.js scos -> câmpul desenat după încărcare fără „×” -> pică. MUTAȚIE: `_dataObligatorie`
    -> `false` -> „×” și pe „Data emiterii *” -> pică."""
    pg.evaluate(_FORMULAR)
    r = pg.evaluate("""() => Object.fromEntries(['d-opt', 'd-oblig', 'd-req', 'd-ro', 'd-gol'].map((id) => {
        const b = document.getElementById(id).parentElement.querySelector('.data-goleste');
        return [id, b ? (b.hidden ? 'ascuns' : 'vizibil') : 'fara'];
      }))""")
    assert r == {"d-opt": "vizibil", "d-oblig": "fara", "d-req": "fara", "d-ro": "fara", "d-gol": "ascuns"}, r
    assert pg.get_attribute("#d-opt + .data-goleste", "aria-label") == "Golește data"


def test_golirea_anunta_ecranul_si_valoarea_trimisa_e_goala(pg):
    """2. Ecranul citește `value || null` la salvare și ascultă `change`. MUTAȚIE: `dispatchEvent(new Event("change"…))` scos ->
    ecranul nu află -> pică."""
    pg.evaluate(_FORMULAR)
    r = pg.evaluate("""() => {
      const inp = document.getElementById('d-opt'); const vazut = [];
      inp.addEventListener('change', () => vazut.push(inp.value || null));
      inp.parentElement.querySelector('.data-goleste').click();
      return { valoare: inp.value, trimis: inp.value || null, vazut, buton: inp.parentElement.querySelector('.data-goleste').hidden };
    }""")
    assert r == {"valoare": "", "trimis": None, "vazut": [None], "buton": True}, r   # 441: „se poate goli”


def test_tasta_delete_goleste_tot_campul(pg):
    """1b. Delete pe câmp golește tot câmpul, nu numai ziua. MUTAȚIE: ascultătorul `keydown` scos -> rămâne „--.10.2026” (valoare
    goală, dar ecranul arată luna și anul) -> testul vede că luna a rămas pe ecran -> pică."""
    pg.evaluate(_FORMULAR)
    pg.focus("#d-opt")
    pg.keyboard.press("Delete")
    assert pg.evaluate("() => document.getElementById('d-opt').value") == ""
    assert pg.evaluate("() => document.getElementById('d-opt').validity.badInput") is False   # nimic rămas pe jumătate scris


def test_eroarea_sta_sub_camp_iar_cutia_nu_adauga_un_rand(pg):
    """4. MUTAȚIE: `_ancoraCamp` -> `inp` -> eroarea intră în cutia flex, lângă „×” -> pică."""
    pg.evaluate(_FORMULAR)
    r = pg.evaluate("""() => {
      window.U0.eroareCamp(document, 'd-opt', 'Data încetării e înaintea angajării.');
      const inp = document.getElementById('d-opt'), cutie = inp.parentElement, sp = document.querySelector('.msg-eroare[data-camp="d-opt"]');
      return { dupaCutie: sp.previousElementSibling === cutie, h: [cutie.getBoundingClientRect().height, inp.getBoundingClientRect().height],
               sub: sp.getBoundingClientRect().top >= cutie.getBoundingClientRect().bottom };
    }""")
    assert r["dupaCutie"] and r["sub"], r
    assert r["h"][0] == r["h"][1], r
