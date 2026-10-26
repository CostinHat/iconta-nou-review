# -*- coding: utf-8 -*-
"""[lotul 10, comanda Costin 10.2 pct.3, deficiența 433] „la F5, după «Contabilizează statul», formularul «Ocupație COR · Ionescu Vasile»
se deschide singur, gol, deși Ionescu are COR. Nimic nu se deschide fără să fie ales.”

CAUZA (măsurată, nu presupusă): în statul de plată, butonul „Adeverință” purta `data-cor="<codul COR>"` (adăugat la deficiența 412, ca să
precompleteze funcția din adeverință), iar formularul COR se leagă pe ORICE element cu `[data-cor]` (`corp.querySelectorAll("[data-cor]")`).
Un clic pe „Adeverință” pornea DOI ascultători: adeverința și formularul COR — cu `dataset.cor` = codul COR luat drept id de salariat și
`dataset.val` lipsă, deci formularul se deschidea GOL (iar „Salvează” ar fi scris pe salariatul cu id-ul egal cu codul COR). Formularul
rămânea deschis pe statul de plată și se vedea la întoarcerea din adeverință — de exemplu după „Contabilizează statul”.

CLASA: un element care poartă DOUĂ atribute-declanșator (`data-x` legat la clic cu `querySelectorAll("[data-x]").forEach(...)`) în același
ecran: clicul pe el deschide și ce n-a fost ales. Plus deschiderile programatice (`.click()` dat de cod): fiecare e în lista de mai jos,
cu motivul pentru care e alegerea omului; una nouă pică testul până primește motivul.

Temei: N/A — UI (comanda 10.2 pct.3: „Nimic nu se deschide fără să fie ales.”).

Ce păzește:
  1. scanerul de coliziuni pe TOT `static/js` (domeniul: funcția de nivel superior în care stau șablonul și legarea) — gol;
  2. scanerul prinde coliziunea pe un fragment sintetic (anti-vacuu) și pe forma veche a butonului „Adeverință”;
  3. lista închisă a clicurilor programatice;
  4. în Chromium, pe ecranul real (`firme.ecranSalariati`): „Adeverință” și „Contabilizează statul” nu deschid formularul COR; butonul
     „COR ✓” îl deschide precompletat cu codul salariatului.
MUTAȚIE: `data-adev-cor` pus înapoi `data-cor` pe butonul „Adeverință” -> 1 (coliziunea) și 4 (formularul se deschide gol) pică.
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
from urllib.parse import urlparse

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COR = "241107"   # auditor financiar — în public.cor_ocupatii (ca în test_412_cim_salariat / test_411_net_cu_cm)

_DECLANSATOR = re.compile(r"""querySelectorAll\(\s*(["'`])\[data-([\w-]+)\]\1\s*\)\s*\.forEach\(""")
_ETICHETA = re.compile(r"<(button|a|div|span|tr|td|li|input|select|label|details|summary)\b")
_FUNCTIE = re.compile(r"^(?:export )?(?:async )?function ", re.M)


def _fisiere():
    out = []
    for f in sorted(glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True)):
        rel = os.path.relpath(f, _RAD)
        # copiile de lucru (`x.bak.js`) și bibliotecile străine (`vendor/`) nu sunt ecranele aplicației
        if {"bak"} & set(os.path.basename(f).split(".")[1:-1]) or {"vendor"} & set(rel.split(os.sep)):
            continue
        out.append((rel, io.open(f, encoding="utf-8").read()))
    return out


def _capat_eticheta(txt, i):
    """Sfârșitul etichetei HTML din șablon: primul `>` din afara unei interpolări `${…}`."""
    d, j = 0, i
    while j < len(txt):
        if txt.startswith("${", j):
            d += 1
            j += 2
            continue
        if txt[j] == "}" and d:
            d -= 1
        elif txt[j] == ">" and d == 0:
            return j
        j += 1
    return j


def coliziuni(fisiere):
    """[(fișier:linie, [atribute])] — elementele care poartă cel puțin două atribute-declanșator ale aceleiași funcții de nivel superior.
    Întoarce și numărul de declanșatoare văzute (anti-vacuu)."""
    gasite, vazute = [], 0
    for nume, txt in fisiere:
        inceputuri = [m.start() for m in _FUNCTIE.finditer(txt)] + [len(txt)]

        def functia(i, inceputuri=inceputuri):
            k = 0
            for j, s0 in enumerate(inceputuri):
                if s0 <= i:
                    k = j
            return k
        decl = {}
        for m in _DECLANSATOR.finditer(txt):
            decl.setdefault(functia(m.start()), set()).add(m.group(2))
            vazute += 1
        for m in _ETICHETA.finditer(txt):
            atr = set(re.findall(r"\bdata-([\w-]+)=", txt[m.start():_capat_eticheta(txt, m.end())]))
            ambele = atr & decl.get(functia(m.start()), set())
            if len(ambele) > 1:
                gasite.append(("%s:%d" % (nume, txt[:m.start()].count("\n") + 1), sorted(ambele)))
    return gasite, vazute


def test_niciun_element_nu_deschide_doua_lucruri():
    gasite, vazute = coliziuni(_fisiere())
    assert vazute >= 60, "ANTI-VACUU: numai %d legări `[data-x]` găsite în static/js" % vazute
    # comanda 10.2 pct.3: „Nimic nu se deschide fără să fie ales.” — un clic pe un element nu pornește ascultătorul altui buton
    assert gasite == [], "elemente cu două atribute-declanșator (clicul deschide și ce n-a fost ales): %s" % gasite


_SABLON = '''
async function ecranProba(corp, nav, t) {
  corp.innerHTML = `<button data-adev="${s.id}" data-nume="${esc(s.nume)}" ATRIBUT="${esc(s.cor || "")}">Adeverință</button>
    <button data-cor="${s.id}" data-val="${esc(s.cor || "")}">COR</button>`;
  corp.querySelectorAll("[data-adev]").forEach((b) => b.addEventListener("click", () => nav.mergi("Adeverință")));
  corp.querySelectorAll("[data-cor]").forEach((b) => b.addEventListener("click", () => {}));
}
'''


@pytest.mark.parametrize("atribut, asteptat", [
    ("data-cor", [["adev", "cor"]]),        # forma de dinainte de 10.2 (deficiența 433)
    ("data-adev-cor", []),                  # forma reparată
])
def test_scanerul_prinde_coliziunea(atribut, asteptat):
    gasite, _ = coliziuni([("proba.js", _SABLON.replace("ATRIBUT", atribut))])
    assert [g[1] for g in gasite] == asteptat, gasite   # „Nimic nu se deschide fără să fie ales.”


def test_un_declansator_din_alt_ecran_nu_e_coliziune():
    """`data-val` e declanșator în Registrul jurnal (Validează), dar pe statul de plată e numai valoarea curentă a butonului: domeniul e
    funcția ecranului, nu fișierul (altfel scanerul ar raporta fals cinci butoane ale statului)."""
    sursa = _SABLON.replace("ATRIBUT", "data-adev-cor") + '''
async function ecranAlt(corp) {
  corp.querySelectorAll("[data-val]").forEach((b) => b.addEventListener("click", () => {}));
}
'''
    assert coliziuni([("proba.js", sursa)])[0] == []


# ── clicurile programatice: fiecare e alegerea omului, cu motivul ────────────────────────────────────────────────────────────────────
CLICURI_PROGRAMATICE = {
    "static/js/api.js": (1, "descărcarea fișierului cerut de om (ancora temporară a descărcării)"),
    "static/js/navigator.js": (1, "notificarea aleasă de om (clopoțel / e-mail): se apasă elementul pe care îl numește"),
    "static/js/ecrane/inceput.js": (2, "cardul „Suport” ales de om deschide raportarea și fila „Cerere import”"),
    "static/js/ecrane/login.js": (1, "Enter în câmpul de e-mail = apăsarea butonului de alături"),
    "static/js/ecrane/portal.js": (2, "„Fotografiază” / „Încarcă” deschid alegerea fișierului (input ascuns)"),
    "static/js/ecrane/raporteaza.js": (2, "„Adaugă poză” / „Adaugă fișier” deschid alegerea fișierului (input ascuns)"),
    "static/js/ecrane/migrare.js": (1, "descărcarea fișierului cerut de om"),
    "static/js/ecrane/etransport_ecran.js": (1, "descărcarea XML-ului cerut de om"),
    "static/js/ecrane/firme.js": (2, "descărcarea cerută de om; „Scanează cod de bare” deschide alegerea imaginii (input ascuns)"),
    "static/js/ecrane/validat.js": (1, "„Respinge nota” ales în caseta de confirmare apasă butonul de respingere al notei"),
}


def test_clicurile_programatice_sunt_numai_cele_alese_de_om():
    numarate = {}
    for nume, txt in _fisiere():
        n = len(re.findall(r"\.click\(\)", txt))
        if n:
            numarate[nume] = n
    asteptat = {k: v[0] for k, v in CLICURI_PROGRAMATICE.items()}
    # „Nimic nu se deschide fără să fie ales.” — un `.click()` nou, dat de cod, intră în listă numai cu motivul alegerii omului
    assert numarate == asteptat, "clicuri programatice schimbate: găsite %s, în listă %s" % (numarate, asteptat)


# ── în Chromium, pe ecranul real ─────────────────────────────────────────────────────────────────────────────────────────────────────
MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  // [lotul 13, 673] navigatorul de probă desenează ferestrele deschise (fereastra salariatului, fereastra „Salariu”) una peste alta
  const nav = { deschide(titlu, f) { const d = document.createElement('div'); d.className = 'fer-proba'; document.body.appendChild(d); f(d, nav); },
                inapoi() { const f = [...document.querySelectorAll('.fer-proba')].pop(); if (f) f.remove(); }, inapoiPas(){}, mergi(){}, setInapoi(){} };
  await m.ecranSalariati(document.getElementById('mount'), nav, { id: 1 });
  return true;
}"""

STAT = {"stat": [{"id": 7, "nume": "IONESCU VASILE", "cor": COR, "salariu_baza": 5000, "brut": 5000, "cas": 1250, "cass": 500,
                  "impozit_salariu": 325, "net": 2925, "cost": 5112.5, "elemente": [], "compozitie": []}]}
PROPUNERE = {"document_ref": "Stat de plată", "note": [{"debit": "641", "credit": "421", "suma": 5000}], "total": 5000,
             "divergente": [], "neincheiata": None, "deja_contata": False, "net_fluturasi": 2925, "nr_salariati": 1}


def _handler(route, request):
    cale = urlparse(request.url).path
    corp = STAT if cale == "/tenants/1/stat-plata" else PROPUNERE if cale.endswith("/salarii-contare/propunere") else {}
    route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    pg = br.new_page()
    pg.route("**/tenants/**", _handler)
    pg.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield pg
    finally:
        br.close()
        pw.stop()
        srv.shutdown()


def _montat(pg):
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
    pg.wait_for_selector("#mount .sp-deschide", timeout=15000)
    # [lotul 13, 677] butoanele salariatului stau în fereastra lui, deschisă din rândul statului
    pg.click("#mount .sp-deschide")
    pg.wait_for_selector(".fer-proba [data-adev]", timeout=15000)


def test_adeverinta_si_contabilizarea_nu_deschid_formularul_cor(pagina):
    pg = pagina
    _montat(pg)
    pg.click(".fer-proba [data-adev]")
    pg.wait_for_selector("#ad-gen", timeout=10000)
    pg.click("#sp-contare")
    pg.wait_for_selector("#sp-contare-scrie", timeout=10000)
    # „formularul «Ocupație COR · Ionescu Vasile» se deschide singur, gol […] Nimic nu se deschide fără să fie ales.”
    assert pg.locator("#cor-edit-cor").count() == 0


def test_formularul_cor_ales_vine_cu_codul_salariatului(pagina):
    pg = pagina
    _montat(pg)
    pg.click(".fer-proba [data-cor]")
    pg.wait_for_selector("#cor-edit-cor-cauta", timeout=5000)
    # „deși Ionescu are COR”: deschis cu „COR ✓”, formularul arată codul lui, nu un câmp gol
    assert pg.input_value("#cor-edit-cor") == COR and pg.input_value("#cor-edit-cor-cauta").startswith(COR)
    # formularul e al salariatului ales (titlul ferestrei lui)
    assert pg.locator(".fer-proba h2", has_text="Ocupație COR").last.inner_text().strip() == "Ocupație COR · IONESCU VASILE"
