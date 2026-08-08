# -*- coding: utf-8 -*-
"""GARD cap.24 regula 2 — inventar (sectiuneaCV), re-rulat IN POARTA prin chromium headless.

Inventarul e o lista FIXA de articole (fara add/delete de randuri user -> regula 1 nu se aplica): fixul e DOAR
regula 2 (fara filtrare inainte de POST). Se trimit TOATE articolele; backendul e autoritatea (sare articolele
necontorizate = faptic gol, NU e eroare; eroare per-linie doar la valoare invalida, plasata langa camp cvi-a{id}).
Asertii: lista trimisa = lista randata (nefiltrata, blank inclus ca null) + hash; eroare per-linie langa campul ei;
re-validare curata doar campul corectat; articolul necontorizat NU produce eroare. Mutatie: re-filtrarea -> rosu.
"""
import os, sys, json, hashlib, threading, functools, http.server, socketserver, subprocess
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

ARTS = [
    {"id": 1, "denumire": "Faina", "stoc": "10", "um": "kg", "cmp": "3.00"},
    {"id": 2, "denumire": "Ulei", "stoc": "5", "um": "l", "cmp": "8.00"},
    {"id": 3, "denumire": "Zahar", "stoc": "20", "um": "kg", "cmp": "4.00"},
]
CANONICAL_LINII = [
    {"articol_id": 1, "faptic": "12"},
    {"articol_id": 2, "faptic": "8"},
    {"articol_id": 3, "faptic": None},
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
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"articole": ARTS})); return
        if url.endswith("/stocuri/locatii"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"locatii": []})); return
        if url.endswith("/retete") and request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"retete": []})); return
        if "/stocuri/inventar" in url and request.method == "POST":
            payload = json.loads(request.post_data)
            posted.append(payload)
            # AUTORITATEA: sare blank-urile (necontorizat, NU eroare); valoare negativa = eroare per-linie
            # (proxy pt "minus peste stocul scriptic"), langa camp cvi-a{id}-faptic.
            rez = []
            for l in payload.get("linii", []):
                fv = l.get("faptic")
                if fv is None or (isinstance(fv, str) and fv.strip() == ""):
                    continue
                try:
                    v = float(fv)
                except (TypeError, ValueError):
                    rez.append({"articol_id": l["articol_id"], "camp": "cvi-a%s-faptic" % l["articol_id"],
                                "eroare": "valoare invalida (numar)"}); continue
                if v < 0:
                    rez.append({"articol_id": l["articol_id"], "denumire": "Art%s" % l["articol_id"],
                                "camp": "cvi-a%s-faptic" % l["articol_id"], "eroare": "minus peste stocul scriptic"}); continue
                rez.append({"articol_id": l["articol_id"], "denumire": "Art%s" % l["articol_id"], "diferenta": "0"})
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"rezultate": rez}))
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
def inv_env():
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
        pg.wait_for_selector("#cv-inv")
        pg.click("#cv-inv")                 # dezvaluie zona de inventar (faptic per articol)
        pg.wait_for_selector("#cvi-salveaza")
        return pg

    try:
        yield {"make_page": make_page, "posted": posted}
    finally:
        br.close(); pw.stop(); srv.shutdown()


def test_noop_toate_articolele_trimise_nefiltrat(inv_env):
    pg = inv_env["make_page"]()
    pg.fill("#cvi-a1-faptic", "12"); pg.fill("#cvi-a2-faptic", "8")   # a3 ramane GOL (necontorizat)
    pg.click("#cvi-salveaza"); pg.wait_for_timeout(300)
    payload = inv_env["posted"][-1]
    assert len(payload["linii"]) == 3, "nu s-au trimis TOATE articolele (filtrare?): %r" % payload["linii"]
    assert payload["linii"] == CANONICAL_LINII, "liniile POST difera de canonical: %r" % payload["linii"]
    assert payload["linii"][2]["faptic"] is None, "articolul necontorizat trebuie trimis cu faptic null, nu filtrat"
    assert _linii_hash(payload["linii"]) == _linii_hash(CANONICAL_LINII), "hash inventar difera (no-op spart)"
    pg.close()


def test_articol_necontorizat_nu_e_eroare(inv_env):
    pg = inv_env["make_page"]()
    pg.fill("#cvi-a1-faptic", "12")   # a2, a3 goale -> necontorizate, NU erori
    pg.click("#cvi-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="cvi-a2-faptic"]').count() == 0, "articolul necontorizat a2 a produs eroare"
    assert pg.locator('.msg-eroare[data-camp="cvi-a3-faptic"]').count() == 0, "articolul necontorizat a3 a produs eroare"
    payload = inv_env["posted"][-1]
    assert len(payload["linii"]) == 3, "articolele necontorizate au fost filtrate tacit: %r" % payload["linii"]
    pg.close()


def test_eroare_per_linie_langa_camp(inv_env):
    pg = inv_env["make_page"]()
    pg.fill("#cvi-a1-faptic", "-5")   # valoare care produce eroare per-linie pe articolul 1
    pg.fill("#cvi-a2-faptic", "8")
    pg.click("#cvi-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="cvi-a1-faptic"]').count() == 1, "eroarea nu e langa cvi-a1-faptic"
    assert pg.locator('.msg-eroare[data-camp="cvi-a2-faptic"]').count() == 0, "articolul valid a2 are eroare falsa"
    pg.close()


def test_revalidare_dupa_corectarea_unuia_singur(inv_env):
    pg = inv_env["make_page"]()
    pg.fill("#cvi-a1-faptic", "-5"); pg.fill("#cvi-a2-faptic", "-5")   # ambele produc eroare
    pg.click("#cvi-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="cvi-a1-faptic"]').count() == 1
    assert pg.locator('.msg-eroare[data-camp="cvi-a2-faptic"]').count() == 1
    pg.fill("#cvi-a1-faptic", "5")   # corectez DOAR articolul 1
    pg.click("#cvi-salveaza"); pg.wait_for_timeout(300)
    assert pg.locator('.msg-eroare[data-camp="cvi-a1-faptic"]').count() == 0, "eroarea corectata nu a fost curatata"
    assert pg.locator('.msg-eroare[data-camp="cvi-a2-faptic"]').count() == 1, "eroarea articolului inca gresit a disparut gresit"
    pg.close()
