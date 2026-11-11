# -*- coding: utf-8 -*-
"""FERESTRE CARE SPUN ADEVĂRUL — lotul 17.5-O (AC080, AC081, AC108, AC143, AC180, AC181 din auditul complet;
decizii_17_5_O.txt și «De ce» din comanda_17_5_O.txt). Scris de arhitect; Code nu îl modifică. Probă pe bază: pică; pe C: trece.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), pe F1 Comert Stoc (tenant_9049) și F5 SRL Salariati (tenant_9053). Fiecare mesaj de eșec începe cu numărul AC
(și cu un id e.1–e.6 propriu testului, distinct de ids din oracolul pasi_17_5_O), urmat de martorul de pe snapshot:
  1. AC180: Stocuri F1 › cardul «NIR-urile lunii»: săgeata din fereastra de card are numai «←» (aria-label și title «Înapoi la Stocuri» rămân), fără text; întoarcerea păstrează luna aleasă;
  2. AC181: Rapoarte comerciale F1: un singur buton principal («Descarcă PDF»), «Salvează varianta curentă» e secundar;
  3. AC108: Fișa salariatului F5 (Ionescu Vasile): un singur «Fluturaș», în bara de jos, iar apăsarea lui cere ruta fluturas;
  4. AC143: fereastra mică «Stornează factura»: fără «←», cu «✕» și «Renunță»; «Renunță» închide fereastra, nimic nu se stornează;
  5. AC080: Mișcări și fișe de magazie F1: opțiunile listei de articole poartă stocul VALIDAT (cel din Stocuri), cu cifra din ciorne spusă separat când diferă; martor Marfa A 122 buc, nu 145;
  6. AC081: Analitică stoc F1: cantitățile de consum cu cantitate() (fără «.000»), procentele ABC cu pct();
Nu scrie nimic în baza de date (singura apăsare pe «Renunță» nu trimite cererea de stornare). Ids: e.1–e.6 (aserțiunile a.1–a.8 ale oracolului sunt altceva). Un singur test."""
import importlib.util
from decimal import Decimal, ROUND_HALF_UP
import json
import os
import re
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
F5 = "F5 SRL Salariati"
SCHEMA = "tenant_9049"
TOP = ".fereastra-overlay:not(.fundal) "
FER = TOP + ".fereastra"
JS_SAGEATA = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .nav-inapoi')].map((e) => ({
  text: (e.textContent || '').replace(/\\s+/g, ' ').trim(), aria: e.getAttribute('aria-label') || '', title: e.title || '', ascuns: !(e.offsetWidth || e.offsetHeight)}))"""
JS_PRINCIPALE = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .buton-primar')].filter((e) => e.offsetWidth || e.offsetHeight)
  .map((e) => ({ id: e.id || '', text: (e.textContent || '').replace(/\\s+/g, ' ').trim() }))"""
JS_BUTOANE_TEXT = """(t) => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) button')].filter((e) => (e.offsetWidth || e.offsetHeight)
  && (e.textContent || '').replace(/\\s+/g, ' ').trim() === t).map((e) => ({ clasa: e.className, in_bara: !!e.closest('.fereastra-jos') }))"""
JS_OPTIUNI_ART = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #cv-art option')].map((o) => [o.value, (o.textContent || '').replace(/\\s+/g, ' ').trim()])"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def ro_cant(v):
    """Formatul cantitate() al aplicației (static/js/api.js): cel mult trei zecimale, punct la mii, virgulă la zecimale, fără zerouri la coadă."""
    n = Decimal(str(v)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)   # ca toLocaleString din JS: half-up
    t = "{:,.3f}".format(n).replace(",", "§").replace(".", ",").replace("§", ".")
    return t.rstrip("0").rstrip(",") if "," in t else t


def ro_pct(v):
    """Formatul pct() al aplicației: întreg + «%», o zecimală cu virgulă când nu e întreg."""
    n = Decimal(str(v or 0))
    if n == n.to_integral_value():
        return str(int(n)) + "%"
    return str(n.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)).replace(".", ",") + "%"   # ca toFixed(1) din JS: half-up pe reprezentarea zecimală


def _text_brut(pg):
    return pg.evaluate("() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return e ? (e.textContent || '').replace(/\\s+/g, ' ').trim() : ''; }")


def _api(pg, cale, metoda="GET", corp=None):
    """Cerere către server cu sesiunea paginii; -> (status, json)."""
    return pg.evaluate("""async ([c, m, b]) => { const t = sessionStorage.getItem('iconta_token');
      const r = await fetch(c, { method: m, headers: Object.assign({ 'Authorization': 'Bearer ' + t }, b ? { 'Content-Type': 'application/json' } : {}), body: b ? JSON.stringify(b) : undefined });
      let j = null; try { j = await r.json(); } catch (e) {} return [r.status, j]; }""", [cale, metoda, corp])


def _sectiune(rele, nume, fn, *argumente):
    """O secțiune care aruncă excepție nu oprește celelalte: eșecul ei intră în listă."""
    try:
        fn(rele, *argumente)
    except Exception as e:   # noqa: BLE001
        rele.append("%s: secțiunea a căzut (%s: %s)" % (nume, type(e).__name__, str(e)[:200]))


def _card(pg, parcurs, firma, sel, asteapta=None):
    parcurs.firma(pg, firma)
    pg.evaluate("""(sel) => { const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return;
      const cont = c.closest('.firme-optiuni'); if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); } }""", sel)
    pg.click(TOP + sel, timeout=10000)
    if asteapta:
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    pg.wait_for_timeout(2000)


def _nir(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-stocuri", "[data-card='nir']")
    luna_inainte = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) input[type=month], .fereastra-overlay:not(.fundal) #st-luna') || {}).value || ''")
    pg.click(TOP + "[data-card='nir']", timeout=10000)
    pg.wait_for_selector(TOP + "#nir-mesaj", state="attached", timeout=20000)
    pg.wait_for_timeout(800)
    sageti = pg.evaluate(JS_SAGEATA)
    vizibile = [s for s in sageti if not s["ascuns"]]
    if len(vizibile) != 1:
        rele.append("AC180 / e.1: fereastra «NIR-urile lunii» are %d săgeți vizibile (așteptat 1): %s" % (len(vizibile), sageti))
        return
    s = vizibile[0]
    if s["text"] != "←":
        rele.append("AC180 / e.1: săgeata ferestrei de card are textul %r (așteptat numai «←»; textul «Înapoi la Stocuri» e în aria-label și title)" % s["text"])
    if "Înapoi la Stocuri" not in (s["aria"] + s["title"]):
        rele.append("AC180: săgeata a pierdut numele destinației din aria-label/title: %s" % s)
    pg.click(TOP + ".nav-inapoi")
    pg.wait_for_selector(TOP + "[data-card='nir']", state="attached", timeout=20000)
    luna_dupa = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) input[type=month], .fereastra-overlay:not(.fundal) #st-luna') || {}).value || ''")
    if luna_inainte != luna_dupa:
        rele.append("AC180: întoarcerea din card nu păstrează luna aleasă (înainte %r, după %r)" % (luna_inainte, luna_dupa))


def _rapoarte(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-rapoarte", "#r-var-salveaza")
    princ = pg.evaluate(JS_PRINCIPALE)
    if len(princ) != 1:
        rele.append("AC181 / e.2: Rapoarte comerciale F1 are %d butoane principale vizibile (așteptat 1: «Descarcă PDF»): %s" % (len(princ), princ))
    clasa = pg.get_attribute(TOP + "#r-var-salveaza", "class") or ""
    if "buton-primar" in clasa or "buton-secundar" not in clasa:
        rele.append("AC181 / e.2: «Salvează varianta curentă» are clasa %r (așteptat buton-secundar, fără buton-primar)" % clasa)
    if not any("PDF" in p["text"] for p in princ):
        rele.append("AC181: butonul principal rămas nu e «Descarcă PDF»: %s" % princ)
    if "Salvează varianta curentă" not in _text_brut(pg) or not pg.get_attribute(TOP + "#r-var-salveaza", "data-actiune"):
        rele.append("AC181: «Salvează varianta curentă» și-a pierdut textul sau data-actiune")


def _salariat(rele, pg, parcurs):
    parcurs.firma(pg, F5)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=false]').forEach(b => b.click())")   # cardul Salariați e într-un grup închis: fără deschidere, clicul expiră înainte de orice aserțiune
    pg.click(TOP + "#fa-salariati", timeout=10000)
    pg.wait_for_selector(TOP + "#sp-tabel tbody tr.sp-rand", timeout=30000)
    pg.locator(TOP + "#sp-tabel tbody tr.sp-rand", has_text="Ionescu").first.locator(".sp-deschide").click()
    pg.wait_for_selector(TOP + "#ss-butoane", timeout=30000)
    pg.wait_for_timeout(1500)
    f = pg.evaluate(JS_BUTOANE_TEXT, "Fluturaș")
    if len(f) != 1:
        rele.append("AC108 / e.3: Fișa salariatului F5 are %d butoane «Fluturaș» vizibile (așteptat 1, în bara de jos): %s" % (len(f), f))
    elif not f[0]["in_bara"] or "buton-primar" not in f[0]["clasa"]:
        rele.append("AC108: singurul «Fluturaș» nu e butonul principal din bara de jos: %s" % f[0])
    if "Fluturaș" in pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) #ss-butoane') || {textContent: ''}).textContent"):
        rele.append("AC108 / e.3: rândul de butoane #ss-butoane mai conține «Fluturaș»")
    try:
        with pg.expect_response(lambda r: "/fluturas/" in r.url, timeout=30000) as rr:
            pg.locator(TOP + "button", has_text=re.compile(r"^\s*Fluturaș\s*$")).last.click()
        if rr.value.status != 200:
            rele.append("AC108: «Fluturaș» din bară cere ruta fluturas și primește %s" % rr.value.status)
    except Exception as e:   # noqa: BLE001
        rele.append("AC108: apăsarea pe «Fluturaș» din bară nu a cerut ruta fluturas (%s)" % type(e).__name__)


def _storno(rele, pg, parcurs):
    parcurs.firma(pg, F1)
    pg.click(TOP + "#fa-facturi")
    pg.click(TOP + "#fac-istoric")
    pg.click(TOP + "#fac-prev")
    pg.locator(TOP + "button.fac-frand-btn").first.click()
    pg.click(TOP + "#fd-storno")
    pg.wait_for_selector(".fereastra.fer-mic", timeout=20000)
    pg.wait_for_timeout(600)
    sageti = [s for s in pg.evaluate("() => [...document.querySelectorAll('.fereastra.fer-mic .nav-inapoi')].map((e) => !!(e.offsetWidth || e.offsetHeight))") if s]
    if sageti:
        rele.append("AC143 / e.4: fereastra mică «Stornează factura» are %d săgeți «←» vizibile (așteptat 0: «✕» și «Renunță» rămân)" % len(sageti))
    inchide = pg.locator(".fereastra.fer-mic .nav-x").count()
    renunta = pg.locator(".fereastra.fer-mic #fd-storno-nu").count()
    if not inchide or not renunta:
        rele.append("AC143: fereastra mică și-a pierdut «✕» (%d) sau «Renunță» (%d)" % (inchide, renunta))
    cereri = []
    pg.on("request", lambda r: cereri.append(r.url) if r.method == "POST" and "/storno" in r.url else None)
    pg.click(".fereastra.fer-mic #fd-storno-nu")
    pg.wait_for_selector(".fereastra.fer-mic", state="detached", timeout=10000)
    if cereri:
        rele.append("AC143: «Renunță» a trimis o cerere de stornare: %s" % cereri)
    # ferestrele mari păstrează săgeata
    parcurs.firma(pg, F1)
    pg.click(TOP + "#fa-facturi")
    pg.click(TOP + "#fac-istoric")
    pg.wait_for_timeout(800)
    if not any(not s["ascuns"] for s in pg.evaluate(JS_SAGEATA)):
        rele.append("AC143: fereastra mare «Istoric facturi» și-a pierdut săgeata «←» (regula se aplică numai ferestrei mici)")


def _miscari(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-stocuri", "#cv-toggle")
    pg.click(TOP + "#cv-toggle")
    pg.wait_for_selector(TOP + "#cv-art option[value]:not([value=''])", state="attached", timeout=30000)
    opt = {v: t for v, t in pg.evaluate(JS_OPTIUNI_ART) if v}
    st, j = _api(pg, "/tenants/105779/stocuri/articole", "GET")
    arts = j if isinstance(j, list) else (j or {}).get("articole") or []
    if st != 200 or not arts:
        rele.append("AC080: ruta stocuri-cv a răspuns %s fără articole; nu se poate compara" % st)
        return
    nr = 0
    for a in arts:
        t = opt.get(str(a["id"]))
        if t is None:
            continue
        nr += 1
        valid = a.get("stoc_validat")
        asteptat = "%s · stoc %s %s" % (a["denumire"], ro_cant(valid if valid is not None else a["stoc"]), a["um"])
        if not t.startswith(asteptat):
            rele.append("AC080 / e.5: opțiunea articolului %s e %r, așteptat să înceapă cu %r (stocul VALIDAT, ca în Stocuri)" % (a["denumire"], t, asteptat))
        if valid is not None and a.get("stoc") != valid and ro_cant(a["stoc"]) not in t:
            rele.append("AC080: articolul %s are mișcări în ciornă (stoc cu ciorne %s), iar opțiunea nu spune cifra cu ciornele: %r" % (a["denumire"], a["stoc"], t))
        if valid is not None and a.get("stoc") == valid and "ciorn" in t:
            rele.append("AC080: articolul %s nu diferă de stocul validat, iar opțiunea vorbește de ciorne: %r" % (a["denumire"], t))
    if not nr:
        rele.append("AC080: nicio opțiune de articol nu a putut fi legată de răspunsul rutei")
    marfa = [a for a in arts if a["denumire"] == "Marfa A"]
    if marfa and marfa[0].get("stoc_validat") is not None and ro_cant(marfa[0]["stoc_validat"]) != "122":
        rele.append("AC080: martorul Marfa A are stocul validat %s pe snapshot (așteptat 122)" % marfa[0]["stoc_validat"])


def _analitica(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-stocuri", "#cv-toggle")
    pg.click(TOP + "#cv-toggle")
    pg.wait_for_selector(TOP + "#cv-ana", state="attached", timeout=30000)
    pg.click(TOP + "#cv-ana")
    pg.wait_for_timeout(2500)
    text = _text_brut(pg)
    st, r = _api(pg, "/tenants/105779/stocuri/analitica", "GET")
    if st != 200 or not isinstance(r, dict):
        rele.append("AC081: ruta de analitică a răspuns %s; nu se poate compara" % st)
        return
    for x in r.get("consum") or []:
        asteptat = "ieșiri ultimele 30 zile %s %s · 30 zile anterioare %s %s" % (ro_cant(x["iesiri_30z"]), x["um"], ro_cant(x["iesiri_30z_anterior"]), x["um"])
        if asteptat not in text:
            rele.append("AC081 / e.6: consumul articolului %s nu e scris cu cantitate(): lipsește %r" % (x["denumire"], asteptat))
    for x in r.get("abc") or []:
        asteptat = "cumulat %s" % ro_pct(x["pondere_cumulata"])
        if asteptat not in text:
            rele.append("AC081 / e.6: ABC al articolului %s nu e scris cu pct(): lipsește %r" % (x.get("denumire", "?"), asteptat))
    if re.search(r"\b\d+\.\d{2}%", text):
        rele.append("AC081: în Analitică stoc au rămas procente cu punct zecimal: %s" % re.findall(r"\b\d+\.\d{2}%", text)[:3])


JS_MODIFICARI_BARA = """async (ms) => {
  const F = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); if (!F) return -1;
  let n = 0;
  const mo = new MutationObserver((lista) => { for (const m of lista) { const t = m.target.nodeType === 1 ? m.target : m.target.parentElement; if (t && t.closest('.fereastra-jos, .bara-fixa')) n++; } });
  mo.observe(F, { childList: true, subtree: true, attributes: true, characterData: true });
  await new Promise((r) => setTimeout(r, ms)); mo.disconnect(); return n; }"""
EXPORT_F1 = ("Balanță de verificare", "Cartea mare", "Rapoarte comerciale", "Registrul de evidență fiscală", "Jurnal regim marjă")


def _stabilitate(rele, pg, parcurs):
    """AC183: după ce fereastra de export s-a așezat, bara de jos nu se mai modifică singură (pe bază: butonul ferestrei și exportul de rezervă se înlocuiesc la fiecare cadru)."""
    for nume in EXPORT_F1:
        parcurs.firma(pg, F1)
        pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=false]').forEach(b => b.click())")
        sel = pg.evaluate("""(nume) => { const c = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) button[id^="fa-"]')].find(b => (b.innerText || '').trim().split('\\n')[0].trim() === nume); return c ? c.id : ''; }""", nume)
        if not sel:
            rele.append("AC183: cardul «%s» nu s-a găsit pe F1" % nume)
            continue
        pg.click(TOP + "#" + sel, timeout=10000)
        pg.wait_for_timeout(3000)   # fereastra se așază: date încărcate, bara construită
        n = pg.evaluate(JS_MODIFICARI_BARA, 1500)
        if n != 0:
            rele.append("AC183 / e.13: în fereastra «%s» bara de jos se modifică singură: %d modificări în .fereastra-jos și .bara-fixa în 1,5 secunde fără nicio acțiune (așteptat 0)" % (nume, n))
        pdf = pg.evaluate("""() => { const F = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); const p = F && F.querySelector('.fj-butoane .fj-principal'); return p ? [(p.textContent || '').trim(), p.id || ''] : ['', '']; }""")
        if not pdf[0].startswith("Descarcă PDF"):
            rele.append("AC183: fereastra «%s» nu mai are «Descarcă PDF» ca buton principal în bara de jos (are %r)" % (nume, pdf[0]))


def _acasa(pg):
    """Pagina principală proaspătă (ca parcurs_17_5_O.acasa; parcurs_17_1 nu are această funcție): memoria ferestrei deschise se șterge, apoi goto și așteptarea cardurilor."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    pg.wait_for_timeout(1500)


def _suport(rele, pg, parcurs):
    _acasa(pg)
    pg.click("[data-banda='raport']", timeout=10000)
    pg.wait_for_selector(TOP + "#rap-zona-sesizare", state="attached", timeout=30000)
    pg.wait_for_timeout(1500)
    butoane = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) button')]
      .filter((e) => (e.textContent || '').trim() === 'Trimite sesizarea' && (e.offsetWidth || e.offsetHeight))
      .map((e) => ({ bara: !!e.closest('.fj-butoane'), id: e.id, clasa: e.className }))""")
    if len(butoane) != 1:
        rele.append("AC182 / e.12: fereastra Suport are %d butoane «Trimite sesizarea» vizibile (așteptat 1, în bara de jos): %s" % (len(butoane), butoane))
    elif not butoane[0]["bara"]:
        rele.append("AC182: singurul «Trimite sesizarea» vizibil nu e în bara de jos: %s" % butoane)
    elif butoane[0]["id"] != "rap-trimite":
        rele.append("AC182: butonul vizibil rămas nu mai poartă id-ul rap-trimite (îl apasă e2e_lot6, e2e_lot5_migrare, e2e_pozitii_validate, e2e_lot13_admin2): %s" % butoane)


def test_ferestre_17_5_O(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _sectiune(rele, "NIR-urile lunii (AC180)", _nir, pg, parcurs)
        _sectiune(rele, "Rapoarte comerciale F1 (AC181)", _rapoarte, pg, parcurs)
        _sectiune(rele, "Fișa salariatului F5 (AC108)", _salariat, pg, parcurs)
        _sectiune(rele, "Fereastra mică Stornează factura (AC143)", _storno, pg, parcurs)
        _sectiune(rele, "Mișcări și fișe de magazie F1 (AC080)", _miscari, pg, parcurs)
        _sectiune(rele, "Analitică stoc F1 (AC081)", _analitica, pg, parcurs)
        _sectiune(rele, "Suport (AC182)", _suport, pg, parcurs)
        _sectiune(rele, "Stabilitatea barei de jos (AC183)", _stabilitate, pg, parcurs)
    finally:
        b.close()
    assert not rele, "ferestrele 17.5-O: " + "; ".join(rele)
