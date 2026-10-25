# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 642, partea de formular — comanda Costin 12.2 pct.19, verbatim: „Retest 24.10 pe formularul din invitație:
CUI-ul invalid e refuzat acum la «Creează cont». Rămân: mesajul de refuz apare de două ori; fereastra formularului iese din ecran sus și
jos, «Creează cont» abia se vede.”]

Formularul „Înregistrează cabinetul tău” (`login.js`, drumul invitației), desenat de `login.js` + `api.js` + `stil.css` REALE, în Chromium;
serverul e simulat (invitația validă, refuzul `/auth/register` cu textul real al lui `tenant_provisioning.MESAJ_CUI_CONTROL`).

CAUZELE (măsurate aici, pe codul de dinainte, la 1280×720):
  1. „de două ori”: verdictul „Verifică la ANAF” (sub CUI) și refuzul de la „Creează cont” (`#reg-eroare`) aveau același text; la un
     refuz cu mai multe câmpuri, textul întreg în `#reg-eroare` + fiecare eroare lângă câmpul ei + caseta „NU s-a salvat.” + plasa
     „refuz nevăzut” (fraza pe mai multe rânduri nu se regăsea în pagină, scrisă pe un rând) — de 4 ori;
  2. „iese din ecran”: formularul avea 967 px într-o fereastră de 672 (derula el însuși; „Creează cont” la 716–752 px, sub marginea de
     jos), iar caseta „NU s-a salvat.” se punea în afara ferestrei (după `.acces-modal`, în stratul centrat), iar eroarea CUI-ului,
     pusă între câmp și „Verifică la ANAF”, strângea formularul pe o coloană de 2.744 px.

Ce păzește (1280×720 și 1366×768; telefonul 390×844 numai pentru bara de acțiune):
  - refuzul cu un singur motiv (CUI-ul greșit) apare O DATĂ, și după „Verifică la ANAF”; refuzul cu mai multe câmpuri: fiecare eroare
    lângă câmpul ei și în „NU s-a salvat.” (DS cap.6 v2.99, 440), fără bannerul „refuz nevăzut”;
  - nimic nu iese din fereastra formularului; pe laptop formularul încape fără derulare, cu refuzul arătat; „Creează cont” și refuzul
    sunt întregi în ecran (pe telefon, bara de jos rămâne în ecran cât derulezi);
  - eroarea CUI-ului stă sub rândul câmp + „Verifică la ANAF”, nu între ele.

Temei: N/A — regulă de UI (CLAUDE.md §9; DS cap.6 „Un mesaj, o singură dată”).
"""
import json
import urllib.parse

import pytest

from core import tenant_provisioning as tp
from core.test_lot11_m_ferestre_import import browser  # noqa: F401  (fixture-ul `browser`: serverul static + Chromium)

MESAJ = tp.MESAJ_CUI_CONTROL % "12345678"
PAROLA_SCURTA = "Parola: cel puțin 10 caractere."
PAGINA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><div id="app"></div><script type="module">
location.hash = "#invitatie=TOK642";
const m = await import("/static/js/ecrane/login.js"); m.ecranLogin(document.getElementById("app")); window._gata = true;
</script></body></html>"""

MASOARA = """(m) => {
  const md = document.querySelector('#acces-modal');
  const R = (s) => { const e = document.querySelector(s); if (!e || e.hidden || !e.offsetParent) return null; const r = e.getBoundingClientRect();
                     return {top: r.top, bottom: r.bottom}; };
  const t = document.body.innerText.replace(/\\s+/g, ' ');
  const cate = (k) => { let n = 0, i = 0; while ((i = t.indexOf(k, i)) >= 0) { n++; i++; } return n; };
  const rand = document.querySelector('#reg-cui').parentElement.getBoundingClientRect();
  const ercui = document.querySelector('.msg-eroare[data-camp="reg-cui"]');
  return {modal: R('#acces-modal'), buton: R('#reg-buton'), eroare: R('#reg-eroare'), inalt: innerHeight,
          deruleaza: md.scrollHeight > md.clientHeight + 1, in_afara: document.querySelector('.acces-overlay').children.length,
          banner: !!document.querySelector('#refuz-nevazut'), cui_mesaj: cate(m[0].slice(0, 50)), parola_mesaj: cate(m[1]),
          eroare_cui_sub_rand: ercui ? ercui.getBoundingClientRect().top >= rand.bottom - 1 : null};
}"""


def _deschide(browser, lat, inalt, detaliu):  # noqa: F811
    b, port = browser
    pg = b.new_page(viewport={"width": lat, "height": inalt})

    def raspuns(route):
        u = urllib.parse.urlsplit(route.request.url).path   # ruta după cale (începutul ei), nu după un șir oriunde în adresă
        if u.startswith("/static/"):
            return route.continue_()
        if u.startswith("/public/invitatie/"):
            return route.fulfill(status=200, content_type="application/json", body=json.dumps({"valida": True, "email": "proba642@exemplu.ro"}))
        if u.startswith("/public/verifica-cui/"):   # răspunsul rutei publice la un CUI greșit (core/test_lot11_a459_cui.py)
            return route.fulfill(status=200, content_type="application/json",
                                 body=json.dumps({"gasit": False, "cui_invalid": True, "cui": "12345678", "camp": "cui", "motiv": MESAJ}))
        if u.startswith("/auth/register"):
            return route.fulfill(status=400, content_type="application/json", body=json.dumps({"detail": detaliu}))
        return route.fulfill(status=200, content_type="application/json", body="{}")
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/public/", "/auth/", "/api/"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_selector("#pr-continua", timeout=10000)
    pg.click("#pr-continua")
    pg.wait_for_selector("#reg-buton", timeout=10000)
    pg.fill("#reg-cui", "12345678")
    pg.fill("#reg-cabinet", "Cabinet Test Inregistrare")
    pg.fill("#reg-parola", "Parola.642-abc")
    pg.fill("#reg-parola2", "Parola.642-abc")
    pg.check("#reg-termeni")
    return pg


def _in_ecran(o, cheie):
    r = o[cheie]
    return r is not None and r["top"] >= 0 and r["bottom"] <= o["inalt"]


@pytest.mark.parametrize("lat,inalt", [(1280, 720), (1366, 768)])
@pytest.mark.parametrize("verifica_intai", [False, True], ids=["direct", "dupa_verifica_la_anaf"])
def test_def_642_refuzul_cui_apare_o_data_iar_formularul_incape(browser, lat, inalt, verifica_intai):  # noqa: F811
    """CUI-ul 12345678 (cifra de control greșită) -> „Creează cont”: refuzul o dată, formularul întreg în ecran, fără derulare, cu
    „Creează cont” și refuzul vizibile. ROȘU înainte: după „Verifică la ANAF” textul apare de 2 ori; formularul derulează (967 px în
    672), „Creează cont” sub marginea ecranului. MUTAȚIA: `catch` cu `arataEroare(e.mesaj …)` la loc, fără ștergerea verdictului -> pică."""
    pg = _deschide(browser, lat, inalt, MESAJ)
    try:
        if verifica_intai:
            pg.click("#reg-cui-verifica")
            pg.wait_for_function("() => document.querySelector('#reg-cui-info').textContent.length > 5", timeout=5000)
        pg.click("#reg-buton")
        pg.wait_for_selector("#reg-eroare:not([hidden])", timeout=5000)
        pg.wait_for_timeout(900)   # după plasa „refuz nevăzut” (700 ms)
        o = pg.evaluate(MASOARA, [MESAJ, PAROLA_SCURTA])
    finally:
        pg.close()
    assert o["cui_mesaj"] == 1, o                        # „mesajul de refuz apare de două ori”
    assert not o["banner"] and o["in_afara"] == 1, o      # nimic în afara ferestrei
    assert not o["deruleaza"], o                         # „fereastra formularului iese din ecran sus și jos”
    assert _in_ecran(o, "modal") and _in_ecran(o, "buton") and _in_ecran(o, "eroare"), o   # „«Creează cont» abia se vede”


@pytest.mark.parametrize("lat,inalt", [(1280, 720), (1366, 768), (390, 844)])
def test_def_642_refuzul_cu_mai_multe_campuri_fiecare_o_data_langa_camp(browser, lat, inalt):  # noqa: F811
    """Refuzul cu două câmpuri (CUI + parola): fiecare eroare lângă câmpul ei și în „NU s-a salvat.” (de 2 ori, DS cap.6 v2.99), fără
    textul întreg dedesubt și fără bannerul „refuz nevăzut”; caseta „NU s-a salvat.” în fereastră; eroarea CUI-ului sub rândul cu
    „Verifică la ANAF”; „Creează cont” în ecran. ROȘU înainte: de 4 ori, caseta în afara ferestrei, formularul strâns pe 2.744 px.
    MUTAȚIA: plasa „refuz nevăzut” fără `erori_campuri` (forma veche din api.js) -> bannerul apare -> pică."""
    det = {"mesaj": "Contul nu s-a creat:\n— %s\n— %s" % (MESAJ, PAROLA_SCURTA),
           "erori_campuri": [{"camp": "reg-cui", "mesaj": MESAJ}, {"camp": "reg-parola", "mesaj": PAROLA_SCURTA}]}
    pg = _deschide(browser, lat, inalt, det)
    try:
        pg.click("#reg-buton")
        pg.wait_for_selector('.msg-eroare[data-camp="reg-parola"]', timeout=5000)
        pg.wait_for_timeout(900)
        o = pg.evaluate(MASOARA, [MESAJ, PAROLA_SCURTA])
    finally:
        pg.close()
    assert o["cui_mesaj"] == 2 and o["parola_mesaj"] == 2, o
    assert not o["banner"] and o["in_afara"] == 1, o
    assert o["eroare"] is None, o                        # textul întreg nu se mai repetă dedesubt
    assert o["eroare_cui_sub_rand"] is True, o
    assert _in_ecran(o, "buton"), o


#: pagina-sondă a clasei: un formular oarecare (nu înregistrarea), cu `api.js` real; butonul trimite, ecranul arată refuzul cum vrea
PAGINA_CLASA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><form id="f" onsubmit="return false"><label class="camp"><span class="camp-eticheta">Cota TVA</span><input id="x-cota" class="camp-input"></label>
<label class="camp"><span class="camp-eticheta">Cantitate</span><input id="x-cant" class="camp-input"></label>
<div class="dec-bara"><button id="x-salveaza" class="buton-primar">Salvează</button></div><div id="x-msg"></div></form>
<script type="module">
const a = await import("/static/js/api.js");
document.getElementById("x-salveaza").addEventListener("click", async () => {
  try { await a.api.post("/proba/" + window._caz, {}); }
  catch (e) { if (window._caz === "campuri") a.arataRefuzul(document.getElementById("f"), e, null);
              else if (window._caz === "un_rand") document.getElementById("x-msg").textContent = e.mesaj; /* „tacut”: nu arată nimic */ }
});
window._gata = true;
</script></body></html>"""


@pytest.mark.parametrize("caz,banner", [("campuri", False), ("un_rand", False), ("tacut", True)])
def test_def_642_clasa_refuzul_aratat_nu_mai_vine_si_in_fereastra_am_inteles(browser, caz, banner):  # noqa: F811
    """CLASA lui 642 (și „Emite factură”, semnalată de pachetul fact2): plasa `api._refuzNevazut` socotea nevăzut un refuz cu mai multe
    erori de câmp arătate lângă câmpuri (fraza lui întreagă nu era pe ecran) și unul pe mai multe rânduri scris pe un rând, deci îl
    repeta în fereastra „Am înțeles” (`#refuz-nevazut`). Pe orice formular: `campuri` (erorile lângă câmpuri + „NU s-a salvat.”) și
    `un_rand` (textul întreg, pe un rând) -> fără fereastră; `tacut` (ecranul nu arată nimic) -> fereastra vine, plasa rămâne.
    MUTAȚIA: forma veche a verificării (`innerText.indexOf(m)`) -> `campuri` și `un_rand` pică."""
    b, port = browser
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    det = {"mesaj": "Factura nu s-a salvat:\n— Cota TVA nu e în listă.\n— Cantitatea trebuie să fie pozitivă.",
           "erori_campuri": [{"camp": "x-cota", "mesaj": "Cota TVA nu e în listă."}, {"camp": "x-cant", "mesaj": "Cantitatea trebuie să fie pozitivă."}]}
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA_CLASA))
    if caz == "tacut":   # refuzul fără câmpuri pe care ecranul nu-l arată nicăieri: plasa trebuie să-l arate
        det = "Factura nu s-a salvat: seria e închisă."
    pg.route("**/proba/**", lambda r: r.fulfill(status=400, content_type="application/json", body=json.dumps({"detail": det})))
    try:
        pg.goto("http://127.0.0.1:%d/harness.html" % port)
        pg.wait_for_function("() => window._gata === true", timeout=10000)
        pg.evaluate("(c) => { window._caz = c; }", caz)
        pg.click("#x-salveaza")
        pg.wait_for_timeout(1000)    # după plasa „refuz nevăzut” (700 ms)
        are = bool(pg.query_selector("#refuz-nevazut"))
        campuri = pg.locator(".msg-eroare[data-camp]").count()
    finally:
        pg.close()
    assert are is banner, (caz, are)
    if caz == "campuri":
        assert campuri == 2, campuri
