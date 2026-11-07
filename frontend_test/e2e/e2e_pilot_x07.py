# -*- coding: utf-8 -*-
"""PILOT X07 — reorganizarea ecranelor după munca contabilului (comanda 17.2): pagina principală a cabinetului cu secțiunea pliabilă „Pentru șeful de cabinet” (6 + 6 carduri), Setări cont în 3 secțiuni,
cifrele zero din Sinteza zilei ca text, lista Asistenților fără „Vizualizează” (numele deschide fișa, „Editează” rămâne pe rând), fișa salariatului cu „+ Beneficiu” și „Mai multe”. Fișier propriu, în plasa fixă
(scripts/plasa_16_2.manifest), 1 test.
Două părți: (1) parcursul docs/dovezi/17_2/parcurs_17_2.py, ale cărui aserțiuni (docs/dovezi/17_2/pasi.json) le judecă scripts/verifica_pas.verifica_pagina, în CSV-ul propriu din E2E_TEMP, cu parcurgerea «plasa»;
(2) măsurători directe pe DOM, pe care oracolul nu le are (lățimea și stilul butonului de titlu, locul secțiunii în grilă, tastatura Enter / Spațiu, clic pe un card din secțiune, starea după „✕” și după reîncărcare,
relația cifră > 0 <=> buton în Sinteza zilei, nume-buton și clic pe rând în Asistenți, meniurile fișei salariatului).
Lotul 17.2 nu primește numere de deficiență de la arhitect: DEFICIENTE_PROBATE e tuplul gol (praguri_17_2.txt: „numere: niciunul”); core/test_deficiente.py::plasa_e2e îl citește ca literal."""
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

LOT = "17.2"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "17_2")
ADMIN = "dovada.71507@sesiuneab.test"
DEFICIENTE_PROBATE = ()   # fără numere în acest lot (praguri_17_2.txt: „numere: niciunul”)

TOP = ".fereastra-overlay:not(.fundal) "
SUS = ["validat", "control", "termene", "firme", "brief", "setari"]
SEF = ["activitate", "pachete", "supervizor", "capacitate", "consolidare", "asistenti"]
SETARI = [["Date profil", "Schimbă parola", "Notificări"], ["Date cabinet", "Ce pot face", "Datele cabinetului (GDPR)"], ["Chei API", "Conectare SPV"]]
TITLURI_SETARI = ["Contul meu", "Cabinet", "Conexiuni"]

# prefixul aserțiunii -> ce se vede
HARTA = {"a": "X07 (a): pagina principală, secțiunea „Pentru șeful de cabinet”", "b": "X07 (b): Setări cont în 3 secțiuni", "c": "X07 (c): Sinteza zilei, cifre zero ca text",
         "d": "X07 (d): lista Asistenților", "e": "X07 (e): fișa salariatului", "f": "X07: ce nu se schimbă"}

JS_PAGINA = """() => {
  const stil = (b, h) => {
    const cb = getComputedStyle(b), ch = getComputedStyle(h), sv = b.querySelector('svg'), cs = sv ? getComputedStyle(sv) : null;
    const m = cs && cs.transform !== 'none' ? cs.transform.match(/matrix\\(([^)]+)\\)/) : null, v = m ? m[1].split(',').map(Number) : null;
    return {marime: cb.fontSize, majuscule: cb.textTransform, greutate: cb.fontWeight, culoare: cb.color, culoareH3: ch.color,
            sagLatime: sv ? Math.round(sv.getBoundingClientRect().width) : null, sagInalt: sv ? Math.round(sv.getBoundingClientRect().height) : null,
            tranzitie: cs ? cs.transitionDuration : null, rotita: v ? (Math.abs(v[0]) < 0.01 && Math.abs(v[1] - 1) < 0.01) : false, faraRotire: !cs || cs.transform === 'none'};
  };
  const s = document.querySelector('.cab-grila > section.firme-grup'); if (!s) return {sectiune: false};
  const h = s.querySelector('h3'), b = h.querySelector('button.firme-grup-btn'), c = document.getElementById(b.getAttribute('aria-controls') || '');
  const rb = b.getBoundingClientRect(), rs = s.getBoundingClientRect(), chei = (r) => [...r.querySelectorAll('button.cab-card [data-cheie]')].map((e) => e.dataset.cheie);
  const grila = s.parentElement;
  return {sectiune: true, titlu: b.textContent.replace(/\\s+/g, ' ').trim(), expandat: b.getAttribute('aria-expanded'), tip: b.getAttribute('type'), controleaza: !!c && s.contains(c),
          ascuns: c ? c.hasAttribute('hidden') : null, inaltimeContinut: c ? Math.round(c.getBoundingClientRect().height) : null, dim: [Math.round(rb.width), Math.round(rb.height)],
          latimeSectiune: Math.round(rs.width), latimeGrila: Math.round(grila.getBoundingClientRect().width), sageata: !!b.querySelector('svg'),
          sus: chei(grila).filter((k) => !c || !c.querySelector('[data-cheie="' + k + '"]')), inSectiune: c ? chei(c) : [],
          dupaSetari: !!s.previousElementSibling && !!s.previousElementSibling.querySelector('[data-cheie="setari"]'), ultimul: !s.nextElementSibling,
          cardInGrilaSus: [...grila.children].filter((x) => x.matches('button.cab-card')).length, stil: stil(b, h)};
}"""
JS_SETARI = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); if (!F) return {};
  const hs = [...F.querySelectorAll('h3.ds-grup-titlu')];
  return {titluri: hs.map((h) => h.textContent.trim()), intrari: hs.map((h) => { const g = h.nextElementSibling; return g && g.classList.contains('set-meniu') ? [...g.querySelectorAll('.meniu-card')].map((x) => x.textContent.trim()) : null; }),
          stil: hs.map((h) => { const c = getComputedStyle(h); return [c.fontSize, c.textTransform]; }), grile: F.querySelectorAll('.set-meniu').length, intro: !!F.querySelector('p.mig-intro')};
}"""
JS_SINTEZA = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal)'); if (!F) return [];
  return [...F.querySelectorAll('.sa-cifra')].map((e) => { const n = e.querySelector('.sa-num'), cs = getComputedStyle(e);
    return {tag: e.tagName, num: n ? n.textContent.trim() : null, clic: e.classList.contains('sa-clic'), cursor: cs.cursor, marime: n ? getComputedStyle(n).fontSize : null}; });
}"""
JS_FISA = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal)'); const bt = F && F.querySelector('#ss-butoane'); if (!bt) return {fisa: false};
  const det = (id) => { const d = bt.querySelector('#' + id); return d ? {tag: d.tagName, deschis: d.hasAttribute('open'), butoane: d.querySelectorAll('button').length, summary: ((d.querySelector('summary') || {}).textContent || '').trim()} : null; };
  return {fisa: true, copii: bt.children.length, butoane: bt.querySelectorAll('button').length, benef: det('ss-benef'), maiMulte: det('ss-mai-multe'),
          directe: ['flut', 'cm', 'iban', 'date'].map((k) => !!bt.querySelector(':scope > [data-' + k + ']'))};
}"""


def _incarca(nume):
    spec = importlib.util.spec_from_file_location(nume, os.path.join(DOVEZI, nume + ".py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _fereastra(pg, rx):
    """Așteaptă fereastra din față al cărei aria-label se potrivește ÎNTREG cu expresia `rx` (navigator.js:256: aria-label = titlul ferestrei); -> aria-label-ul ei sau None.
    Potrivire exactă, nu pe prefix: „Asistent — <nume>” nu se confundă cu „Asistenți”."""
    try:
        pg.wait_for_function("(rx) => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return !!f && new RegExp(rx).test(f.getAttribute('aria-label') || ''); }", arg=rx, timeout=30000)
    except Exception:   # noqa: BLE001
        return None
    return pg.get_attribute(TOP + ".fereastra", "aria-label")


def test_pilot_X07(browser, monkeypatch):
    from core import ceas_proba
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("PARCURS_SHA", sha)
    temp = os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "pilot_x07")
    shutil.rmtree(temp, ignore_errors=True)
    os.makedirs(temp)
    jurnal = os.path.join(temp, "jurnal_verificare.csv")
    pasi_json = os.path.join(DOVEZI, "pasi.json")
    ctx = types.SimpleNamespace(lot=LOT, parcurgere="plasa", verificator="code", pasi_json=pasi_json, csv=jurnal, sha=sha, director=os.path.join(temp, "plasa", "code"))
    os.makedirs(ctx.director, exist_ok=True)
    m = {}
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        # data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        P = _incarca("parcurs_17_2")
        P.ruleaza(pg, ctx)
        # (2) măsurători directe
        P.acasa(pg)
        pg.mouse.move(0, 0)
        m["pagina"] = pg.evaluate(JS_PAGINA)
        btn = P.BTN_SEF
        pg.focus(btn)
        pg.keyboard.press("Enter")
        pg.wait_for_selector(P.SEF_DESCHIS, state="attached", timeout=5000)
        m["enter"] = pg.eval_on_selector(btn, "b => b.getAttribute('aria-expanded')")
        m["deschis"] = pg.evaluate(JS_PAGINA)
        pg.keyboard.press("Space")
        pg.wait_for_selector(P.SEF_PLIAT, state="attached", timeout=5000)
        m["spatiu"] = pg.eval_on_selector(btn, "b => b.getAttribute('aria-expanded')")
        # starea: deschis, intrare într-un card din secțiune, „✕” => a rămas deschis; reîncărcare => pliat
        pg.click(btn)
        pg.click(P.card("asistenti"), timeout=10000)
        m["card_in_sectiune"] = _fereastra(pg, "^Asistenți$")
        P.x_acasa(pg)
        m["dupa_x"] = pg.eval_on_selector(btn, "b => b.getAttribute('aria-expanded')")
        P.acasa(pg)
        m["dupa_goto"] = pg.eval_on_selector(btn, "b => b.getAttribute('aria-expanded')")
        # Setări cont
        P.deschide_card(pg, "setari", ".set-meniu")
        m["setari"] = pg.evaluate(JS_SETARI)
        P.x_acasa(pg)
        # Sinteza zilei: butonul <=> cifra > 0
        P.deschide_card(pg, "brief", TOP + ".sa-cifra")
        pg.wait_for_timeout(1200)
        m["sinteza"] = pg.evaluate(JS_SINTEZA)
        P.x_acasa(pg)
        # Asistenți: nume-buton, clic pe rând, „Editează”
        P.lista_asistenti(pg)
        m["asi_text"] = pg.text_content(TOP + ".fereastra-corp") or ""
        m["asi_randuri"] = pg.eval_on_selector_all(TOP + "#asi-lista > .val-card", "rs => rs.map(r => ({nume: r.querySelectorAll('.asi-nume button[data-act=\"vezi\"]').length, edit: r.querySelectorAll('[data-act=\"edit\"]').length, vezi: r.querySelectorAll('[data-act=\"vezi\"]').length}))")
        pg.locator(TOP + "#asi-lista > .val-card .asi-nume button[data-act='vezi']").first.click()
        m["asi_nume"] = _fereastra(pg, "^Asistent \u2014 .+$")
        pg.click(TOP + ".nav-inapoi")
        pg.wait_for_selector(TOP + "#asi-lista > .val-card", timeout=20000)
        pg.locator(TOP + "#asi-lista > .val-card .asi-rol").first.click()
        m["asi_rand"] = _fereastra(pg, "^Asistent \u2014 .+$")
        pg.click(TOP + ".nav-inapoi")
        pg.wait_for_selector(TOP + "#asi-lista > .val-card", timeout=20000)
        pg.locator(TOP + "#asi-lista > .val-card [data-act='edit']").first.click()
        m["asi_edit"] = _fereastra(pg, "^Editează \u2014 .+$")
        P.x_acasa(pg)
        # fișa salariatului
        P.fisa_salariat(pg)
        m["fisa"] = pg.evaluate(JS_FISA)
        pg.click(TOP + "#ss-benef > summary")
        pg.wait_for_selector(TOP + "#ss-benef[open]", state="attached", timeout=5000)
        pg.click(TOP + "#ss-butoane [data-masa]")
        m["masa"] = _fereastra(pg, "^Tichet de masă \u00b7 .+$")
        pg.click(TOP + ".nav-inapoi")
        pg.wait_for_selector(TOP + "#ss-butoane", timeout=20000)
        pg.click(TOP + "#ss-mai-multe > summary")
        pg.wait_for_selector(TOP + "#ss-mai-multe[open]", state="attached", timeout=5000)
        m["reges_vizibil"] = pg.locator(TOP + "#ss-mai-multe [data-reges]").is_visible()
    finally:
        b.close()
    asertiuni = json.load(open(pasi_json, encoding="utf-8"))["asertiuni"]
    verdicte = {}
    if os.path.exists(jurnal):
        with open(jurnal, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["parcurgere"] == "plasa" and r["commit"].startswith(sha[:8]):
                    verdicte[r["pas"]] = r["verdict"]
    picate = ["%s [%s]: %s" % (a["id"], HARTA[a["id"].split(".")[0]], verdicte.get(a["id"], "neexecutat")) for a in asertiuni if verdicte.get(a["id"]) != "trece"]
    assert not picate, "aserțiuni X07 care nu trec (id [ce se vede]: verdict): %s" % "; ".join(picate)
    rele = []
    p = m["pagina"]
    if not p.get("sectiune"):
        rele.append("pagina principală: nu există secțiunea pliabilă")
    else:
        if p["titlu"] != "Pentru șeful de cabinet" or p["tip"] != "button" or not p["controleaza"] or not p["sageata"]:
            rele.append("secțiune: titlu=%r, type=%s, aria-controls valid=%s, săgeată=%s" % (p["titlu"], p["tip"], p["controleaza"], p["sageata"]))
        if p["dim"][1] != 40 or abs(p["dim"][0] - p["latimeSectiune"]) > 1 or abs(p["latimeSectiune"] - p["latimeGrila"]) > 1:
            rele.append("secțiune: buton %s, secțiune %s, grilă %s (așteptat înălțime 40, lățime = a secțiunii = a grilei)" % (p["dim"], p["latimeSectiune"], p["latimeGrila"]))
        if p["expandat"] != "false" or not p["ascuns"] or p["inaltimeContinut"] != 0:
            rele.append("implicit: aria-expanded=%s, hidden=%s, înălțime conținut=%s (așteptat pliat)" % (p["expandat"], p["ascuns"], p["inaltimeContinut"]))
        if p["sus"] != SUS or p["inSectiune"] != SEF:
            rele.append("carduri: sus %s, în secțiune %s (așteptat %s / %s)" % (p["sus"], p["inSectiune"], SUS, SEF))
        if not p["dupaSetari"] or not p["ultimul"] or p["cardInGrilaSus"] != 6:
            rele.append("loc: după cardul setari=%s, ultimul element al grilei=%s, carduri direct în grilă=%s (așteptat True, True, 6)" % (p["dupaSetari"], p["ultimul"], p["cardInGrilaSus"]))
        st = p["stil"]
        if st["marime"] != "14px" or st["majuscule"] != "uppercase" or st["greutate"] != "600" or st["culoare"] != st["culoareH3"]:
            rele.append("stil titlu %s (așteptat 14px, uppercase, 600, culoarea titlului de grup)" % st)
        if st["tranzitie"] not in ("0s", None) or st["sagLatime"] != 16 or st["sagInalt"] != 16 or not st["faraRotire"]:
            rele.append("săgeata pliată: %s (așteptat 16 × 16, fără transition, fără rotire)" % st)
        d = m["deschis"]
        if d["expandat"] != "true" or d["ascuns"] or not d["inaltimeContinut"] or not d["stil"]["rotita"]:
            rele.append("deschis: aria-expanded=%s, hidden=%s, înălțime=%s, săgeată rotită=%s" % (d["expandat"], d["ascuns"], d["inaltimeContinut"], d["stil"]["rotita"]))
    if m["enter"] != "true" or m["spatiu"] != "false":
        rele.append("tastatura: după Enter aria-expanded=%s (așteptat true), după Spațiu %s (așteptat false)" % (m["enter"], m["spatiu"]))
    if not m["card_in_sectiune"]:
        rele.append("clic pe cardul Asistenți din secțiunea deschisă nu a deschis fereastra „Asistenți”")
    if m["dupa_x"] != "true":
        rele.append("după „✕” secțiunea are aria-expanded=%s (așteptat true: starea se reține în memorie)" % m["dupa_x"])
    if m["dupa_goto"] != "false":
        rele.append("după reîncărcare secțiunea are aria-expanded=%s (așteptat false: starea nu se reține)" % m["dupa_goto"])
    s = m["setari"]
    if s.get("titluri") != TITLURI_SETARI or s.get("intrari") != SETARI or s.get("grile") != 3 or not s.get("intro"):
        rele.append("Setări cont: titluri %s, intrări %s, grile %s, intro %s (așteptat %s / %s / 3)" % (s.get("titluri"), s.get("intrari"), s.get("grile"), s.get("intro"), TITLURI_SETARI, SETARI))
    elif any(x != ["14px", "uppercase"] for x in s["stil"]):
        rele.append("Setări cont: stil titluri %s (așteptat 14px, uppercase)" % s["stil"])
    c = m["sinteza"]
    if len(c) != 6:
        rele.append("Sinteza zilei: %d cifre (așteptat 6)" % len(c))
    for x in c:
        pozitiv = x["num"] not in (None, "0")
        if (x["tag"] == "BUTTON") != pozitiv:
            rele.append("Sinteza zilei: cifra %r e %s (buton exact când cifra > 0)" % (x["num"], x["tag"]))
        if x["tag"] != "BUTTON" and (x["clic"] or x["cursor"] == "pointer"):
            rele.append("Sinteza zilei: cifra text %r are .sa-clic=%s, cursor=%s" % (x["num"], x["clic"], x["cursor"]))
    if len({x["marime"] for x in c}) > 1:
        rele.append("Sinteza zilei: cifrele au mărimi diferite %s" % sorted({x["marime"] for x in c}))
    if "vizualizează" in m["asi_text"].lower():
        rele.append("Asistenți: textul „Vizualizează” apare încă în fereastră")
    if not m["asi_randuri"] or any(r != {"nume": 1, "edit": 1, "vezi": 1} for r in m["asi_randuri"]):
        rele.append("Asistenți: rânduri %s (așteptat un buton-nume, un „Editează”, un singur [data-act=vezi])" % m["asi_randuri"])
    if not m["asi_nume"] or not m["asi_rand"]:
        rele.append("Asistenți: clic pe nume -> %r, clic pe rând -> %r (așteptat fereastra „Asistent — <nume>”)" % (m["asi_nume"], m["asi_rand"]))
    if not m["asi_edit"]:
        rele.append("Asistenți: „Editează” nu a deschis fereastra „Editează — <nume>”")
    f = m["fisa"]
    if not f.get("fisa") or f["copii"] != 13 or f["butoane"] != 19 or not all(f["directe"]):
        rele.append("fișa: %s (așteptat 13 copii, 19 butoane, flut/cm/iban/date direct)" % f)
    else:
        for cheie, n in (("benef", 5), ("maiMulte", 3)):
            d = f[cheie]
            if not d or d["tag"] != "DETAILS" or d["deschis"] or d["butoane"] != n:
                rele.append("fișa: %s = %s (așteptat details pliat cu %d butoane)" % (cheie, d, n))
        if (f["benef"] or {}).get("summary") != "+ Beneficiu" or (f["maiMulte"] or {}).get("summary") != "Mai multe":
            rele.append("fișa: summary-uri %r / %r" % ((f["benef"] or {}).get("summary"), (f["maiMulte"] or {}).get("summary")))
    if not m["masa"]:
        rele.append("fișa: „+ masă” din „+ Beneficiu” nu a deschis fereastra „Tichet de masă · <nume>”")
    if not m["reges_vizibil"]:
        rele.append("fișa: „REGES” nu e vizibil după deschiderea lui „Mai multe”")
    assert not rele, "măsurători directe X07: %s" % "; ".join(rele)
