# -*- coding: utf-8 -*-
"""GARD cap.24 — randuri dinamice NIR (ecranStocuri), re-rulate IN POARTA prin chromium headless.

Monteaza modulul real (firme.js -> ecranStocuri) + intercepteaza /tenants/** cu LOGICA REALA a backendului
(core.stocuri_api._nir_campuri_lipsa, exact ca ruta /stocuri/nir). Cele 5 scenarii DOM + no-op devin asertii
care rosesc daca defectul reapare (filtrare inainte de POST, appendChild/remove care pierde valori la re-randare,
rand care dispare tacit, eroare deplasata, index stale la stergere din mijloc).
Reproductibil FARA pasi manuali: auto-instaleaza playwright + chromium; altfel pytest.fail.
"""
import os, sys, json, hashlib, threading, functools, http.server, socketserver, subprocess
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import stocuri_api as S

FILL = [
    {"denumire": "Faina alba", "cantitate": "10", "pret_achizitie": "3", "pret_vanzare": "5"},
    {"denumire": "Ulei floarea", "cantitate": "4", "pret_achizitie": "8", "pret_vanzare": "12"},
]
CANONICAL_LINII = [
    {"denumire": "Faina alba", "cantitate": 10, "pret_achizitie": 3, "pret_vanzare": 5, "cota_tva": 21},
    {"denumire": "Ulei floarea", "cantitate": 4, "pret_achizitie": 8, "pret_vanzare": 12, "cota_tva": 21},
]


def _linii_hash(linii):
    return hashlib.sha256(json.dumps(linii, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  const corp = document.getElementById('mount');
  await m.ecranStocuri(corp, { inapoiPas(){}, deschide(){} }, { id: 1 });
  return true;
}"""


def _handler(posted):
    def h(route, request):
        url = request.url
        if url.endswith("/stocuri/articole"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"articole": []})); return
        if url.endswith("/stocuri/locatii"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"locatii": []})); return
        if url.endswith("/retete") and request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"retete": []})); return
        if "/stocuri/nir" in url and request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"nir": []})); return
        if "/stocuri/nir" in url and request.method == "POST":
            payload = json.loads(request.post_data)
            posted.append(payload)
            lipsa = S._nir_campuri_lipsa(payload.get("linii") or [])   # AUTORITATEA REALA (aceeasi ca ruta)
            if lipsa:
                route.fulfill(status=422, content_type="application/json", body=json.dumps({
                    "detail": {"mesaj": "Completeaza articolele: " + "; ".join(x["eticheta"] for x in lipsa),
                               "erori_campuri": [{"camp": x["camp"], "mesaj": x["eticheta"]} for x in lipsa]}}))
            else:
                route.fulfill(status=200, content_type="application/json", body=json.dumps(
                    {"inregistrari": [1], "transport": 0, "taxe": 0, "cost_total": "0",
                     "adaos_total": "0", "tva_neexigibila": "0"}))
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
def nir_env():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=False)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            pytest.fail("GARD headless nu poate rula: 'playwright' lipseste si pip install a esuat. NU e skip verde-fals.")

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
        pg.wait_for_selector("#sn-toggle")
        pg.click("#sn-toggle")           # dezvaluie zona NIR (hidden by default)
        pg.wait_for_selector("#sn-linii")
        return pg

    try:
        yield {"make_page": make_page, "posted": posted}
    finally:
        br.close(); pw.stop(); srv.shutdown()


def _fill_benef(pg):
    pg.fill("#sn-numar", "NIR-1")


def _fill_linie(pg, i, l):
    pg.fill("#nir-l%d-denumire" % i, l["denumire"])
    pg.fill("#nir-l%d-cantitate" % i, l["cantitate"])
    pg.fill("#nir-l%d-pret_achizitie" % i, l["pret_achizitie"])
    pg.fill("#nir-l%d-pret_vanzare" % i, l["pret_vanzare"])


def _randuri(pg):
    return pg.locator("#sn-linii > [data-idx]").count()


def test_noop_lista_nefiltrata_si_hash(nir_env):
    pg = nir_env["make_page"](); pg.click("#sn-plus")   # row0 (bootstrap) + row1
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0]); _fill_linie(pg, 1, FILL[1])
    pg.click("#sn-salveaza"); pg.wait_for_timeout(300)
    payload = nir_env["posted"][-1]
    assert len(payload["linii"]) == 2, "lista trimisa nu are 2 articole (filtrare?): %r" % payload["linii"]
    assert payload["linii"] == CANONICAL_LINII, "liniile POST difera de canonical: %r" % payload["linii"]
    assert _linii_hash(payload["linii"]) == _linii_hash(CANONICAL_LINII), "hash NIR difera (no-op spart)"
    pg.close()


def test_rand_adaugat(nir_env):
    pg = nir_env["make_page"]()
    assert _randuri(pg) == 1
    pg.click("#sn-plus"); pg.click("#sn-plus")
    assert _randuri(pg) == 3, "adaugarea de articole nu re-randeaza lista din model"
    pg.close()


def test_rand_sters_din_mijloc_pastreaza_valori_si_reindexeaza(nir_env):
    pg = nir_env["make_page"]()
    pg.click("#sn-plus"); pg.click("#sn-plus")   # l0,l1,l2
    pg.fill("#nir-l0-denumire", "ALFA"); pg.fill("#nir-l1-denumire", "BETA"); pg.fill("#nir-l2-denumire", "GAMA")
    pg.click('.nir-l-sterge[data-idx="1"]'); pg.wait_for_timeout(150)   # sterge MIJLOCUL
    assert _randuri(pg) == 2, "stergerea nu a redus lista (re-randare integrala?)"
    assert pg.input_value("#nir-l0-denumire") == "ALFA", "valoarea l0 s-a pierdut la re-randare"
    assert pg.input_value("#nir-l1-denumire") == "GAMA", "l1 dupa stergere trebuie sa fie fosta l2 (reindexata)"
    assert pg.locator("#nir-l2-denumire").count() == 0, "a ramas un al treilea articol"
    pg.close()


def test_doua_randuri_cu_erori_simultan(nir_env):
    pg = nir_env["make_page"](); pg.click("#sn-plus")
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0])
    # l1: denumire GOALA + cantitate 0, dar pret_achizitie completat -> exact doua erori
    pg.fill("#nir-l1-pret_achizitie", "5")
    pg.fill("#nir-l1-cantitate", "0")
    pg.click("#sn-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="nir-l1-denumire"]').count() == 1, "eroarea nu e langa nir-l1-denumire"
    assert pg.locator('.msg-eroare[data-camp="nir-l1-cantitate"]').count() == 1, "eroarea nu e langa nir-l1-cantitate"
    assert pg.locator('#mount .msg-eroare[data-camp^="nir-l0-"]').count() == 0, "linia completa l0 are erori false"
    pg.close()


def test_revalidare_dupa_corectarea_unuia_singur(nir_env):
    pg = nir_env["make_page"](); pg.click("#sn-plus")
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0])
    pg.fill("#nir-l1-pret_achizitie", "5"); pg.fill("#nir-l1-cantitate", "0")
    pg.click("#sn-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="nir-l1-denumire"]').count() == 1
    assert pg.locator('.msg-eroare[data-camp="nir-l1-cantitate"]').count() == 1
    pg.fill("#nir-l1-denumire", "Zahar")   # corectez DOAR denumirea (cantitate ramane 0)
    pg.click("#sn-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="nir-l1-denumire"]').count() == 0, "eroarea denumirii corectate nu a fost curatata"
    assert pg.locator('.msg-eroare[data-camp="nir-l1-cantitate"]').count() == 1, "eroarea cantitatii inca 0 a disparut gresit"
    pg.close()


def test_rand_incomplet_in_mijloc_nu_dispare(nir_env):
    pg = nir_env["make_page"](); pg.click("#sn-plus"); pg.click("#sn-plus")   # l0,l1,l2
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0]); _fill_linie(pg, 2, FILL[1])
    # l1 = mijloc INCOMPLET: cantitate + pret completate, denumire GOALA -> doar denumirea lipseste
    pg.fill("#nir-l1-cantitate", "2"); pg.fill("#nir-l1-pret_achizitie", "3")
    pg.click("#sn-salveaza"); pg.wait_for_timeout(300)
    payload = nir_env["posted"][-1]
    assert len(payload["linii"]) == 3, "articolul incomplet din mijloc a disparut tacit (filtrare?): %r" % payload["linii"]
    assert payload["linii"][1]["denumire"] == "", "articolul din mijloc nu mai e pe pozitia 1 (reordonare/filtrare?)"
    assert pg.locator('.msg-eroare[data-camp="nir-l1-denumire"]').count() == 1, "eroarea nu e la articolul REAL din mijloc (nir-l1)"
    pg.close()
