# -*- coding: utf-8 -*-
"""[lotul 12, pachetul ui2] Clasa lui 617, a doua jumătate — „După «Validează» pagina sare sus fără confirmare” (comanda Costin 12.2 pct.9).

Registrul jurnal și „De validat” se redesenează acum pe loc (fără „Se încarcă…”, `core/test_lot12_ui2_ecrane.py`). Celelalte ecrane care
se redesenează după o acțiune pe un rând trec prin „Se încarcă…” (56 de locuri, în 9 fișiere: `firme.js` 38, `rip_ecran.js` 5,
`mijloace_ecran.js` 3, `portal.js` 3, `facturi_ecran.js` 2, `produse_ecran.js` 2, `admin.js`, `reevaluare_ecran.js`, `woo_ecran.js`) —
conținutul scade la un rând, derularea cade la 0, iar omul ajunge sus. Mecanismul e unul, în navigator (`static/js/navigator.js`, la
observatorul ferestrei): derularea de dinainte se pune la loc când lista revine, dacă redesenarea vine după un clic într-un rând.

Ecranele REALE (`navigator.js`, `firme.js`, `stil.css`), în Chromium, cu rutele simulate. Variabila de mediu `UI2_NAVIGATOR` (calea unui
`navigator.js`) servește altă versiune a navigatorului — numai pentru proba schimbării înainte de aplicarea ei.
Mutația: mecanismul scos din navigator -> ROȘU (derularea 0 după clic).

Temei: N/A — regulă de interfață (DS cap.9 v2.102; CLAUDE.md §9).
"""
import json
import os
import urllib.parse

import pytest

from core.test_lot12_ui2_ecrane import INALT, LAT, PAGINA, browser  # noqa: F401 — fixture

_NAV = os.environ.get("UI2_NAVIGATOR")
N = 60


def _pagina(browser, rute):  # noqa: F811
    b, port = browser
    pg = b.new_page(viewport={"width": LAT, "height": INALT})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    if _NAV:
        pg.route("**/static/js/navigator.js*", lambda r: r.fulfill(status=200, content_type="text/javascript",
                                                                   body=open(_NAV, encoding="utf-8").read()))

    def raspuns(route):
        u = urllib.parse.urlsplit(route.request.url)
        if u.path.startswith("/static/"):
            return route.continue_()
        for k in sorted(rute, key=len, reverse=True):
            if u.path.endswith(k) or (k + "/") in u.path:
                v = rute[k]
                return route.fulfill(status=200, content_type="application/json", body=json.dumps(v() if callable(v) else v))
        return route.fulfill(status=200, content_type="application/json", body="{}")
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    pg.route("**/tenants/**", raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    return pg, erori


_SUS = "() => [...document.querySelectorAll('.fereastra-corp')].pop().scrollTop"
_LA = """(sel) => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), r = c.querySelector(sel);
  c.scrollTop += r.getBoundingClientRect().top - c.getBoundingClientRect().top - c.clientHeight / 2; return c.scrollTop; }"""

# ecran sintetic, cu forma celor 56: lista se redesenează după acțiune prin „Se încarcă…”
_ECRAN = """async (inRezumat) => {
  const randeaza = (corp) => {
    corp.innerHTML = `<div class="rezumat-fix"><p class="pf-intro">Luna 09/2026 <button class="buton-secundar" id="p-luna">luna →</button></p></div>
      <table class="fd-tabel"><tbody>${[...Array(%d).keys()].map((i) => `<tr><td>Rândul ${i}</td><td><button class="buton-secundar" data-act="${i}">Acțiune</button></td></tr>`).join("")}</tbody></table>`;
    const dupa = () => { corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>'; setTimeout(() => randeaza(corp), 150); };
    corp.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", dupa));
    corp.querySelector("#p-luna").addEventListener("click", dupa);
  };
  window._nav.deschide('Probă', (c) => randeaza(c), {lat: 'tabel'});
}""" % N


@pytest.mark.parametrize("unde", ["rand", "rezumat"])
def test_def_617_dupa_actiunea_pe_rand_lista_revine_unde_era(browser, unde):  # noqa: F811
    """ROȘU înainte (navigatorul fără mecanism): după clicul pe „Acțiune” din rândul 40, lista revenea sus (derularea 0). Clicul din
    rezumat (luna →) nu păstrează derularea: acolo vine altă listă."""
    pg, erori = _pagina(browser, {})
    try:
        pg.evaluate(_ECRAN, unde == "rezumat")
        pg.wait_for_selector("[data-act='40']", timeout=10000)
        inainte = pg.evaluate(_LA, "[data-act='40']")
        assert inainte > 300, inainte
        pg.evaluate("(s) => document.querySelector(s).click()", "[data-act='40']" if unde == "rand" else "#p-luna")
        pg.wait_for_timeout(100)
        pg.wait_for_selector("[data-act='40']", timeout=5000)
        pg.wait_for_timeout(200)
        dupa = pg.evaluate(_SUS)
    finally:
        pg.close()
    assert not erori, erori
    if unde == "rand":
        assert abs(dupa - inainte) <= 60, (inainte, dupa)       # „pagina sare sus” -> rămâne pe loc (± titlul pus de navigator)
    else:
        assert dupa == 0, (inainte, dupa)


def test_def_617_ecran_real_centre_de_cost_ramane_pe_loc_dupa_dezactivare(browser):  # noqa: F811
    """Un ecran real dintre cele 56: Centre de cost, „Dezactivează” pe centrul 40 -> lista revine unde era (rândul-card `.pf-frand`)."""
    centre = [{"id": i, "nume": "Centru %02d" % i, "activ": True} for i in range(N)]
    pg, erori = _pagina(browser, {"/centre-cost": lambda: {"centre": centre, "ok": True}})
    try:
        pg.evaluate("""async () => { const f = await import('/static/js/ecrane/firme.js');
          f.deschideFirma({id: 1, nume: 'Firma Probă SRL', cui: '1', regim_contabil: 'dubla', tip_firma: 'srl', platitor_tva: true}, window._nav); }""")
        pg.wait_for_selector("#fa-centrecost", timeout=15000)
        pg.click("#fa-centrecost")
        pg.wait_for_selector("[data-toggle='40']", timeout=15000)
        inainte = pg.evaluate(_LA, "[data-toggle='40']")
        assert inainte > 300, inainte
        pg.evaluate("() => document.querySelector(\"[data-toggle='40']\").click()")
        pg.wait_for_timeout(150)
        pg.wait_for_selector("[data-toggle='40']", timeout=5000)
        pg.wait_for_timeout(300)
        dupa = pg.evaluate(_SUS)
    finally:
        pg.close()
    assert not erori, erori
    assert abs(dupa - inainte) <= 60, (inainte, dupa)
