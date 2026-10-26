# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), mesajele de refuz — 515 (caseta spune motivul), 625 (aceeași eroare o singură dată; bannerul nu pleacă
singur), 654 (mesajele vechi pleacă la acțiunea următoare), 45 (mesajul scris direct într-o zonă după buton vine în vedere). Codul REAL
din `api.js`, în Chromium.

Comanda 13.1, verbatim: 515 „Caseta roșie spune doar «motivul e mai jos» […] O singură propoziție clară în casetă”; 625 „Aceeași eroare
de trei ori; fereastra plutitoare dispare la schimbarea ecranului și mesajul se pierde. Lângă câmp + rezumat, persistente”; 654 „Mesajele
de eroare vechi («NU s-a salvat», «nu are ce genera») rămân pe ecran după acțiunea următoare, când eroarea e alta sau a dispărut.”

Temei: N/A — reguli de interfață (DS cap.6, v2.104).
"""
import functools
import http.server
import io
import os
import re
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
    p = b.new_page(viewport={"width": 1000, "height": 520})
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.add_style_tag(url="/static/stil.css")
    p.evaluate("async () => { window.A = await import('/static/js/api.js'); }")
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


_FORMULAR = """() => {
  document.body.innerHTML = `<div class="fereastra"><div class="fereastra-corp" style="height:460px;overflow-y:auto">
    <label class="camp"><span class="camp-eticheta">Suma</span><input id="s" class="camp-input" type="number"></label>
    <label class="camp"><span class="camp-eticheta">Cont</span><input id="cont" class="camp-input"></label>
    <p class="randb"><button class="buton-primar" id="salv" data-actiune="POST /x">Salvează</button></p><div id="m"></div>
  </div></div>`;
  window._nr = 0;
  return new Promise((r) => setTimeout(r, 40));
}"""

_APASA = "(id) => { const b = document.getElementById(id); b.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true})); b.click(); }"


def test_def_515_caseta_spune_motivul_o_singura_data(pg):
    """515. MUTAȚIE: ramura „zona e chiar lângă buton” din `refuzSalvare` întoarsă la `li.hidden = true` -> caseta rămâne „NU s-a
    salvat.” fără motiv, motivul dedesubt -> pică."""
    pg.evaluate(_FORMULAR)
    pg.evaluate("""() => document.getElementById('salv').addEventListener('click', () =>
      A.arataMesaj(document.getElementById('m'), 'Contul de ajustare a stocurilor trebuie să fie din grupa 39.', 'eroare'))""")
    pg.evaluate(_APASA, "salv")
    r = pg.evaluate("""() => { const box = document.querySelector('.refuz-salvare');
      return { box: box && box.innerText, motiv: box && (box.querySelector('.refuz-salvare-motiv') || {}).textContent,
               zonaAscunsa: document.getElementById('m').hidden }; }""")
    assert r["box"] and r["box"].startswith("NU s-a salvat.") and r["motiv"] == "Contul de ajustare a stocurilor trebuie să fie din grupa 39.", r
    assert r["zonaAscunsa"] is True, r                                       # același text, o singură dată
    assert "motivul e mai" not in r["box"]
    # corectarea câmpului: refuzul pleacă, zona revine (goală)
    pg.fill("#cont", "397")
    pg.wait_for_timeout(50)
    r2 = pg.evaluate("() => ({ box: !!document.querySelector('.refuz-salvare'), ascunsa: document.getElementById('m').hidden })")
    assert r2 == {"box": False, "ascunsa": False}, r2


def test_def_654_refuzul_vechi_pleaca_la_actiunea_urmatoare(pg):
    """654. MUTAȚIE: `refuzuriVechi(_butonScriere)` scos din ascultătorul clicului -> refuzul celuilalt buton rămâne -> pică."""
    pg.evaluate(_FORMULAR)
    pg.evaluate("""() => {
      document.querySelector('.randb').insertAdjacentHTML('beforeend', ' <button class="buton-secundar" id="gen" data-actiune="POST /y">Generează</button>');
      document.querySelector('.randb').insertAdjacentHTML('afterend', '<div id="m2"></div>');
      document.getElementById('salv').addEventListener('click', () => A.arataMesaj(document.getElementById('m2'), 'D207 nu are ce genera.', 'eroare'));
    }""")
    pg.evaluate(_APASA, "salv")
    assert pg.evaluate("() => !!document.querySelector('.refuz-salvare')")
    pg.evaluate(_APASA, "gen")       # acțiunea următoare (alt buton): refuzul de dinainte nu mai e adevărat
    r = pg.evaluate("() => ({ box: document.querySelectorAll('.refuz-salvare').length, m2: document.getElementById('m2').textContent })")
    assert r == {"box": 0, "m2": ""}, r


def test_def_625_eroarea_de_camp_sta_langa_camp_si_in_rezumat_nu_si_in_zona(pg):
    """625. Refuzul serverului făcut numai din erori de câmp, afișat de ecran și în zona formularului: după `catch` textul stă lângă câmp
    și în „NU s-a salvat.”, nu a treia oară în zonă. MUTAȚIE: blocul [625] din `_campuriAutomat` scos -> zona îl repetă -> pică."""
    pg.evaluate(_FORMULAR)
    r = pg.evaluate("""() => new Promise((rez) => {
      const f0 = window.fetch;
      window.fetch = async () => new Response(JSON.stringify({ detail: { mesaj: 'Suma trebuie să fie mai mare ca 0.',
        erori_campuri: [{ camp: 's', mesaj: 'Suma trebuie să fie mai mare ca 0.' }] } }), { status: 400, headers: { 'Content-Type': 'application/json' } });
      document.getElementById('salv').addEventListener('click', async () => {
        try { await A.api.post('/x', {}); } catch (e) { A.arataMesaj(document.getElementById('m'), e.mesaj, 'eroare'); }
        setTimeout(() => { window.fetch = f0;
          const t = 'Suma trebuie să fie mai mare ca 0.';
          const n = (document.body.innerText.match(new RegExp(t.replace(/[.]/g, '\\\\.'), 'g')) || []).length;
          rez({ n, camp: (document.querySelector('.msg-eroare[data-camp="s"]') || {}).textContent, zona: document.getElementById('m').textContent,
                box: (document.querySelector('.refuz-salvare') || {}).innerText || '' }); }, 60);
      });
      const b = document.getElementById('salv'); b.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true})); b.click();
    })""")
    assert r["camp"] == "Suma trebuie să fie mai mare ca 0." and r["zona"] == "", r
    assert "Suma" in r["box"] and r["n"] == 2, r          # lângă câmp + în rezumat


def test_def_625_bannerul_refuzului_nevazut_nu_pleaca_singur():
    """625. Bannerul `#refuz-nevazut` rămâne până la „Am înțeles”, o scriere reușită pe aceeași rută sau acțiunea următoare.
    MUTAȚIE: `setTimeout(() => { if (d.isConnected) d.remove(); }, 12000)` pus înapoi în `_bannerRefuz` -> pică."""
    api = io.open(os.path.join(_RAD, "static", "js", "api.js"), encoding="utf-8").read()
    corp = re.search(r"function _bannerRefuz\(mesaj, cale\) \{(.*?)\n\}", api, re.S).group(1)
    assert "setTimeout" not in corp and "d.remove()" in corp, corp


def test_def_45_mesajul_scris_direct_sub_buton_vine_in_vedere(pg):
    """45. Butonul la marginea de jos a ferestrei; handlerul scrie mesajul DIRECT într-o zonă fără clasă de mesaj (`textContent`, apoi
    `className = "msg-ok"`): mecanismul unic (`aduInVedere`, observatorul din api.js) îl aduce în vedere. MUTAȚIE: rândul
    `if (t && t.matches(SELECTOR_MESAJ) …) aduInVedere(t);` scos din observatorul lui 45 -> mesajul rămâne sub marginea ferestrei
    (474–510 față de 0–460) -> pică."""
    pg.evaluate(_FORMULAR)
    r = pg.evaluate("""() => new Promise((rez) => {
      const corp = document.querySelector('.fereastra-corp');
      corp.insertAdjacentHTML('afterbegin', '<div style="height:900px">Text lung</div>');
      document.getElementById('m').insertAdjacentHTML('afterend', '<div style="height:900px"></div>');
      const b = document.getElementById('salv');
      corp.scrollTop += b.getBoundingClientRect().bottom - corp.getBoundingClientRect().bottom + 2;
      b.addEventListener('click', () => { const m = document.getElementById('m');
        m.innerHTML = 'Cheia ta (copiaz-o acum: nu se mai afișează):<br><code>ic_' + 'x'.repeat(40) + '</code>'; m.className = 'msg-ok'; });
      b.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true})); b.click();
      setTimeout(() => { const m = document.getElementById('m').getBoundingClientRect(), c = corp.getBoundingClientRect();
        rez({ sus: m.top, jos: m.bottom, cSus: c.top, cJos: c.bottom }); }, 900);
    })""")
    assert r["sus"] >= r["cSus"] - 1 and r["jos"] <= r["cJos"] + 1, r
