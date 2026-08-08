# -*- coding: utf-8 -*-
"""GARD cap.24 — randuri dinamice RETETE (ingrediente HoReCa), re-rulate IN POARTA prin chromium headless.

Monteaza sectiunea reala (static/js/ecrane/firme.js -> sectiuneaCV, care contine formularul de retete) +
intercepteaza /tenants/** cu LOGICA REALA a backendului (core.retete_api._ingrediente_campuri_lipsa, exact ca
ruta /retete). Cele 5 scenarii DOM + proba no-op devin asertii care rosesc daca defectul reapare (filtrare
inainte de POST, ingredient care dispare tacit, eroare deplasata, pierderea valorilor la re-randare, index stale
la stergere din mijloc). Reproductibil FARA pasi manuali: auto-instaleaza playwright + chromium; altfel pytest.fail.
"""
import os, sys, json, hashlib, threading, functools, http.server, socketserver, subprocess
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import retete_api as R

ARTS = [
    {"id": 1, "denumire": "Faina", "cmp": "2.00", "stoc": "10", "um": "kg"},
    {"id": 2, "denumire": "Ulei", "cmp": "5.00", "stoc": "5", "um": "l"},
]
CANONICAL_LINII = [
    {"articol_id": 1, "cantitate": 2},
    {"articol_id": 1, "cantitate": 3},
]


def _linii_hash(linii):
    return hashlib.sha256(json.dumps(linii, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"><div id="cv-zona"></div><div id="msgs"></div></div>';
  const corp = document.getElementById('mount');
  const zonaM = document.getElementById('msgs');
  await m.sectiuneaCV(corp, { id: 1 }, zonaM);
  return true;
}"""


def _handler(posted):
    def h(route, request):
        url = request.url
        if url.endswith("/stocuri/articole"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"articole": ARTS}))
            return
        if url.endswith("/stocuri/locatii"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"locatii": []}))
            return
        if url.endswith("/retete") and request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"retete": []}))
            return
        if url.endswith("/retete") and request.method == "POST":
            payload = json.loads(request.post_data)
            posted.append(payload)
            linii = payload.get("linii") or []
            if not (payload.get("denumire") or "").strip():
                route.fulfill(status=422, content_type="application/json",
                              body=json.dumps({"detail": "Denumirea retetei e obligatorie."}))
                return
            if not linii:
                route.fulfill(status=422, content_type="application/json",
                              body=json.dumps({"detail": "Adauga cel putin un ingredient."}))
                return
            lipsa = R._ingrediente_campuri_lipsa(linii)   # AUTORITATEA REALA (aceeasi ca ruta)
            if lipsa:
                route.fulfill(status=422, content_type="application/json", body=json.dumps({
                    "detail": {"mesaj": "Completeaza ingredientele: " + "; ".join(x["eticheta"] for x in lipsa),
                               "erori_campuri": [{"camp": x["camp"], "mesaj": x["eticheta"]} for x in lipsa]}}))
            else:
                route.fulfill(status=200, content_type="application/json", body=json.dumps({"id": 1}))
            return
        route.fulfill(status=200, content_type="application/json", body="{}")
    return h


def _lanseaza_chromium(pw):
    try:
        return pw.chromium.launch()
    except Exception as e:
        msg = str(e).lower()
        if "executable" in msg or "playwright install" in msg or "download" in msg:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
            try:
                return pw.chromium.launch()
            except Exception:
                return None
        return None


@pytest.fixture(scope="module")
def rt_env():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=False)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            pytest.fail("GARD headless nu poate rula: pachetul 'playwright' lipseste si pip install a esuat. "
                        "NU e skip verde-fals.")

    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD)

    class _Srv(socketserver.TCPServer):
        allow_reuse_address = True

    srv = _Srv(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil si auto-instalarea a esuat. NU e skip verde-fals.")

    posted = []

    def make_page():
        pg = br.new_page()
        pg.route("**/tenants/**", _handler(posted))
        pg.goto("http://127.0.0.1:%d/static/" % port)
        pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
        return pg

    try:
        yield {"make_page": make_page, "posted": posted}
    finally:
        br.close(); pw.stop(); srv.shutdown()


def _randuri(pg):
    return pg.locator("#rt-ingrediente > [data-idx]").count()


def test_noop_lista_nefiltrata_si_hash(rt_env):
    pg = rt_env["make_page"]()
    pg.fill("#rt-den", "Meniul zilei")
    pg.click("#rt-plus"); pg.click("#rt-plus")
    pg.fill("#rt-l0-cantitate", "2"); pg.fill("#rt-l1-cantitate", "3")
    pg.click("#rt-salveaza"); pg.wait_for_timeout(300)
    payload = rt_env["posted"][-1]
    assert len(payload["linii"]) == 2, "lista trimisa nu are 2 ingrediente (filtrare?): %r" % payload["linii"]
    assert payload["linii"] == CANONICAL_LINII, "liniile POST difera de canonical: %r" % payload["linii"]
    assert _linii_hash(payload["linii"]) == _linii_hash(CANONICAL_LINII), "hash reteta difera (no-op spart)"
    pg.close()


def test_ingredient_adaugat(rt_env):
    pg = rt_env["make_page"]()
    assert _randuri(pg) == 0
    pg.click("#rt-plus"); pg.click("#rt-plus")
    assert _randuri(pg) == 2, "adaugarea de ingrediente nu re-randeaza lista din model"
    pg.close()


def test_ingredient_sters_din_mijloc_pastreaza_valori_si_reindexeaza(rt_env):
    pg = rt_env["make_page"]()
    pg.click("#rt-plus"); pg.click("#rt-plus"); pg.click("#rt-plus")   # l0,l1,l2
    pg.fill("#rt-l0-cantitate", "1"); pg.fill("#rt-l1-cantitate", "2"); pg.fill("#rt-l2-cantitate", "3")
    pg.click('.rt-scoate[data-i="1"]'); pg.wait_for_timeout(150)   # sterge MIJLOCUL
    assert _randuri(pg) == 2, "stergerea nu a redus lista (re-randare integrala?)"
    assert pg.input_value("#rt-l0-cantitate") == "1", "valoarea l0 s-a pierdut la re-randare"
    assert pg.input_value("#rt-l1-cantitate") == "3", "l1 dupa stergere trebuie sa fie fosta l2 (reindexata)"
    assert pg.locator("#rt-l2-cantitate").count() == 0, "a ramas un al treilea ingredient"
    pg.close()


def test_doua_randuri_cu_erori_simultan(rt_env):
    pg = rt_env["make_page"]()
    pg.fill("#rt-den", "Meniul zilei")
    pg.click("#rt-plus"); pg.click("#rt-plus")   # doua ingrediente, ambele cu cantitate GOALA
    pg.click("#rt-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="rt-l0-cantitate"]').count() == 1, "eroarea nu e langa rt-l0-cantitate"
    assert pg.locator('.msg-eroare[data-camp="rt-l1-cantitate"]').count() == 1, "eroarea nu e langa rt-l1-cantitate"
    pg.close()


def test_revalidare_dupa_corectarea_unuia_singur(rt_env):
    pg = rt_env["make_page"]()
    pg.fill("#rt-den", "Meniul zilei")
    pg.click("#rt-plus"); pg.click("#rt-plus")
    pg.click("#rt-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="rt-l0-cantitate"]').count() == 1
    assert pg.locator('.msg-eroare[data-camp="rt-l1-cantitate"]').count() == 1
    pg.fill("#rt-l0-cantitate", "5")   # corectez DOAR primul
    pg.click("#rt-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="rt-l0-cantitate"]').count() == 0, "eroarea corectata nu a fost curatata"
    assert pg.locator('.msg-eroare[data-camp="rt-l1-cantitate"]').count() == 1, "eroarea ingredientului inca gol a disparut gresit"
    pg.close()


def test_ingredient_incomplet_in_mijloc_nu_dispare(rt_env):
    pg = rt_env["make_page"]()
    pg.fill("#rt-den", "Meniul zilei")
    pg.click("#rt-plus"); pg.click("#rt-plus"); pg.click("#rt-plus")   # l0,l1,l2
    pg.fill("#rt-l0-cantitate", "2"); pg.fill("#rt-l2-cantitate", "3")   # l1 = mijloc INCOMPLET (cantitate goala)
    pg.click("#rt-salveaza"); pg.wait_for_timeout(300)
    payload = rt_env["posted"][-1]
    assert len(payload["linii"]) == 3, "ingredientul incomplet din mijloc a disparut tacit (filtrare?): %r" % payload["linii"]
    assert payload["linii"][1]["cantitate"] in ("", None, 0), "ingredientul din mijloc nu mai e pe pozitia 1 (reordonare/filtrare?)"
    assert pg.locator('.msg-eroare[data-camp="rt-l1-cantitate"]').count() == 1, "eroarea nu e la ingredientul REAL din mijloc (rt-l1)"
    pg.close()
