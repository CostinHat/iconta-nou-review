# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 459.1, comanda Costin 12.2 pct.5 — clasa „datele aduse de la ANAF pentru un CUI rămân după schimbarea CUI-ului”]
Verbatim: „la schimbarea CUI-ului denumirea adusă de la CUI-ul anterior (DANTE INTERNATIONAL SA) rămâne completată.”

Pachetul ui2 a scris implementarea unică (`static/js/ecrane/date_anaf.js`, `legaDateAnaf`) și a legat-o în „Adaugă firmă”, NIR și casă
(`firme.js`). Integrarea I1 a legat-o în celelalte trei formulare în care ANAF completează câmpuri din CUI:

  * Emite factură (`emitere_ecran.js`): denumirea, adresa, localitatea, județul clientului (și ce aduce VIES pentru un client din UE);
  * Factură primită introdusă de mână (`facturi_ecran.js`): furnizorul și linia de sub CUI;
  * Înregistrarea cabinetului (`login.js`): denumirea cabinetului și linia de sub CUI.

Comportamentul păstrat, verificat aici: „Verifică” (cerut de om) pune datele ANAF și peste ce era scris; ce a scris / corectat omul după
aceea rămâne la schimbarea CUI-ului (F188); răspunsul verificării de sub CUI pleacă la tastarea altui CUI (304 / C166 / 642).

Ecranele REALE, în Chromium, cu rutele simulate (harness-ul `core/test_lot12_ui2_ecrane.py`). MUTAȚIE: `campCui.addEventListener("input", …)`
scos din `date_anaf.js` -> pică toate trei (denumirea CUI-ului vechi rămâne). Temei: N/A — regulă de interfață (CLAUDE.md §9 „Nimic
precompletat sau afișat care poate induce în eroare contabilul”)."""
import json
import urllib.parse

from core.test_lot12_ui2_ecrane import _pagina, browser  # noqa: F401 — fixtura `browser` (serverul static + Chromium)

DANTE = {"gasit": True, "denumire": "DANTE INTERNATIONAL SA", "adresa": "Str. Industriilor nr. 1", "localitate": "Sector 2 Mun. Bucureşti",
         "judet": "B", "platitor_tva": True, "cod_caen": "6920"}


def _verifica_cui(_m, cale, _q, _b):
    cui = urllib.parse.unquote(cale.rsplit("/", 1)[-1])
    return DANTE if cui == "14399840" else {"gasit": False}


_VAL = "(s) => document.querySelector(s).value"


def test_def_459_1_emiterea_facturii_datele_clientului_tin_de_cui(browser):  # noqa: F811
    pg, erori = _pagina(browser, {"/verifica-cui": _verifica_cui, "/facturi/numerotare": {
        "serie": None, "urmator_numar": 1, "configurata": True, "lipsuri_firma": [], "cote_permise": [21, 11, 0]},
        "/stocuri/articole": {"articole": []}})
    try:
        pg.evaluate("""async () => { const m = await import('/static/js/ecrane/emitere_ecran.js');
          document.body.insertAdjacentHTML('beforeend', '<div id="mount"></div>');
          await m.randeazaEmitere(document.getElementById('mount'), { inapoi(){}, setInapoi(){}, mergi(){} }, 1, {}); }""")
        pg.wait_for_selector("#em-cui", timeout=10000)
        pg.fill("#em-nume", "Client scris de mână")
        pg.fill("#em-cui", "14399840")
        pg.click("#em-verifica")
        pg.wait_for_function("() => document.querySelector('#em-nume').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        dupa_verifica = [pg.evaluate(_VAL, s) for s in ("#em-nume", "#em-adresa", "#em-oras", "#em-judet")]
        stare = pg.inner_text("#em-cui-stare")
        pg.fill("#em-cui", "1439984")                      # alt CUI (o cifră scoasă)
        dupa_schimbare = [pg.evaluate(_VAL, s) for s in ("#em-nume", "#em-adresa", "#em-oras", "#em-judet")]
        stare_dupa = pg.inner_text("#em-cui-stare")
        pg.fill("#em-cui", "14399840")
        pg.click("#em-verifica")
        pg.wait_for_function("() => document.querySelector('#em-nume').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        pg.fill("#em-adresa", "Adresa corectată de mine")  # scrisă de om după ANAF
        pg.fill("#em-cui", "18547290")
        om = [pg.evaluate(_VAL, s) for s in ("#em-nume", "#em-adresa")]
    finally:
        pg.close()
    assert not erori, erori
    # „Verifică” e cerut de om: datele ANAF intră și peste denumirea scrisă înainte (comportamentul de dinainte, C61)
    assert dupa_verifica == ["DANTE INTERNATIONAL SA", "Str. Industriilor nr. 1", "Sector 2 Mun. Bucureşti", "B"], dupa_verifica
    assert stare == "plătitor TVA", stare
    assert dupa_schimbare == ["", "", "", ""], dupa_schimbare   # datele CUI-ului vechi nu rămân lângă CUI-ul nou
    assert stare_dupa.strip() == "", stare_dupa                 # 304: răspunsul verificării de dinainte pleacă
    assert om == ["", "Adresa corectată de mine"], om           # F188: ce a scris omul rămâne


def test_def_459_1_factura_primita_de_mana_furnizorul_tine_de_cui(browser):  # noqa: F811
    pg, erori = _pagina(browser, {"/verifica-cui": _verifica_cui, "/facturi-primite": {"primite": [], "categorii_331": []}})
    try:
        pg.evaluate("""async () => { const f = await import('/static/js/ecrane/facturi_ecran.js');
          window._nav.deschide('Facturi', (c, n) => f.randeazaFacturi(c, n, 1, {})); }""")
        pg.click("#fac-primite")
        pg.wait_for_selector("#fp-manual", timeout=10000)
        pg.click("#fp-manual")
        pg.wait_for_selector("#pm-cui", timeout=10000)
        pg.fill("#pm-cui", "14399840")
        pg.click("#pm-verifica")
        pg.wait_for_function("() => document.querySelector('#pm-furnizor').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        stare = pg.inner_text("#pm-cui-stare")
        pg.fill("#pm-cui", "1439984")
        furnizor_dupa, stare_dupa = pg.evaluate(_VAL, "#pm-furnizor"), pg.inner_text("#pm-cui-stare")
        pg.fill("#pm-cui", "14399840")
        pg.click("#pm-verifica")
        pg.wait_for_function("() => document.querySelector('#pm-furnizor').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        pg.fill("#pm-furnizor", "DANTE INTERNATIONAL SA — punct de lucru")
        pg.fill("#pm-cui", "18547290")
        om = pg.evaluate(_VAL, "#pm-furnizor")
    finally:
        pg.close()
    assert not erori, erori
    assert stare == "DANTE INTERNATIONAL SA · plătitor TVA", stare
    assert furnizor_dupa == "" and stare_dupa.strip() == "", (furnizor_dupa, stare_dupa)
    assert om == "DANTE INTERNATIONAL SA — punct de lucru", om


PAGINA_LOGIN = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><div id="app"></div><script type="module">
location.hash = "#invitatie=TOK459";
const m = await import("/static/js/ecrane/login.js"); m.ecranLogin(document.getElementById("app")); window._gata = true;
</script></body></html>"""


def test_def_459_1_inregistrarea_cabinetului_denumirea_tine_de_cui(browser):  # noqa: F811
    b, port = browser
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        u = urllib.parse.urlsplit(route.request.url)
        if u.path.startswith("/static/"):
            return route.continue_()
        if u.path.startswith("/public/invitatie/"):
            corp = {"valida": True, "email": "proba459@exemplu.ro"}
        elif u.path.startswith("/public/verifica-cui/"):
            corp = _verifica_cui("GET", u.path, None, None)
        else:
            corp = {}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))
    try:
        pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA_LOGIN))
        for pref in ("/public/", "/auth/", "/api/"):
            pg.route("**%s**" % pref, raspuns)
        pg.goto("http://127.0.0.1:%d/harness.html" % port)
        pg.wait_for_selector("#pr-continua", timeout=10000)
        pg.click("#pr-continua")
        pg.wait_for_selector("#reg-cui", timeout=10000)
        pg.fill("#reg-cui", "14399840")
        pg.click("#reg-cui-verifica")
        pg.wait_for_function("() => document.querySelector('#reg-cabinet').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        info = pg.inner_text("#reg-cui-info")
        pg.fill("#reg-cui", "1439984")
        cabinet_dupa, info_dupa = pg.evaluate(_VAL, "#reg-cabinet"), pg.inner_text("#reg-cui-info")
        pg.fill("#reg-cui", "14399840")
        pg.click("#reg-cui-verifica")
        pg.wait_for_function("() => document.querySelector('#reg-cabinet').value === 'DANTE INTERNATIONAL SA'", timeout=5000)
        pg.fill("#reg-cabinet", "Cabinetul meu SRL")
        pg.fill("#reg-cui", "18547290")
        om = pg.evaluate(_VAL, "#reg-cabinet")
    finally:
        pg.close()
    assert not erori, erori
    assert info.startswith("Găsit: DANTE INTERNATIONAL SA"), info
    assert cabinet_dupa == "" and info_dupa.strip() == "", (cabinet_dupa, info_dupa)   # 642 + 459.1
    assert om == "Cabinetul meu SRL", om
