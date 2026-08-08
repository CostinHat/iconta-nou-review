# -*- coding: utf-8 -*-
"""GARD cap.24 batch 3a — randuri dinamice e-Transport, re-rulate in POARTA prin chromium headless.

Monteaza modulul REAL (static/js/ecrane/etransport_ecran.js) intr-o pagina servita local si intercepteaza
/tenants/** cu LOGICA REALA a backendului (core.etransport.campuri_required_lipsa + xml_notificare). Cele 5
scenarii DOM de la 3a + proba no-op sha256 devin asertii care rosesc daca defectul reapare:
  - rand adaugat / rand sters din mijloc (valori pastrate + reindexare)
  - doua randuri cu erori simultan (fiecare langa campul ei)
  - re-validare dupa corectarea unuia singur
  - rand incomplet in mijloc care NU mai dispare (defectul reparat la 3a)
  - no-op: lista trimisa = lista randata (nefiltrata) + XML identic cu corpul canonical complet

REPRODUCTIBIL de pe repo curat, FARA pasi manuali: daca binarul chromium lipseste, se auto-instaleaza
(playwright install chromium). Daca nici asa nu poate rula -> pytest.fail (NU skip verde-fals).
Infra (driver/browser) e gitignored (>100MB); pachetul python + browserul se provizioneaza automat aici.
"""
import os, sys, json, hashlib, threading, functools, http.server, socketserver, subprocess
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import etransport as E

CUI = "12345678"

# set complet de referinta (2 randuri). FILL = valorile tastate (siruri); CANONICAL = corpul POST asteptat
# (numericele devin int prin parseFloat->JSON->json.loads). Structura = exact ce emite construiesteCorp.
FILL = {
    "cod_tip_operatiune": "30", "ref": "REF-1",
    "bunuri": [
        {"cod_scop": "101", "cod_tarifar": "12345678", "denumire": "Marfa A", "cantitate": "10", "um": "H87", "greutate_neta": "5", "greutate_bruta": "6", "valoare_fara_tva": "100"},
        {"cod_scop": "201", "cod_tarifar": "87654321", "denumire": "Marfa B", "cantitate": "2", "um": "KGM", "greutate_neta": "3", "greutate_bruta": "4", "valoare_fara_tva": "50"},
    ],
    "partener": {"cod_tara": "RO", "cod": "RO99999999", "denumire": "Partener SRL"},
    "transport": {"nr_vehicul": "B123ABC", "nr_remorca1": "B999XYZ", "cod_tara_org": "RO", "cod_org": "12345678", "denumire_org": "Transportator SRL", "data": "2026-08-10"},
    "start": {"cod_judet": "B", "localitate": "Bucuresti", "strada": "Str. A", "numar": "1"},
    "final": {"cod_judet": "CJ", "localitate": "Cluj", "strada": "Str. B", "numar": "2"},
}


def _num(s):
    return int(s) if str(s).lstrip("-").isdigit() else float(s)


def _canonical(fill):
    return {
        "ref": fill["ref"], "cod_tip_operatiune": fill["cod_tip_operatiune"],
        "bunuri": [{"cod_scop": b["cod_scop"], "cod_tarifar": b["cod_tarifar"], "denumire": b["denumire"],
                    "cantitate": _num(b["cantitate"]), "um": b["um"], "greutate_neta": _num(b["greutate_neta"]),
                    "greutate_bruta": _num(b["greutate_bruta"]), "valoare_fara_tva": _num(b["valoare_fara_tva"])}
                   for b in fill["bunuri"]],
        "partener": dict(fill["partener"]), "transport": dict(fill["transport"]),
        "start": dict(fill["start"]), "final": dict(fill["final"]),
    }


CANONICAL = _canonical(FILL)

MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  const corp = document.getElementById('mount');
  await m.ecranEtransport(corp, { deschide(){}, inapoiPas(){} }, { id: 1 });
  return true;
}"""


def _handler(posted):
    def h(route, request):
        url = request.url
        if url.endswith("/etransport/trimiteri"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"trimiteri": []}))
            return
        if url.endswith("/etransport-xml") or url.endswith("/etransport/trimite"):
            corp = json.loads(request.post_data)
            posted.append(corp)
            lipsa = E.campuri_required_lipsa(corp)   # AUTORITATEA REALA
            if lipsa:
                route.fulfill(status=422, content_type="application/json", body=json.dumps({
                    "detail": {"cod": "CAMPURI_LIPSA",
                               "mesaj": "Campuri obligatorii lipsa: " + "; ".join(x["eticheta"] for x in lipsa),
                               "campuri": lipsa}}))
            else:
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps({"xml": E.xml_notificare(CUI, corp), "nota": "ok"}))
            return
        route.fulfill(status=200, content_type="application/json", body="{}")
    return h


def _lanseaza_chromium(pw):
    """Lanseaza chromium; daca binarul lipseste -> auto-install (fara pasi manuali); daca tot nu merge -> None."""
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
def et_env():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=False)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            pytest.fail("GARD headless nu poate rula: pachetul 'playwright' lipseste si pip install a esuat "
                        "(reproductibil: pip install playwright). NU e skip verde-fals.")

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
        pytest.fail("GARD headless nu poate rula: chromium indisponibil si auto-instalarea a esuat "
                    "(reproductibil: playwright install chromium). NU e skip verde-fals.")

    posted = []

    def make_page():
        pg = br.new_page()
        pg.route("**/tenants/**", _handler(posted))
        pg.goto("http://127.0.0.1:%d/static/" % port)
        pg.evaluate(MOUNT, ["/static/js/ecrane/etransport_ecran.js"])
        return pg

    try:
        yield {"make_page": make_page, "posted": posted}
    finally:
        br.close(); pw.stop(); srv.shutdown()


def _fill_rand(pg, i, b):
    pg.select_option("#b%d-cod_scop" % i, b["cod_scop"])
    for camp in ("cod_tarifar", "denumire", "cantitate", "um", "greutate_neta", "greutate_bruta", "valoare_fara_tva"):
        pg.fill("#b%d-%s" % (i, camp), b[camp])


def _fill_restul(pg, c):
    pg.select_option("#et-tip", c["cod_tip_operatiune"]); pg.fill("#et-ref", c["ref"])
    pg.fill("#p-cod_tara", c["partener"]["cod_tara"]); pg.fill("#p-cod", c["partener"]["cod"]); pg.fill("#p-denumire", c["partener"]["denumire"])
    tr = c["transport"]
    pg.fill("#t-nr_vehicul", tr["nr_vehicul"]); pg.fill("#t-nr_remorca1", tr["nr_remorca1"])
    pg.fill("#t-cod_tara_org", tr["cod_tara_org"]); pg.fill("#t-cod_org", tr["cod_org"])
    pg.fill("#t-denumire_org", tr["denumire_org"]); pg.fill("#t-data", tr["data"])
    for pre, k in (("s", "start"), ("f", "final")):
        l = c[k]
        pg.select_option("#%s-judet" % pre, l["cod_judet"])
        pg.fill("#%s-localitate" % pre, l["localitate"]); pg.fill("#%s-strada" % pre, l["strada"]); pg.fill("#%s-numar" % pre, l["numar"])


def _randuri(pg):
    return pg.locator("#mount .grila-campuri-compacta").count()


def test_noop_lista_nefiltrata_si_sha256(et_env):
    """No-op: lista trimisa = lista randata (nefiltrata, 2 randuri complete) si XML-ul e IDENTIC cu al corpului
    canonical. Daca frontendul re-introduce filtrarea / reordoneaza / schimba tipuri -> corp != CANONICAL -> rosu."""
    pg = et_env["make_page"](); pg.click("#et-plus-bun")
    _fill_rand(pg, 0, FILL["bunuri"][0]); _fill_rand(pg, 1, FILL["bunuri"][1]); _fill_restul(pg, FILL)
    pg.click("#et-genereaza"); pg.wait_for_timeout(400)
    corp = et_env["posted"][-1]
    assert len(corp["bunuri"]) == 2, "lista trimisa nu are 2 randuri (filtrare?): %r" % corp["bunuri"]
    assert corp == CANONICAL, "corpul POST difera de canonical (filtrare/reordonare/tip): %r" % corp
    h_corp = hashlib.sha256(E.xml_notificare(CUI, corp).encode("utf-8")).hexdigest()
    h_can = hashlib.sha256(E.xml_notificare(CUI, CANONICAL).encode("utf-8")).hexdigest()
    assert h_corp == h_can, "sha256 XML difera de canonical (no-op spart): %s != %s" % (h_corp, h_can)
    pg.close()


def test_rand_adaugat(et_env):
    pg = et_env["make_page"]()
    assert _randuri(pg) == 1
    pg.click("#et-plus-bun"); pg.click("#et-plus-bun")
    assert _randuri(pg) == 3, "adaugarea de randuri nu re-randeaza lista din model"
    pg.close()


def test_rand_sters_din_mijloc_pastreaza_valori_si_reindexeaza(et_env):
    pg = et_env["make_page"]()
    pg.click("#et-plus-bun"); pg.click("#et-plus-bun")   # b0,b1,b2
    pg.fill("#b0-denumire", "ALFA"); pg.fill("#b1-denumire", "BETA"); pg.fill("#b2-denumire", "GAMA")
    pg.click('.b-sterge[data-bun="1"]'); pg.wait_for_timeout(150)   # sterge MIJLOCUL
    assert _randuri(pg) == 2, "stergerea nu a redus lista (re-randare integrala?)"
    assert pg.input_value("#b0-denumire") == "ALFA", "valoarea b0 s-a pierdut la re-randare"
    assert pg.input_value("#b1-denumire") == "GAMA", "b1 dupa stergere trebuie sa fie fostul b2 (reindexat), cu valoarea pastrata"
    assert pg.locator("#b2-denumire").count() == 0, "a ramas un al treilea rand"
    pg.close()


def test_doua_randuri_cu_erori_simultan(et_env):
    pg = et_env["make_page"](); pg.click("#et-plus-bun")
    _fill_rand(pg, 0, FILL["bunuri"][0]); _fill_restul(pg, FILL)
    # b1: cod_tarifar + denumire GOALE, restul completat
    pg.select_option("#b1-cod_scop", "201"); pg.fill("#b1-cantitate", "2"); pg.fill("#b1-um", "KGM")
    pg.fill("#b1-greutate_neta", "3"); pg.fill("#b1-greutate_bruta", "4"); pg.fill("#b1-valoare_fara_tva", "50")
    pg.click("#et-genereaza"); pg.wait_for_timeout(400)
    assert pg.locator('.msg-eroare[data-camp="b1-cod_tarifar"]').count() == 1, "eroarea nu e langa b1-cod_tarifar"
    assert pg.locator('.msg-eroare[data-camp="b1-denumire"]').count() == 1, "eroarea nu e langa b1-denumire"
    assert pg.locator('#mount .msg-eroare[data-camp^="b0-"]').count() == 0, "rand complet b0 are erori false"
    pg.close()


def test_revalidare_dupa_corectarea_unuia_singur(et_env):
    pg = et_env["make_page"](); pg.click("#et-plus-bun")
    _fill_rand(pg, 0, FILL["bunuri"][0]); _fill_restul(pg, FILL)
    pg.select_option("#b1-cod_scop", "201"); pg.fill("#b1-cantitate", "2"); pg.fill("#b1-um", "KGM")
    pg.fill("#b1-greutate_neta", "3"); pg.fill("#b1-greutate_bruta", "4"); pg.fill("#b1-valoare_fara_tva", "50")
    pg.click("#et-genereaza"); pg.wait_for_timeout(400)
    assert pg.locator('.msg-eroare[data-camp="b1-cod_tarifar"]').count() == 1
    assert pg.locator('.msg-eroare[data-camp="b1-denumire"]').count() == 1
    pg.fill("#b1-cod_tarifar", "55554444")   # corectez DOAR cod_tarifar
    pg.click("#et-genereaza"); pg.wait_for_timeout(400)
    assert pg.locator('.msg-eroare[data-camp="b1-cod_tarifar"]').count() == 0, "eroarea campului corectat nu a fost curatata"
    assert pg.locator('.msg-eroare[data-camp="b1-denumire"]').count() == 1, "eroarea campului inca lipsa a disparut gresit"
    pg.close()


def test_rand_incomplet_in_mijloc_nu_dispare(et_env):
    """DEFECTUL reparat la 3a: rand incomplet in mijloc NU se filtreaza tacit; se trimit toate randurile si eroarea
    apare la randul REAL. Mutatie: reintroducerea filtrarii in construiesteCorp face aceasta asertie ROSIE."""
    pg = et_env["make_page"](); pg.click("#et-plus-bun"); pg.click("#et-plus-bun")   # b0,b1,b2
    _fill_rand(pg, 0, FILL["bunuri"][0]); _fill_rand(pg, 2, FILL["bunuri"][1]); _fill_restul(pg, FILL)
    # b1 = mijloc INCOMPLET: cod_tarifar SI denumire goale (exact randul pe care filtrul vechi il arunca tacit)
    pg.select_option("#b1-cod_scop", "301"); pg.fill("#b1-cantitate", "1")
    pg.fill("#b1-um", "H87"); pg.fill("#b1-greutate_neta", "1"); pg.fill("#b1-greutate_bruta", "1"); pg.fill("#b1-valoare_fara_tva", "1")
    pg.click("#et-genereaza"); pg.wait_for_timeout(400)
    corp = et_env["posted"][-1]
    assert len(corp["bunuri"]) == 3, "randul incomplet din mijloc a disparut tacit (filtrare reintrodusa?): %r" % corp["bunuri"]
    assert corp["bunuri"][1]["denumire"] == "" and corp["bunuri"][1]["cod_tarifar"] == "", "randul din mijloc nu mai e pe pozitia 1 (reordonare/filtrare?)"
    assert pg.locator('.msg-eroare[data-camp="b1-denumire"]').count() == 1, "eroarea nu e la randul REAL din mijloc (b1)"
    pg.close()
