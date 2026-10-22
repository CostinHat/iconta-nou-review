# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 422 (clasa 286) — contorul „De validat” și clopoțelul urmează acțiunile, fără reîncărcare.

Decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”: „422: contorul «De validat» și clopoțelul nu se actualizează după acțiuni
(clasa 286); se repară.” Comanda 11.1 pct.1 o cere aplicată.

Temei: N/A — comportament de interfață (DS cap.6; mecanismul 286 din `api.js`).

CAUZA: insigna clopoțelului (`navigator.js::_clopotActualizeazaBadge`) se citea o dată, la construirea barei, și la deschiderea panoului;
semnalul `iconta:schimbare` (286: orice scriere reușită prin `api.*`) îl ascultau numai pagina principală și cardurile de început. Ce schimba
un coleg (o notă trimisă la validare, o validare) nu ajungea deloc, nici la clopoțel, nici la contoarele paginii principale.
CE FACE IMPOSIBIL (codul REAL al navigatorului și al lui api.js, în Chromium; serverul e simulat cu `page.route`):
  1. o scriere reușită (validare, respingere, ciornă, ștergere, trimitere) fără ca insigna să se recitească;
  2. o schimbare a altcuiva (contorul de pe server s-a mișcat) fără semnalul mai departe către contoarele paginii principale;
  3. semnalul fără căile scrise (8c le folosește: „Regenerează amortizarea” se reactivează numai după o scriere în mijloacele fixe);
  4. o scriere care ocolește `api.js` (fetch direct cu metodă de scriere) — garda statică de mai jos.
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
    p = b.new_page()
    stare = {"necitite": 3, "cereri": 0}

    def _contor(route, _req):
        stare["cereri"] += 1
        route.fulfill(status=200, content_type="application/json", body='{"ok": true, "necitite": %d}' % stare["necitite"])
    p.route("**/notificari/contor", _contor)
    p.route("**/proba-validare**", lambda r, q: r.fulfill(status=200, content_type="application/json", body='{"ok": true}'))
    p.route("**/tenants/7/mijloace-fixe**", lambda r, q: r.fulfill(status=200, content_type="application/json", body='{"ok": true}'))
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.stare = stare
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


_BARA = """
  document.body.innerHTML = '<div id="bara"><button id="nav-clopot"><span id="nav-clopot-badge"></span></button></div>';
  const { urmaresteClopotul } = await import('/static/js/navigator.js');
  const reia = urmaresteClopotul(document.getElementById('bara'));
  await reia(false);
  const insigna = () => document.getElementById('nav-clopot-badge').textContent;
"""


def test_insigna_se_reciteste_dupa_o_scriere_reusita(pg):
    """1. Validarea (o scriere prin `api.post`) rezolvă notificarea „de validat”: insigna coboară de la 3 la 2 fără reîncărcare.
    MUTAȚIE: listenerul `iconta:schimbare` scos din `urmaresteClopotul` -> insigna rămâne „3” -> pică."""
    pg.stare["necitite"] = 3
    r = pg.evaluate("async () => {" + _BARA + " return insigna(); }")
    assert r == "3", r
    pg.stare["necitite"] = 2   # serverul: validarea a rezolvat notificarea
    r = pg.evaluate("""async () => {
      const { api } = await import('/static/js/api.js');
      await api.post('/proba-validare', {});
      await new Promise((ok) => setTimeout(ok, 700));   // semnalul pleacă după 300 ms de liniște
      return document.getElementById('nav-clopot-badge').textContent;
    }""")
    assert r == "2", r   # decizia 10.3: „clopoțelul [...] se actualizează după acțiuni”


def test_schimbarea_altcuiva_ajunge_la_contoarele_paginii_principale(pg):
    """2. Un coleg trimite o notă la validare: contorul de pe server crește; la recitirea periodică (`reia(true)`: ceasul sau întoarcerea
    în filă) insigna o arată și semnalul pleacă mai departe (`din: "notificari"`), ca „De validat” de pe pagina principală (cabinet.js)
    să se recitească. Contorul neschimbat: niciun semnal. MUTAȚIE: `dispatchEvent` scos din ramura `dinAfara && schimbat` -> pică."""
    pg.stare["necitite"] = 6
    r = pg.evaluate("async () => {" + _BARA + """
      window.__semnale = [];
      window.addEventListener('iconta:schimbare', (e) => window.__semnale.push(e.detail));
      window.__reia = reia;
      return insigna();
    }""")
    assert r == "6", r
    pg.stare["necitite"] = 7   # alt utilizator: încă o notă trimisă la validare
    r = pg.evaluate("""async () => {
      await window.__reia(true);
      return { insigna: document.getElementById('nav-clopot-badge').textContent, semnale: window.__semnale };
    }""")
    assert r["insigna"] == "7", r
    assert r["semnale"] == [{"cai": [], "din": "notificari"}], r   # semnalul către contoarele paginii principale (cabinet.js, 286)
    r = pg.evaluate("""async () => { window.__semnale = []; await window.__reia(true); return window.__semnale; }""")
    assert r == [], r   # fără recitiri degeaba ale paginii principale


def test_semnalul_poarta_caile_scrise(pg):
    """3. `iconta:schimbare` spune CE s-a scris (fără parametrii cererii). MUTAȚIE: `detail: { cai }` scos din `_anuntaSchimbarea` -> pică."""
    r = pg.evaluate("""async () => {
      const { api } = await import('/static/js/api.js');
      const vazute = [];
      const l = (e) => vazute.push(e.detail);
      window.addEventListener('iconta:schimbare', l);
      await api.post('/tenants/7/mijloace-fixe?x=1', {});
      await api.post('/proba-validare', {});
      await new Promise((ok) => setTimeout(ok, 700));
      window.removeEventListener('iconta:schimbare', l);
      return vazute;
    }""")
    assert r == [{"cai": ["/tenants/7/mijloace-fixe", "/proba-validare"]}], r   # o rafală = un semnal, cu ambele căi


def test_coaja_porneste_urmarirea_si_intervalul_e_declarat():
    """Legătura: `_clopotInit` (bara reală) cheamă `urmaresteClopotul`, iar ceasul există. MUTAȚIE: apelul scos din `_clopotInit` -> pică."""
    from core.arbore_js import apeluri, arbore_js, functia
    nav = io.open(os.path.join(_RAD, "static/js/navigator.js"), encoding="utf-8").read()
    # apelurile ca noduri acorn în corpul funcțiilor (callee + argumente), nu șiruri în sursă (core/test_garzi_pe_text.py)
    arb, cod = arbore_js(os.path.join(_RAD, "static/js/navigator.js"))
    assert apeluri(functia(arb, "_clopotInit"), cod, "urmaresteClopotul") == [("bara",)]
    assert re.search(r"export const CLOPOT_INTERVAL_MS = \d+;", nav)
    assert len(apeluri(functia(arb, "urmaresteClopotul"), cod, "setInterval")) == 1


#: scrierile directe cu `fetch` admise, fiecare cu motivul: nu scriu în baza firmei (previzualizări, telemetrie publică, autentificare)
FETCH_SCRIERE_ADMIS = {
    ("migrare.js", "/incarca"): "previzualizarea unui fișier încărcat (rutele `…/incarca` nu salvează nimic)",
    ("login.js", "/api/eveniment-public"): "telemetria paginii publice, înainte de autentificare",
}


def scrieri_care_ocolesc_api(d):
    """[(fișier:linie cale)] — `fetch` direct cu metodă de scriere în ecranele din `d`, în afara listei admise."""
    rele = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".js"):
            continue
        t = io.open(os.path.join(d, f), encoding="utf-8").read()
        for m in re.finditer(r"\bfetch\(\s*([`'\"])(.*?)\1\s*,\s*\{(.{0,300}?)\}", t, re.S):
            if not re.search(r"method:\s*[\"'](POST|PUT|PATCH|DELETE)", m.group(3)):
                continue
            cale = m.group(2)
            if any(f == ff and frag in cale for (ff, frag) in FETCH_SCRIERE_ADMIS):
                continue
            rele.append("%s:%d %s" % (f, t[:m.start()].count("\n") + 1, cale))
    return rele


def test_nicio_scriere_din_ecrane_nu_ocoleste_api_js():
    """4. O scriere cu `fetch` direct nu anunță schimbarea (contoarele, clopoțelul rămân vechi) și ocolește refuzul comun. Instanța găsită:
    importul AMEF din Raport Z (firme.js). MUTAȚIE (pe o copie a directorului): `fetch(`/tenants/${t.id}/horeca/import-amef`, { method:
    "POST", … })` pus la loc -> lista nevidă -> pică."""
    d = os.path.join(_RAD, "static/js/ecrane")
    rele = scrieri_care_ocolesc_api(d)
    assert not rele, "scrieri care ocolesc api.js (contoarele și clopoțelul nu le văd — 422): %s" % rele
    assert len([1 for f in os.listdir(d) if f.endswith(".js")]) > 30   # ANTI-VACUU
