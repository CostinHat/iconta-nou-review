# -*- coding: utf-8 -*-
"""GARD cap.24 batch 3b — randuri dinamice emitere factura, re-rulate IN POARTA prin chromium headless.

Monteaza modulul real (static/js/ecrane/emitere_ecran.js) + intercepteaza /tenants/** cu LOGICA REALA a
backendului (core.facturi_api.linii_campuri_lipsa + totaluri_din_linii). Cele 5 scenarii DOM + proba no-op
sha256 pe factura devin asertii care rosesc daca defectul reapare (filtrare inainte de POST, rand care dispare
tacit, eroare deplasata, pierderea valorilor la re-randare). Reproductibil FARA pasi manuali: auto-instaleaza
playwright + chromium daca lipsesc; altfel pytest.fail (niciodata skip verde-fals).
"""
import os, sys, json, hashlib, threading, functools, http.server, socketserver, subprocess
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import facturi_api as F

COTA = 21

# FILL = valorile tastate (siruri); CANONICAL = liniile din payload asteptat (numericele devin int prin
# parseFloat->JSON; cota_tva = COTA din potrivirea automata).
FILL = [
    {"descriere": "Serviciu consultanta", "cantitate": "2", "pret_unitar": "100"},
    {"descriere": "Produs marfa vandut", "cantitate": "3", "pret_unitar": "50"},
]
CANONICAL_LINII = [
    {"descriere": "Serviciu consultanta", "cantitate": 2, "pret_unitar": 100, "cota_tva": COTA, "articol_id": None},
    {"descriere": "Produs marfa vandut", "cantitate": 3, "pret_unitar": 50, "cota_tva": COTA, "articol_id": None},
]


def _factura_content_hash(linii):
    """sha256 pe CONTINUTUL DETERMINIST al facturii generate (linii + totaluri PURE, fara contorul volatil).
    totaluri_din_linii e pur (fara DB). Frontendul nefiltrat -> aceleasi linii -> acelasi continut -> acelasi hash."""
    tot = F.totaluri_din_linii(linii)
    payload = {"linii": linii, "total": str(tot["total"]), "tva": str(tot["tva"])}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  const corp = document.getElementById('mount');
  await m.randeazaEmitere(corp, { inapoi(){}, setInapoi(){} }, 1, {});
  return true;
}"""


def _handler(posted):
    def h(route, request):
        url = request.url
        if url.endswith("/facturi/numerotare"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"serie": None, "urmator_numar": 1, "configurata": True}))
            return
        if url.endswith("/stocuri/articole"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"articole": []}))
            return
        if url.endswith("/produse/potriveste"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "cota": COTA}))
            return
        if url.endswith("/facturi/emite"):
            payload = json.loads(request.post_data)
            posted.append(payload)
            lipsa = F.linii_campuri_lipsa(payload["linii"])   # AUTORITATEA REALA
            if lipsa:
                route.fulfill(status=422, content_type="application/json", body=json.dumps({
                    "detail": {"cod": "LINII_INCOMPLETE",
                               "mesaj": "Completeaza liniile: " + "; ".join(x["eticheta"] for x in lipsa),
                               "campuri": lipsa}}))
            else:
                tot = F.totaluri_din_linii(payload["linii"])
                route.fulfill(status=200, content_type="application/json", body=json.dumps(
                    {"ok": True, "factura_id": 1, "numar": "1", "serie": "",
                     "total": float(tot["total"]), "tva": float(tot["tva"])}))
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
def em_env():
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
        pg.evaluate(MOUNT, ["/static/js/ecrane/emitere_ecran.js"])
        return pg

    try:
        yield {"make_page": make_page, "posted": posted}
    finally:
        br.close(); pw.stop(); srv.shutdown()


def _fill_benef(pg):
    pg.fill("#em-nume", "Client SRL")
    pg.fill("#em-cui", "RO12345678")


def _fill_linie(pg, i, l):
    pg.fill("#em-l%d-descriere" % i, l["descriere"])
    pg.fill("#em-l%d-cantitate" % i, l["cantitate"])
    pg.fill("#em-l%d-pret_unitar" % i, l["pret_unitar"])


def _randuri(pg):
    return pg.locator("#em-linii > [data-idx]").count()


def test_noop_lista_nefiltrata_si_sha256_factura(em_env):
    """No-op: lista trimisa = lista randata (nefiltrata, 2 linii complete); continutul facturii (linii + totaluri
    PURE) are sha256 IDENTIC cu al liniilor canonical. Filtrare/reordonare/tip schimbat -> payload != canonical -> rosu."""
    pg = em_env["make_page"](); pg.click("#em-add-linie")
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0]); _fill_linie(pg, 1, FILL[1])
    pg.wait_for_timeout(800)   # asteapta potrivirea automata a cotei (debounce 550ms)
    pg.click("#em-emite"); pg.wait_for_timeout(400)
    payload = em_env["posted"][-1]
    assert len(payload["linii"]) == 2, "lista trimisa nu are 2 linii (filtrare?): %r" % payload["linii"]
    assert payload["linii"] == CANONICAL_LINII, "liniile POST difera de canonical: %r" % payload["linii"]
    assert _factura_content_hash(payload["linii"]) == _factura_content_hash(CANONICAL_LINII), "sha256 factura difera (no-op spart)"
    pg.close()


def test_rand_adaugat(em_env):
    pg = em_env["make_page"]()
    assert _randuri(pg) == 1
    pg.click("#em-add-linie"); pg.click("#em-add-linie")
    assert _randuri(pg) == 3, "adaugarea de linii nu re-randeaza lista din model"
    pg.close()


def test_rand_sters_din_mijloc_pastreaza_valori_si_reindexeaza(em_env):
    pg = em_env["make_page"]()
    pg.click("#em-add-linie"); pg.click("#em-add-linie")   # l0,l1,l2
    pg.fill("#em-l0-descriere", "ALFA"); pg.fill("#em-l1-descriere", "BETA"); pg.fill("#em-l2-descriere", "GAMA")
    pg.click('.em-l-sterge[data-idx="1"]'); pg.wait_for_timeout(150)   # sterge MIJLOCUL
    assert _randuri(pg) == 2, "stergerea nu a redus lista (re-randare integrala?)"
    assert pg.input_value("#em-l0-descriere") == "ALFA", "valoarea l0 s-a pierdut la re-randare"
    assert pg.input_value("#em-l1-descriere") == "GAMA", "l1 dupa stergere trebuie sa fie fosta l2 (reindexata), valoarea pastrata"
    assert pg.locator("#em-l2-descriere").count() == 0, "a ramas o a treia linie"
    pg.close()


def test_doua_randuri_cu_erori_simultan(em_env):
    pg = em_env["make_page"](); pg.click("#em-add-linie")
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0])
    # l1: denumire GOALA + cantitate 0 -> doua erori
    pg.fill("#em-l1-cantitate", "0")
    pg.click("#em-emite"); pg.wait_for_timeout(400)
    assert pg.locator('.msg-eroare[data-camp="em-l1-descriere"]').count() == 1, "eroarea nu e langa em-l1-descriere"
    assert pg.locator('.msg-eroare[data-camp="em-l1-cantitate"]').count() == 1, "eroarea nu e langa em-l1-cantitate"
    assert pg.locator('#mount .msg-eroare[data-camp^="em-l0-"]').count() == 0, "linia completa l0 are erori false"
    pg.close()


def test_revalidare_dupa_corectarea_unuia_singur(em_env):
    pg = em_env["make_page"](); pg.click("#em-add-linie")
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0])
    pg.fill("#em-l1-cantitate", "0")
    pg.click("#em-emite"); pg.wait_for_timeout(400)
    assert pg.locator('.msg-eroare[data-camp="em-l1-descriere"]').count() == 1
    assert pg.locator('.msg-eroare[data-camp="em-l1-cantitate"]').count() == 1
    pg.fill("#em-l1-descriere", "Serviciu nou")   # corectez DOAR denumirea (cantitate ramane 0)
    pg.click("#em-emite"); pg.wait_for_timeout(400)
    assert pg.locator('.msg-eroare[data-camp="em-l1-descriere"]').count() == 0, "eroarea denumirii corectate nu a fost curatata"
    assert pg.locator('.msg-eroare[data-camp="em-l1-cantitate"]').count() == 1, "eroarea cantitatii inca 0 a disparut gresit"
    pg.close()


def test_rand_incomplet_in_mijloc_nu_dispare(em_env):
    """DEFECTUL: linia incompleta din mijloc NU se filtreaza tacit; se trimit toate liniile si eroarea e la linia
    REALA. Mutatie: reintroducerea filtrului in trimiteEmitere face aceasta asertie ROSIE."""
    pg = em_env["make_page"](); pg.click("#em-add-linie"); pg.click("#em-add-linie")   # l0,l1,l2
    _fill_benef(pg)
    _fill_linie(pg, 0, FILL[0]); _fill_linie(pg, 2, FILL[1])
    # l1 = mijloc INCOMPLET: denumire goala (cantitate ramane 1 default -> doar denumirea lipseste)
    pg.click("#em-emite"); pg.wait_for_timeout(400)
    payload = em_env["posted"][-1]
    assert len(payload["linii"]) == 3, "linia incompleta din mijloc a disparut tacit (filtrare reintrodusa?): %r" % payload["linii"]
    assert payload["linii"][1]["descriere"] == "", "linia din mijloc nu mai e pe pozitia 1 (reordonare/filtrare?)"
    assert pg.locator('.msg-eroare[data-camp="em-l1-descriere"]').count() == 1, "eroarea nu e la linia REALA din mijloc (em-l1)"
    pg.close()
