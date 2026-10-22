# -*- coding: utf-8 -*-
"""Lotul 11, 8c (decizia Costin 10.3: „8c: reparația centrală, cu DS cap. 6 actualizat.”) — după generarea unei note, un singur drum.

Clasa (comanda 10.2 pct.8c, raportul Z): „După generare, titlul «Notă generată» e roșu, conturile notei nu se văd, iar «Generează notă»
rămâne activ.” Pe orice ecran care generează o notă dintr-un calcul (Z, amortizare, inventar, descărcarea gestiunii, reevaluare,
compensare, operațiunile, salarii): confirmarea are stilul de succes, arată conturile și sumele, iar butonul devine inactiv cu motivul.

Temei: N/A — regulă de interfață (DS cap.6 v2.98, „După generarea unei note”).

CE FACE IMPOSIBIL (codul REAL din `api.js` și `stil.css`, în Chromium):
  1. confirmarea în culoarea refuzului de dinainte (zona cu `msg-eroare`), fără conturi, cu butonul activ;
  2. două motive lângă același buton (cel al ecranului și cel al generării) — „un mesaj, o singură dată” (DS cap.6 v2.89);
  3. reactivarea la propria scriere (butonul „Regenerează amortizarea” s-ar reaprinde imediat), sau nereactivarea după o scriere în datele
     din care se generează;
  4. conturile pierdute când răspunsul generării dă numai id-urile notelor (`noteGenerate` le citește din Registrul jurnal).
Partea statică (fiecare buton de generare trece prin helper, textul „Notă generată” numai în helper) e regula verificatorului
DUPA_GENERARE: `core/test_lot11_j_verificator.py`.
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

_JURNAL = {"note": [
    {"id": 41, "numar": "DESC-GV-2099-10", "descriere": "Descărcare gestiune 10/2099", "linii": [
        {"debit": "607", "credit": "371", "suma": 800.0}, {"debit": "378", "credit": "371", "suma": 150.0}]},
    {"id": 42, "numar": None, "descriere": "Altă notă a lunii", "linii": [{"debit": "6022", "credit": "5311", "suma": 11.0}]},
]}


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
    ok = lambda r, q: r.fulfill(status=200, content_type="application/json", body='{"ok": true}')
    p.route("**/tenants/7/amortizare**", ok)
    p.route("**/tenants/7/mijloace-fixe**", ok)
    p.route("**/tenants/7/jurnal?an=2099&luna=10", lambda r, q: r.fulfill(status=200, content_type="application/json",
                                                                         body=json.dumps(_JURNAL)))
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.add_style_tag(url="/static/stil.css")
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


def test_confirmarea_e_verde_arata_conturile_iar_butonul_e_inactiv_cu_motivul(pg):
    """1. Instanța Z: refuzul de dinainte („numerar + card ≠ total”, `msg-eroare` pe zonă), apoi nota generată. MUTAȚII: curățarea
    claselor `msg-*` scoasă din `dupaGenerare` -> zona rămâne roșie -> pică; `butonGenerat(...)` scos -> butonul rămâne activ -> pică."""
    r = pg.evaluate("""async () => {
      const { arataMesaj, dupaGenerare } = await import('/static/js/api.js');
      document.body.innerHTML = '<div><input id="z-nr" value="0042"><div id="z-rezultat"></div><p><button id="z-salveaza">Generează notă</button></p></div>';
      const zona = document.getElementById('z-rezultat'), b = document.getElementById('z-salveaza');
      arataMesaj(zona, 'Numerar + card (200,00) ≠ total (231,00): diferență 31,00.', 'eroare');
      dupaGenerare(zona, b, { eticheta: 'Z-0042 — ciornă', idLinii: 'z-nota-linii', reactiveazaLa: [document.getElementById('z-nr')],
        linii: [{debit: '5311', credit: '707', suma: '200.00'}, {debit: '5125', credit: '707', suma: '31.00'}, {debit: '707', credit: '4427', suma: '40.09'}] });
      const titlu = zona.querySelector('.cok-titlu');
      const m = document.getElementById(b.getAttribute('aria-describedby'));
      const inainte = { clasaZona: zona.className, caseta: !!zona.querySelector('.caseta-ok[role=status]'), titlu: titlu.textContent,
        culoare: getComputedStyle(titlu).color, linii: document.getElementById('z-nota-linii').innerText,
        inactiv: b.disabled, motiv: m && m.textContent };
      document.getElementById('z-nr').dispatchEvent(new Event('input'));   // alt raport Z scris în formular
      return { inainte, dupa: { inactiv: b.disabled, motiv: !!document.getElementById('z-salveaza-motiv-generat'),
                                descris: b.getAttribute('aria-describedby') } };
    }""")
    i = r["inainte"]
    assert "msg-eroare" not in i["clasaZona"] and i["caseta"], i   # 8c: „titlul «Notă generată» e roșu” -> nu mai e
    assert i["titlu"] == "Notă generată" and i["culoare"] == "rgb(27, 115, 73)", i   # --verde-inchis (#1b7349), nu roșul refuzului
    assert i["linii"].split("\n") == ["5311 = 707 · 200,00 lei", "5125 = 707 · 31,00 lei", "707 = 4427 · 40,09 lei"], i   # „conturile notei”
    assert i["inactiv"] and i["motiv"] == "Nota e generată — o vezi în Registru jurnal.", i   # „«Generează notă» rămâne activ” -> nu mai e
    assert r["dupa"] == {"inactiv": False, "motiv": False, "descris": None}, r


def test_motivul_ecranului_e_folosit_nu_dublat_si_revine_la_reactivare(pg):
    """2. Butonul are deja motivul lui (`aria-describedby`, ex. „Regenerează” la amortizarea în ciornă): generarea îi scrie textul acolo,
    nu încă un mesaj alături; la reactivare textul ecranului revine. MUTAȚIE: ramura „motivul existent” scoasă din `butonGenerat` ->
    două motive -> pică."""
    r = pg.evaluate("""async () => {
      const { butonGenerat, butonDeGenerat } = await import('/static/js/api.js');
      document.body.innerHTML = '<p><button id="j-amort" aria-describedby="j-amort-motiv">Regenerează amortizarea</button></p><p id="j-amort-motiv">Ciorna există.</p>';
      const b = document.getElementById('j-amort');
      butonGenerat(b, 'Nota e generată — o vezi mai jos.');
      const dupa = { motive: document.querySelectorAll('#j-amort-motiv, [data-motiv-generat]').length,
                     text: document.getElementById('j-amort-motiv').textContent, inactiv: b.disabled };
      butonDeGenerat(b);
      return { dupa, revenit: document.getElementById('j-amort-motiv').textContent, activ: !b.disabled, descris: b.getAttribute('aria-describedby') };
    }""")
    assert r == {"dupa": {"motive": 1, "text": "Nota e generată — o vezi mai jos.", "inactiv": True},
                 "revenit": "Ciorna există.", "activ": True, "descris": "j-amort-motiv"}, r


def test_reactivarea_la_scriere_ignora_propria_generare(pg):
    """3. „Regenerează amortizarea”: propria scriere (`/amortizare`) nu-l reaprinde; o scriere în registrul mijloacelor fixe, da.
    MUTAȚIE: predicatul ignorat (`butonDeGenerat` la orice semnal) -> butonul se reaprinde după propria generare -> pică."""
    r = pg.evaluate("""async () => {
      const { api, dupaGenerare } = await import('/static/js/api.js');
      document.body.innerHTML = '<div id="j-mesaj"></div><button id="j-amort">Generează amortizarea</button>';
      const b = document.getElementById('j-amort');
      await api.post('/tenants/7/amortizare?an=2099&luna=10', {});
      dupaGenerare(document.getElementById('j-mesaj'), b, { linii: [{debit: '6811', credit: '2813', suma: 200}],
        reactiveazaLaScriere: (cai) => cai.some((c) => /\\/mijloace-fixe/.test(c)) });
      await new Promise((ok) => setTimeout(ok, 700));
      const dupaPropria = b.disabled;
      await api.post('/tenants/7/mijloace-fixe', {});
      await new Promise((ok) => setTimeout(ok, 700));
      return { dupaPropria, dupaRegistru: b.disabled };
    }""")
    assert r == {"dupaPropria": True, "dupaRegistru": False}, r


def test_notele_generate_se_citesc_din_jurnal_dupa_id(pg):
    """4. Descărcarea gestiunii întoarce numai id-urile notelor: conturile se citesc din Registrul jurnal al lunii, numai notele cerute.
    MUTAȚIE: filtrul pe id scos din `noteGenerate` -> apare și nota 42 -> pică."""
    r = pg.evaluate("""async () => {
      const { noteGenerate } = await import('/static/js/api.js');
      return await noteGenerate(7, [41], '2099-10-31');
    }""")
    assert r == [{"eticheta": "DESC-GV-2099-10 · Descărcare gestiune 10/2099",
                  "linii": [{"debit": "607", "credit": "371", "suma": 800.0}, {"debit": "378", "credit": "371", "suma": 150.0}]}], r


def test_ordinea_notelor_si_campurile_formularului_raman(pg):
    """`noteGenerate` întoarce notele în ordinea id-urilor primite (eticheta i ↔ nota i), iar confirmarea pusă pe un container cu câmpuri
    nu le șterge (ca `arataMesaj`, DS cap.6 v2.82). MUTAȚII: ordinea din jurnal în loc de cea cerută -> pică; ramura „câmpuri” scoasă
    din `dupaGenerare` -> câmpul e detașat -> pică."""
    r = pg.evaluate("""async () => {
      const { noteGenerate, dupaGenerare } = await import('/static/js/api.js');
      const ord = (await noteGenerate(7, [42, 41], '2099-10-31')).map((n) => n.eticheta.slice(0, 4));
      document.body.innerHTML = '<div id="f"><input id="c" value="0042"><button id="b">Generează nota</button></div>';
      const c = document.getElementById('c');
      dupaGenerare(document.getElementById('f'), document.getElementById('b'), { linii: [] });
      return { ord, legat: c.isConnected, caseta: !!document.querySelector('#f > .msg-in-formular > .caseta-ok') };
    }""")
    assert r == {"ord": ["Altă", "DESC"], "legat": True, "caseta": True}, r
