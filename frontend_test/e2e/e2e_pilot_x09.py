# -*- coding: utf-8 -*-
"""PILOT X09 — o singură derulare pe ferestrele de lucru (lotul 17.5-B; deficiențele 814, 815, 793). Scris de arhitect; Code nu îl modifică.

Pe F1 Comert Stoc: Bancă, Casă, Registru jurnal, Balanță de verificare, Clienți, Stocuri, Salariați (Stat de plată); pe F5 SRL Salariati: Salariați și Fișa salariatului Ionescu Vasile.
La 603 × 590 și la 1366 × 768 aplică modelul din e2e_pilot_x06.py (JS_DERULARI): cel mult un loc de derulare verticală; dacă fereastra are .zona-derulare,
corpul nu derulează; la lățime <= 700 px fiecare zonă are cel puțin 40% din înălțimea corpului (pragul de 50% peste 700 px nu se cere în 17.5-B: deficiența 816). La Casă, nicio derulare orizontală (815). În plus (815): niciun element frunză cu text nu iese la dreapta ferestrei,
în afara unui container care derulează orizontal. Nu salvează nimic; nu scrie în jurnalul lotului și nici capturi în docs/dovezi/. Un singur test: test_pilot_X09."""
import importlib.util
import os
import sys

from conftest import BAZA, sesiune
from e2e_pilot_x06 import JS_DERULARI

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
DEFICIENTE_PROBATE = ("793",)   # 814 și 815 intră în DEFICIENTE.md odată cu rândurile 794–813 (arhitectul, pe main); core/test_deficiente.py:147-150 cere ca fiecare număr să existe în registru
TOP = ".fereastra-overlay:not(.fundal) "

# cardul ferestrei de lucru -> eticheta din raport (cardurile sunt în fereastra firmei; grupul pliat se deschide prin butonul lui de titlu)
F1_CARDURI = (("#fa-banca", "Bancă"), ("#fa-casa", "Casă"), ("#fa-jurnal", "Registru jurnal"), ("#fa-balanta", "Balanță de verificare"),
              ("#fa-clienti", "Clienți"), ("#fa-stocuri", "Stocuri"), ("#fa-salariati", "Salariați F1"))

JS_IESITE = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return null;
  const fr = F.getBoundingClientRect();
  const vazut = (e) => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const inDerulareOrizontala = (e) => { for (let p = e.parentElement; p && p !== F; p = p.parentElement) { if (/(auto|scroll)/.test(getComputedStyle(p).overflowX) && p.scrollWidth > p.clientWidth + 1) return true; } return false; };
  return [...F.querySelectorAll('.fereastra-corp *')].filter((e) => vazut(e) && e.children.length === 0 && e.textContent.trim() && e.getBoundingClientRect().right > fr.right + 1 && !inDerulareOrizontala(e))
    .map((e) => e.textContent.trim().slice(0, 30));
}"""

JS_ORIZONTALE = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return 0;
  return [F, ...F.querySelectorAll('*')].filter((e) => e.getClientRects().length > 0 && /(auto|scroll)/.test(getComputedStyle(e).overflowX) && e.scrollWidth > e.clientWidth + 1).length;
}"""

JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


LUNA_PILOT = "Luna 10/2026"
JS_ARE_LUNA = "(t) => { const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); return !!f && f.innerText.includes(t); }"
JS_LUNA_AFISATA = "() => { const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); const m = f && f.innerText.match(/Luna \\d{2}\\/\\d{4}/); return m ? m[0] : null; }"

def _masoara(pg):
    pg.wait_for_timeout(900)
    return {"derulari": pg.evaluate(JS_DERULARI), "iesite": pg.evaluate(JS_IESITE), "orizontale": pg.evaluate(JS_ORIZONTALE)}


def _card(pg, parcurs, firma, sel):
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return None
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector("#fa-facturi", state="detached", timeout=20000)
    except Exception:   # noqa: BLE001 — fereastra nu s-a schimbat: se măsoară ce e desenat, rezultatul pică
        pass
    # ceasul înghețat e 03.11.2026 (core/ceas_proba.py:7), iar datele lunii de lucru a Pilotului sunt în 10/2026. [17.5-C0] Luna de pornire a ferestrei
    # nu se presupune (17.5-C o schimbă): unde fereastra are „← luna”, se apasă până când textul ferestrei arată „Luna 10/2026”, cel mult 3 apăsări
    luna = pg.locator(TOP + ".fereastra-corp button", has_text="← luna")
    if luna.count():
        for _ in range(3):
            if pg.evaluate(JS_ARE_LUNA, LUNA_PILOT):
                break
            inainte = pg.evaluate(JS_LUNA_AFISATA)
            luna.first.click(timeout=10000)
            try:   # se așteaptă schimbarea antetului „Luna LL/AAAA”, nu un timp fix (o încărcare lentă nu duce la o apăsare în plus)
                pg.wait_for_function("(p) => (%s)() !== p" % JS_LUNA_AFISATA, arg=inainte, timeout=15000)
            except Exception:   # noqa: BLE001 — antetul nu s-a schimbat: se verifică mai jos
                pass
            pg.wait_for_timeout(600)
        if not pg.evaluate(JS_ARE_LUNA, LUNA_PILOT):
            return None   # fereastra n-a ajuns pe 10/2026 în 3 apăsări: _judeca o raportează ca fereastră nedeschisă
    return _masoara(pg)


def _judeca(nume, latime, m, rele):
    if m is None:
        rele.append("%s: cardul nu există, nu s-a deschis sau n-a ajuns pe Luna 10/2026" % nume)
        return
    d = m["derulari"]
    if not d or not d.get("fereastra"):
        rele.append("%s: nicio fereastră deschisă" % nume)
        return
    prag = 0.4 if latime <= 700 else None   # peste 700 px: fără prag de zonă în lotul 17.5-B (limită declarată, deficiența 816); rămân locurile de derulare, corpul și elementele ieșite
    if len(d["derulante"]) > 1:
        rele.append("%s: %d locuri de derulare verticală (%s)" % (nume, len(d["derulante"]), ", ".join(d["derulante"])))
    if d["zone"]:
        if d["corpContinut"] > d["corpInaltime"] + 2:
            rele.append("%s: fereastra derulează (%s px de conținut în %s px) deși are zonă de derulare" % (nume, d["corpContinut"], d["corpInaltime"]))
        for z in d["zone"]:
            if prag is not None and z["inaltime"] < prag * d["corpInaltime"]:
                rele.append("%s: zona %s are %s px din %s px ai corpului (cel puțin %d%%)" % (nume, z["loc"], z["inaltime"], d["corpInaltime"], round(prag * 100)))
    if nume.startswith("Casă") and m.get("orizontale"):
        rele.append("%s: %d containere cu derulare orizontală (815: acțiunile din rânduri încap fără derulare orizontală)" % (nume, m["orizontale"]))
    if m["iesite"]:
        rele.append("%s: %d elemente cu text ies din fereastră la dreapta (%s)" % (nume, len(m["iesite"]), ", ".join(m["iesite"][:4])))


def test_pilot_X09(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        for (w, h) in ((603, 590), (1366, 768)):
            pg.set_viewport_size({"width": w, "height": h})
            for sel, nume in F1_CARDURI:
                _judeca("%s %dx%d" % (nume, w, h), w, _card(pg, parcurs, "F1 Comert Stoc", sel), rele)
            _judeca("Salariați F5 %dx%d" % (w, h), w, _card(pg, parcurs, "F5 SRL Salariati", "#fa-salariati"), rele)
            try:
                pg.locator(TOP + "button, " + TOP + "tr, " + TOP + "td", has_text="Ionescu Vasile").first.click(timeout=10000)
                m = _masoara(pg)
            except Exception:   # noqa: BLE001
                m = None
            _judeca("Fișa salariatului Ionescu F5 %dx%d" % (w, h), w, m, rele)
    finally:
        b.close()
    assert not rele, "măsurători X09: %s" % "; ".join(rele)
