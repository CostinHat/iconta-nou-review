# -*- coding: utf-8 -*-
"""LUNA DE LUCRU — lotul 17.5-C (rândurile A01, A12, A13 din auditul de ecrane; deciziile Costin 08.11.2026). Scris de arhitect; Code nu îl modifică.

(1) Pe F1 Comert Stoc, cu ceasul înghețat la 03.11.2026 și luna 10/2026 neblocată, ecranele lunare deschise din fereastra firmei, fără nicio apăsare
„← luna”, arată „Luna 10/2026”: Casă, Registru jurnal, Balanță de verificare, Stocuri, Salariați (Stat de plată), Închidere lună, Verificări.
(2) Cu 10/2026 raportată ca blocată (răspunsul GET perioade-blocate interceptat cu page.route, fără nicio scriere în bază: pe snapshot 10/2026
nu se poate bloca, are note în ciornă), după reîncărcarea paginii Balanța pornește pe 11/2026.
(3) Funcția pură lunaDeLucruDin din static/js/luna_lucru.js pe patru cazuri (fără blocări, luna trecută blocată, ianuarie, ianuarie cu decembrie blocat).
(4) O ciornă de factură cu data facturii 15.06.2025 (salvată la 01.07.2025) se redeschide cu data de azi (03.11.2026), iar cardul ciornei spune
„Data facturii din ciornă era 15.06.2025”; ciorna se șterge la final. Scrie în baza de test numai ciorna, pe care o șterge; baza se restaurează oricum înaintea plasei. Nu scrie în jurnalul lotului."""
import importlib.util
import os
import re
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
TOP = ".fereastra-overlay:not(.fundal) "
LUNA_LUCRU = "10/2026"
# cardul din fereastra firmei -> eticheta (toate ecranele au „Luna LL/AAAA” în textul ferestrei, static/js/ecrane/firme.js)
ECRANE = (("#fa-casa", "Casă"), ("#fa-jurnal", "Registru jurnal"), ("#fa-balanta", "Balanță de verificare"), ("#fa-stocuri", "Stocuri"),
          ("#fa-salariati", "Salariați (Stat de plată)"), ("#fa-inchidere", "Închidere lună"), ("#fa-verificari", "Verificări"))

JS_LUNA = """() => { const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); if (!f) return null;
  const m = f.innerText.match(/Luna (\\d{2}\\/\\d{4})/); return m ? m[1] : null; }"""
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
JS_API = """async ([metoda, url, corp]) => { const {api} = await import('/static/js/api.js');
  if (metoda === 'get') return await api.get(url); if (metoda === 'post') return await api.post(url, corp || {});
  if (metoda === 'put') return await api.put(url, corp || {}); return await api.del(url); }"""
JS_PURA = """async () => { const m = await import('/static/js/luna_lucru.js'); const f = m.lunaDeLucruDin;
  const t = (b, d) => { const r = f(b, d); return r.an + '/' + r.luna; };
  return [t([], new Date(2026, 10, 3)), t([{an: 2026, luna: 10}], new Date(2026, 10, 3)), t([], new Date(2027, 0, 15)), t([{an: 2026, luna: 12}], new Date(2027, 0, 15))]; }"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _luna_ecranului(pg, parcurs, sel):
    parcurs.firma(pg, F1)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return "cardul lipsește"
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); "
                             "return !!f && /Luna \\d{2}\\/\\d{4}/.test(f.innerText) && !document.querySelector('.fereastra-overlay:not(.fundal) #fa-facturi'); }",
                             timeout=30000)
    except Exception:   # noqa: BLE001 — ecranul nu arată nicio lună: se judecă ce s-a desenat
        pass
    pg.wait_for_timeout(800)
    return pg.evaluate(JS_LUNA)


def _tenant(pg):
    d = pg.evaluate(JS_API, ["get", "/tenants", None])
    lista = d.get("tenants", d) if isinstance(d, dict) else d
    return [t["id"] for t in lista if (t.get("denumire") or t.get("nume") or "").startswith(F1)][0]


def test_luna_de_lucru_17_5_C(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    tid = None
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        tid = _tenant(pg)
        bl = [(p["an"], p["luna"]) for p in (pg.evaluate(JS_API, ["get", "/tenants/%d/perioade-blocate" % tid, None]).get("blocate") or [])]
        assert (2026, 10) not in bl and (2026, 11) not in bl, "premisa: 10/2026 și 11/2026 neblocate pe F1 (blocate: %s)" % bl
        # (1) luna propusă la deschidere
        for sel, nume in ECRANE:
            luna = _luna_ecranului(pg, parcurs, sel)
            if luna != LUNA_LUCRU:
                rele.append("(1) %s: pornește pe %s, nu pe %s" % (nume, luna, LUNA_LUCRU))
        # (2) luna trecută blocată -> luna curentă (răspunsul serverului interceptat; nimic scris în bază)
        def _blocata_10(route):
            route.fulfill(status=200, content_type="application/json",
                          body='{"blocate": [{"an": 2026, "luna": 10}]}')
        tipar = re.compile(r".*/tenants/%d/perioade-blocate(\?.*)?$" % tid)
        pg.route(tipar, _blocata_10)
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        luna = _luna_ecranului(pg, parcurs, "#fa-balanta")
        if luna != "11/2026":
            rele.append("(2) Balanță cu 10/2026 blocată: pornește pe %s, nu pe 11/2026" % luna)
        pg.unroute(tipar)
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        # (3) funcția pură
        try:
            pura = pg.evaluate(JS_PURA)
        except Exception as e:   # noqa: BLE001 — modulul lipsește pe bază
            pura = "eroare: %s" % str(e)[:120]
        if pura != ["2026/10", "2026/11", "2026/12", "2027/1"]:
            rele.append("(3) lunaDeLucruDin: %s, așteptat ['2026/10', '2026/11', '2026/12', '2027/1']" % pura)
        # (4) ciorna de factură cu dată veche
        ciorna = {"v": 1, "salvat_la": "2025-07-01T10:00:00.000Z", "linii": [{"descriere": "Proba 17.5-C", "cantitate": 1, "pret_unitar": 10}], "moneda": "RON", "scadentaScrisa": False,
                  "pleacaMarfa": None, "semnMarfa": None, "campuri": {"em-data": "2025-06-15", "em-scadenta": "2025-07-15"}, "stareCui": None}
        pg.evaluate(JS_API, ["put", "/tenants/%d/ciorne-formular/factura" % tid, {"continut": ciorna}])
        parcurs.firma(pg, F1)
        pg.click(TOP + "#fa-facturi", timeout=10000)
        pg.click("#fac-emite", timeout=10000)
        pg.wait_for_selector("#em-cui", timeout=25000)
        pg.wait_for_timeout(1500)
        data = pg.input_value("#em-data")
        scad = pg.input_value("#em-scadenta")
        card = pg.inner_text("#em-ciorna") if pg.locator("#em-ciorna").count() else ""
        if data != "2026-11-03":
            rele.append("(4) data facturii din ciorna veche: %s, nu 2026-11-03" % data)
        if not scad or scad < "2026-11-03":
            rele.append("(4) scadența din ciorna veche: %s (înainte de data facturii)" % scad)
        if "Data facturii din ciornă era 15.06.2025" not in card:
            rele.append("(4) cardul ciornei nu spune „Data facturii din ciornă era 15.06.2025”: %s" % re.sub(r"\s+", " ", card)[:160])
    finally:
        try:
            if tid is not None:
                pg.evaluate(JS_API, ["del", "/tenants/%d/ciorne-formular/factura" % tid, None])
        except Exception:   # noqa: BLE001 — curățenia nu ascunde verdictul; baza se restaurează înaintea plasei
            pass
        b.close()
    assert not rele, "luna de lucru 17.5-C: %s" % "; ".join(rele)
