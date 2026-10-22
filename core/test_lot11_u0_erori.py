# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 440 (comanda Costin 11.1 pct.16, verbatim): „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă
câmp. Fără «motivul e mai sus». Pe toată aplicația.”

Temei: N/A — regulă de interfață (DS cap.6 v2.99, „Toate erorile deodată, fiecare cu textul ei”).

CE FACE IMPOSIBIL (codul REAL din `api.js`, în Chromium, cu un server simulat):
  1. caseta „NU s-a salvat.” cu o trimitere fără text („motivul e mai sus / mai jos”) în locul refuzului;
  2. refuzul serverului cu trei erori de câmp arătat ca o singură frază, fără câmpurile marcate — chiar pe un ecran care afișează
     numai `e.mesaj` (marcarea automată de după `catch`-ul ecranului);
  3. o eroare de câmp fără legătura pentru cititorul de ecran (`aria-invalid` + `aria-describedby` spre textul ei) și legătura rămasă
     după corectare;
  4. validarea din ecran care se oprește la primul câmp gol (`cereCompletate` le marchează pe toate).
"""
import functools
import http.server
import json
import os
import socketserver
import threading

import pytest

from core.test_emitere_randuri_dinamice import _lanseaza_chromium

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_REFUZ_3 = {"detail": {"mesaj": "Cererea nu poate fi acceptată: 3 câmpuri.", "erori_campuri": [
    {"camp": "u0-nume", "mesaj": "Numele firmei lipsește."},
    {"camp": "u0-cui", "mesaj": "CUI-ul nu are cifra de control corectă."},
    {"camp": "u0-iban", "mesaj": "IBAN-ul are 23 de caractere, nu 24."},
    {"camp": "u0-necunoscut", "mesaj": "Județul lipsește."}]}}


@pytest.fixture(scope="module")
def pg():
    from playwright.sync_api import sync_playwright
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    p = b.new_page()
    p.route("**/tenants/7/u0-salveaza", lambda r, q: r.fulfill(status=422, content_type="application/json", body=json.dumps(_REFUZ_3)))
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.add_style_tag(url="/static/stil.css")
    p.evaluate("async () => { window.U0 = await import('/static/js/api.js'); }")   # fiecare test poate rula singur
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


_FORMULAR = """
  document.body.innerHTML = `<div class="fereastra"><div class="fereastra-corp">
    <div id="u0-zona-sus"></div>
    <label class="camp"><span class="camp-eticheta">Numele firmei</span><input id="u0-nume" class="camp-input"></label>
    <label class="camp"><span class="camp-eticheta">CUI</span><input id="u0-cui" class="camp-input" aria-describedby="u0-cui-ajutor"></label>
    <span id="u0-cui-ajutor" class="camp-ajutor">fără RO</span>
    <label class="camp"><span class="camp-eticheta">IBAN</span><input id="u0-iban" class="camp-input"></label>
    <div class="bara-fixa"><div class="rand-actiuni"><button id="u0-salveaza">Salvează</button></div><div id="u0-mesaj"></div></div>
  </div></div>`;
"""


def _clic(pg, sel):
    pg.click(sel)
    pg.wait_for_timeout(150)


def test_refuzul_de_formular_departe_de_buton_apare_cu_textul_lui_nu_motivul_e_mai_sus(pg):
    """1. Refuz de formular scris în zona de SUS, butonul jos: caseta spune textul, nu „motivul e mai sus”.
    MUTAȚIE: `a.textContent = (mesaj.textContent || "").trim();` -> „motivul e mai sus” -> pică."""
    pg.evaluate("async () => { %s }" % _FORMULAR)
    pg.evaluate("""() => document.getElementById('u0-salveaza').addEventListener('click', () =>
        window.U0.arataMesaj(document.getElementById('u0-zona-sus'), 'Perioada 09/2026 e încheiată: nu se mai scrie în ea.', 'eroare'))""")
    _clic(pg, "#u0-salveaza")
    r = pg.evaluate("""() => [...document.querySelectorAll('.refuz-salvare li')].map((li) => [li.innerText, li.hidden])""")
    assert pg.inner_text(".refuz-salvare b") == "NU s-a salvat."
    assert r == [["Perioada 09/2026 e încheiată: nu se mai scrie în ea.", False]], r   # 440: „fiecare cu textul ei”
    assert "motivul e" not in pg.inner_text(".refuz-salvare"), r                       # 440: „Fără «motivul e mai sus»”


def test_refuzul_de_formular_lipit_de_buton_nu_se_copiaza_a_doua_oara(pg):
    """1b. Zona refuzului e chiar lângă buton (în bara fixă): textul nu se copiază lângă el (DS cap.6: același text nu stă de două ori
    lipit). MUTAȚIE: `if (_langaButon(mesaj, b)) li.hidden = true;` scos -> textul de două ori în vedere -> pică."""
    pg.evaluate("async () => { %s }" % _FORMULAR)
    pg.evaluate("""() => document.getElementById('u0-salveaza').addEventListener('click', () =>
        window.U0.arataMesaj(document.getElementById('u0-mesaj'), 'Casa ar ajunge la -58,00 lei.', 'eroare'))""")
    _clic(pg, "#u0-salveaza")
    vazut = pg.inner_text(".fereastra-corp")
    assert vazut.count("Casa ar ajunge la -58,00 lei.") == 1, vazut
    assert pg.inner_text(".refuz-salvare b") == "NU s-a salvat."


def test_refuzul_serverului_cu_trei_campuri_le_marcheaza_pe_toate_chiar_daca_ecranul_arata_numai_mesajul(pg):
    """2 + 3. Ecranul (ca în 25 de locuri înainte) arată numai `e.mesaj`; serverul a refuzat trei câmpuri + unul fără câmp pe ecran.
    Toate trei se marchează lângă câmp (aria-invalid, aria-describedby spre text, descrierea proprie a câmpului păstrată), caseta le
    are pe toate cu textul lor. MUTAȚIE: `setTimeout(() => _campuriAutomat(e, declansator), 0)` scos din `cere` -> câmpurile nemarcate
    -> pică."""
    pg.evaluate("async () => { %s }" % _FORMULAR)
    pg.evaluate("""() => document.getElementById('u0-salveaza').addEventListener('click', async () => {
        try { await window.U0.api.post('/tenants/7/u0-salveaza', {}); }
        catch (e) { window.U0.arataMesaj(document.getElementById('u0-zona-sus'), e.mesaj, 'eroare'); } })""")
    _clic(pg, "#u0-salveaza")
    pg.wait_for_function("() => document.querySelectorAll('[aria-invalid=true]').length === 3", timeout=5000)
    r = pg.evaluate("""() => ['u0-nume', 'u0-cui', 'u0-iban'].map((id) => {
        const el = document.getElementById(id);
        return [el.getAttribute('aria-invalid'), (el.getAttribute('aria-describedby') || '').split(' ').map((d) => (document.getElementById(d) || {}).textContent)];
      })""")
    assert r == [["true", ["Numele firmei lipsește."]],
                 ["true", ["fără RO", "CUI-ul nu are cifra de control corectă."]],
                 ["true", ["IBAN-ul are 23 de caractere, nu 24."]]], r
    caseta = pg.evaluate("() => [...document.querySelectorAll('.refuz-salvare li:not([hidden])')].map((li) => li.innerText)")
    assert caseta == ["Cererea nu poate fi acceptată: 3 câmpuri.", "Numele firmei — Numele firmei lipsește.",
                      "CUI — CUI-ul nu are cifra de control corectă.", "IBAN — IBAN-ul are 23 de caractere, nu 24.",
                      "Județul lipsește."], caseta   # câmpul nu e pe ecran: textul lui, nu pierdut
    # 3. corectat: legătura spre eroare pleacă, descrierea proprie rămâne
    pg.fill("#u0-cui", "14399840")
    assert pg.get_attribute("#u0-cui", "aria-describedby") == "u0-cui-ajutor"
    assert pg.get_attribute("#u0-cui", "aria-invalid") is None


def test_arataRefuzul_pune_campurile_si_textul_erorii_fara_camp_pe_ecran(pg):
    """2b. Helperul unic al ecranelor: fiecare câmp lângă el (cu harta nume-server -> id), iar eroarea al cărei câmp nu e pe ecran
    („Județul lipsește.”) intră în zona formularului, cu textul ei. MUTAȚIE: `rest` scos din `arataRefuzul` -> „Județul lipsește.”
    nu se mai vede -> pică."""
    pg.evaluate("async () => { %s }" % _FORMULAR)
    r = pg.evaluate("""() => {
      const e = { mesaj: 'Cererea nu poate fi acceptată.', erori_campuri: [
        { camp: 'nume', mesaj: 'Numele firmei lipsește.' }, { camp: 'iban', mesaj: 'IBAN-ul are 23 de caractere.' },
        { camp: 'judet', mesaj: 'Județul lipsește.' }] };
      const puse = window.U0.arataRefuzul(document.querySelector('.fereastra-corp'), e, document.getElementById('u0-mesaj'),
                                          { campuri: { nume: 'u0-nume', iban: 'u0-iban' } });
      return { puse, zona: document.getElementById('u0-mesaj').innerText,
               marcate: [...document.querySelectorAll('[aria-invalid=true]')].map((x) => x.id) };
    }""")
    assert r == {"puse": 2, "zona": "Cererea nu poate fi acceptată.\nJudețul lipsește.", "marcate": ["u0-nume", "u0-iban"]}, r


def test_cereCompletate_marcheaza_toate_campurile_goale_nu_numai_primul(pg):
    """4. DS cap.6 v2.30 pct.4: „Fail-fast e INTERZIS pe formularele multi-câmp.” MUTAȚIE: `lipsa = true;` urmat de `break` -> numai
    primul câmp marcat -> pică."""
    pg.evaluate("async () => { %s }" % _FORMULAR)
    r = pg.evaluate("""() => {
      const lipsa = window.U0.cereCompletate(document, ['u0-nume', { id: 'u0-cui', mesaj: 'Scrie CUI-ul firmei.' }, 'u0-iban']);
      return { lipsa, texte: [...document.querySelectorAll('.msg-eroare[data-camp]')].map((s) => s.textContent) };
    }""")
    assert r == {"lipsa": True, "texte": ["Completează „Numele firmei”.", "Scrie CUI-ul firmei.", "Completează „IBAN”."]}, r
