# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 458 — comanda Costin 11.3 pct.6, partea (1)] „în Erori — echipa: text suprapus peste nume”.

Fereastra „Erori — echipa” desenată de `asistenti.js` + `navigator.js` + `stil.css` REALE, în Chromium, la 1280×720, 1366×768 și pe
telefon (390×844), cu datele de pe cabinetul de test (forma răspunsului `/asistenti/echipa/erori`; backendul simulat — aici se măsoară
așezarea, cifrele le probează `core/test_lot11_a458_erori_echipa.py`).

CAUZA (măsurată aici): eticheta bulinei („probleme”) purta clasa `asi-sem-txt`, pe care selectorul GLOBAL al bulinei din
STANDARD_SEMAFOR (`span[class*="sem-"]`, DS cap.8) o făcea cutie rotundă de 16×16 px (`!important`): textul ieșea din cutie peste
numele omului. A doua: în rândul motivului, insignele și numărul („sistematic nou 3×”) se rupeau pe două rânduri, iar insignele se
suprapuneau. Reparația: eticheta = `.tip-desc` (clasa globală de text), coada rândului nu se rupe.

Gărzile: (a) în fereastră, niciun text nu se suprapune peste alt text (dreptunghiurile glifelor, nu ale cutiilor), la cele trei
lățimi; (b) niciun element prins de selectorul global al bulinei nu are text; (c) static, pe tot `static/`: nicio clasă de text nu
cade sub selectorul bulinei (`sem-` / `pct` în numele clasei = numai bulinele din STANDARD_SEMAFOR).

Temei: N/A — regulă de UI (DS cap.8 „Bulină LED 16px cu gradient + etichetă text”).
"""
import functools
import glob
import http.server
import io
import json
import os
import re
import socketserver
import threading
import urllib.parse

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECRANE = [(1280, 720), (1366, 768), (390, 844)]

#: forma răspunsului de pe cabinetul de test (producție, numai citire, 22.10.2026, după reparația (2)+(3)): nume, motive lungi
ERORI = {"ok": True, "zile": 30, "asistenti": [
    {"id": 1, "nume": "Ana Asistent", "respinse": 5, "evaluate": 15, "rata": 33, "culoare": "rosu", "tipare": [
        {"motiv": "Descrierea conține referințe interne („decizia Costin 08.10, pct.4”). Contabilitatea e corectă; refă doar descrierea "
                  "în limbaj de contabil și retrimite.", "nr": 2, "tip": "sistematic", "nou": True},
        {"motiv": "Lipsește prima de performanță la Popescu", "nr": 1, "tip": "accident", "nou": True},
        {"motiv": "NIR făcut cu logica veche (preț de raft); se reface la cost", "nr": 1, "tip": "accident", "nou": True},
        {"motiv": "verifică data notei", "nr": 1, "tip": "accident", "nou": True}]},
    {"id": 2, "nume": "Contabil Sesiunea B", "respinse": 1, "evaluate": 1, "rata": 100, "culoare": "galben", "tipare": [
        {"motiv": "Depășită, lipsește F1A5 (servicii UE, rd.3/3.1)", "nr": 1, "tip": "accident", "nou": True}]}]}
SEMAFOR = {"ok": True, "culoare": "rosu", "counts": {"rosu": 1, "galben": 1, "verde": 0}, "zile": 30, "asistenti": []}

PAGINA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="/static/stil.css"></head><body><div id="app"></div><script type="module">
sessionStorage.setItem("iconta_user", JSON.stringify({rol: "admin_firma", nume: "Probă", bun_venit_vazut: true}));
const m = await import("/static/js/navigator.js"); const a = await import("/static/js/ecrane/asistenti.js");
window._nav = m.creeazaNavigator(document.getElementById("app"), () => {}); window._a = a; window._gata = true;
</script></body></html>"""

#: selectorul global al bulinei, citit din STANDARD_SEMAFOR (nu copiat): dacă se schimbă acolo, măsurătoarea îl urmează
def _selector_bulina():
    css = io.open(os.path.join(RAD, "static", "stil.css"), encoding="utf-8").read()
    bloc = css[css.index("[STANDARD_SEMAFOR]"):css.index("sfarsit STANDARD_SEMAFOR")]
    return re.search(r"\*/\s*([^{]+)\{", bloc).group(1).strip()


MASOARA = """(sel) => {
  const f = [...document.querySelectorAll('.fereastra')].pop();
  const noduri = [], w = document.createTreeWalker(f, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    if (!n.textContent.trim() || !n.parentElement.getClientRects().length) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    noduri.push({t: n.textContent.trim().slice(0, 40), rr: [...r.getClientRects()].filter((x) => x.width > 0.5)});
  }
  const supr = [];
  for (let i = 0; i < noduri.length; i++) for (let j = i + 1; j < noduri.length; j++)
    for (const a of noduri[i].rr) for (const b of noduri[j].rr) {
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 1 && oy > 1) supr.push([noduri[i].t, noduri[j].t, Math.round(ox), Math.round(oy)]);
    }
  const bulineCuText = [...f.querySelectorAll(sel)].filter((e) => e.textContent.trim()).map((e) => e.className + ': ' + e.textContent);
  // coada rândului (insignele + numărul): câte rânduri ocupă = câte „top”-uri distincte au copiii ei (cutia flex are mereu una)
  // (insignele și <b> au alt „top” pe același rând, din padding: un rând nou = un salt mai mare decât jumătate de rând)
  const cozi = [...f.querySelectorAll('.asi-cal-motiv > span:last-child')].map((e) => {
    const t = [...e.children].map((c) => c.getBoundingClientRect().top).sort((x, y) => x - y);
    return 1 + t.slice(1).filter((v, i) => v - t[i] > 8).length; });
  const corp = [...document.querySelectorAll('.fereastra-corp')].pop();
  return {supr, bulineCuText, cozi_rupte: cozi.filter((n) => n > 1).length, lateral: corp.scrollWidth > corp.clientWidth + 1,
          pagina_lat: document.documentElement.scrollWidth > innerWidth + 1, nume: [...f.querySelectorAll(".val-card > div:first-child > b")].map((b) => b.innerText)};
}"""


class _Tacut(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_Tacut, directory=RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    try:
        yield b, srv.server_address[1]
    finally:
        b.close()
        pw.stop()
        srv.shutdown()


def _deschide(browser, lat, inalt):
    b, port = browser
    pg = b.new_page(viewport={"width": lat, "height": inalt})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        cale = urllib.parse.urlsplit(route.request.url).path
        if cale.startswith("/static/"):
            return route.continue_()
        corp = {"/asistenti": {"actori": [], "sumar": {}}, "/asistenti/echipa/semafor": SEMAFOR, "/asistenti/echipa/erori": ERORI}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp.get(cale, {})))
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/asistenti", "/tenants", "/auth/", "/notificari", "/versiune"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    pg.evaluate("() => window._nav.deschide('Asistenți', (c) => window._a.randeazaAsistenti(c, window._nav))")
    pg.wait_for_selector("#asi-vezi-erori", timeout=10000)
    pg.click("#asi-vezi-erori")
    pg.wait_for_selector(".val-card .asi-cal-motiv", timeout=10000)
    pg.wait_for_timeout(200)
    assert not erori, erori
    return pg


@pytest.mark.parametrize("lat,inalt", ECRANE)
def test_def_458_erori_echipa_fara_text_suprapus(browser, lat, inalt):
    """ROȘU înainte: „probleme” (eticheta bulinei, cutie de 16 px) peste „Ana Asistent” / „Contabil Sesiunea B” la toate cele trei
    lățimi; pe telefon „3×” pe rândul lui și insignele „sistematic” / „nou” suprapuse. MUTAȚIA: eticheta înapoi pe `asi-sem-txt`
    -> pică (a), (b); coada rândului fără `white-space:nowrap` -> pică pe telefon."""
    pg = _deschide(browser, lat, inalt)
    try:
        o = pg.evaluate(MASOARA, _selector_bulina())
    finally:
        pg.close()
    assert o["nume"] == ["Ana Asistent", "Contabil Sesiunea B"], o["nume"]
    assert not o["supr"], (lat, o["supr"])                              # „text suprapus peste nume”
    assert not o["bulineCuText"], (lat, o["bulineCuText"])              # bulina e bulină, eticheta e text (DS cap.8)
    assert o["cozi_rupte"] == 0, (lat, o["cozi_rupte"])                 # insignele și numărul rândului, pe un rând
    assert not o["lateral"] and not o["pagina_lat"], lat


def test_nicio_clasa_de_text_sub_selectorul_bulinei():
    """GARDA de clasă (static, tot `static/`): selectorul global al bulinei prinde ORICE `span` cu `sem-` sau `pct` în clasă; o clasă de
    text cu un astfel de nume devine cutie de 16 px și textul iese peste vecini (cauza 458). Numele permise = bulinele definite în
    STANDARD_SEMAFOR (plus `rap-badge-pct`, exclusă acolo prin `:not`). MUTAȚIA: o clasă `asi-sem-txt` pe un `span` cu text -> pică."""
    css = io.open(os.path.join(RAD, "static", "stil.css"), encoding="utf-8").read()
    bloc = css[css.index("[STANDARD_SEMAFOR]"):css.index("sfarsit STANDARD_SEMAFOR")]
    bulina = set(re.findall(r"\.([a-z][a-z0-9_-]*)", bloc)) | {"rap-badge-pct"}
    culori = {"verde", "galben", "rosu", "gri", "info"}
    rele, vazute = [], set()
    surse = glob.glob(os.path.join(RAD, "static", "**", "*.js"), recursive=True) + [os.path.join(RAD, "static", "stil.css")]
    #: un nume de clasă pe care selectorul global al bulinei îl prinde: selectorul e `[class*=…]`, deci potrivirea lui E sub-șir în
    #: numele clasei — aici sub-șirul e chiar semantica de verificat, nu o aproximare a ei
    prinsa = re.compile(r"sem-|pct")
    for f in surse:
        txt = io.open(f, encoding="utf-8").read()
        if f.endswith(".css"):
            nume = re.findall(r"\.([a-zA-Z][a-zA-Z0-9_-]*(?:sem-|pct)[a-zA-Z0-9_-]*)", txt)
        else:
            nume = [t for c in re.findall(r"class=\\?[\"']([^\"']*)", txt) for t in c.split() if prinsa.search(t)]
        vazute.update(nume)
        for t in nume:
            if "${" in t:   # `asi-sem-${culoare}`: prefixul trebuie să dea numai buline, pe fiecare culoare
                pref = t.split("${", 1)[0]
                if not any(pref + c in bulina for c in culori):
                    rele.append((os.path.relpath(f, RAD), t))
            elif t not in bulina:
                rele.append((os.path.relpath(f, RAD), t))
    # premisa: scanul chiar vede bulinele folosite în JS și în CSS (fără ele, `not rele` ar trece pe un scan orb)
    assert len(surse) > 1 and vazute & (bulina - {"rap-badge-pct"}), sorted(vazute)
    assert not rele, rele
