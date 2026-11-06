# -*- coding: utf-8 -*-
"""PILOT X06 — Meniul firmei (comanda 17.1): fereastra firmei în 7 grupuri, titlul grupului e un buton (aria-expanded), implicit deschis numai „Zi de zi”, starea se reține în memorie cât aceeași firmă e deschisă, un card dintr-un grup
pliat se deschide (clic și căutare globală), „Migrare cabinet” o singură intrare, cardul Salariați cu descrierea nouă, lista „Firme existente” ca singur loc de derulare (788), modelul „o fereastră are o singură derulare” și lățimea de 40 px a lui „←” și „✕” (790). Fișier propriu, în plasa fixă (scripts/plasa_16_2.manifest), 1 test: test_pilot_X06.

Două părți: (1) parcursul docs/dovezi/17_1/parcurs_17_1.py, ale cărui aserțiuni (docs/dovezi/17_1/pasi.json) le judecă scripts/verifica_pas.verifica_pagina, în CSV-ul propriu din E2E_TEMP,
cu parcurgerea «plasa»; (2) măsurători directe pe DOM, pe care oracolul nu le are (lățimea butonului de titlu față de secțiune, aria-controls, tastatura Enter / Spațiu, clic pe un card dintr-un grup
deschis, căutarea globală pe ambele căi (card și intrare de catalog) care deschide un card dintr-un grup pliat și lasă grupul deschis după „←”, stilul calculat: 14 px, majuscule, 600, culoarea titlului, săgeata rotită 90° numai la grupul deschis; modelul „o singură derulare” și lățimile lui „←” / „✕” pe meniul „Firme”, „Firme existente” și fereastra firmei F1 și F4, la 1366 × 768 și în pagina de 603 × 590 px). Nu salvează nimic; nu scrie niciodată în jurnalul lotului sau capturi în docs/dovezi/.
Deficiențele pe care le dovedește: 788 și 790 (DEFICIENTE_PROBATE; core/test_deficiente.py::plasa_e2e îl citește ca literal). 789, 791, 792, 793 sunt nefăcute intenționat în 17.1."""
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types

import pytest

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

LOT = "17.1"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "17_1")
ADMIN = "dovada.71507@sesiuneab.test"
DEFICIENTE_PROBATE = ("788", "790")   # numerele dovedite de test (praguri_17_1.txt: „numere: 788, 790”); core/test_deficiente.py::plasa_e2e citește tuplul ca literal

TOP = ".fereastra-overlay:not(.fundal) "
ST = ".fereastra-overlay:not(.fundal) .fereastra "
TITLURI = ["zi de zi", "personal și stocuri", "contabilitate", "registre", "termene", "parteneri", "configurare"]
CHEI = ["zilnic", "personal", "contabilitate", "registre", "termene", "parteneri", "configurare"]

# pasul -> (deficiențele dovedite, ce se vede)
HARTA = {
    "a": ("17.1", "X06 (1): F1, 7 grupuri în ordine, 37 de carduri, deschis numai „Zi de zi”, ordinea cardurilor, Salariați cu descrierea nouă"),
    "b": ("17.1", "X06 (2): clic pe „Contabilitate” îl deschide"),
    "c": ("17.1", "X06 (2): al doilea clic îl pliază"),
    "d": ("17.1", "X06 (2): starea nu se reține după reîncărcare"),
    "e": ("17.1", "X06 (3): F4 PFA, 7 grupuri, 27 de carduri, ordinea cardurilor"),
    "f": ("17.1", "X06 (5): meniul „Firme” are o singură intrare spre Migrare cabinet"),
    "g": ("17.1, 788", "X06 (5)+(6): „Firme existente” fără „Import în masă (CSV)”, lista este zona de derulare, fereastra fixă"),
    "h": ("17.1", "X06 (2): aceeași firmă redeschisă după „←”, fără reîncărcare, păstrează „Contabilitate” deschis"),
    "k": ("17.1", "X06 (2): aceeași firmă redeschisă după „✕” (acasă, Firme › Firme existente), păstrează „Contabilitate” deschis"),
    "i": ("17.1", "X06 (2): după intrarea într-un card și „←”, „Contabilitate” a rămas deschis"),
    "j": ("17.1", "X06 (2): altă firmă (F4) după „←”, fără reîncărcare, pornește cu numai „Zi de zi” deschis"),
    "m": ("788, 790", "X06 (6)+(7): „Firme existente” în pagina de 603 × 590 px: lista este zona de derulare, fereastra fixă, „←” și „✕” de aceeași lățime"),
    "n": ("790", "X06 (7): fereastra firmei F1 în fereastra de 603 px: „←” și „✕” de aceeași lățime"),
}

# măsurătorile directe, în pagina vie: ultima fereastră care nu e fundal, grupurile ei
JS_GRUPURI = """() => {
  // stilul calculat al butonului de titlu: mărimea, majusculele, greutatea și culoarea vin de la titlul de grup (h3), săgeata are 16 × 16 și e rotită 90° numai când grupul e deschis
  const stil = (b, h) => {
    const cb = getComputedStyle(b), ch = getComputedStyle(h), sv = b.querySelector('svg'), cs = sv ? getComputedStyle(sv) : null;
    const m = cs && cs.transform !== 'none' ? cs.transform.match(/matrix\\(([^)]+)\\)/) : null, v = m ? m[1].split(',').map(Number) : null;
    return {marime: cb.fontSize, majuscule: cb.textTransform, greutate: cb.fontWeight, culoare: cb.color, culoareH3: ch.color,
            sagLatime: sv ? Math.round(sv.getBoundingClientRect().width) : null, sagInalt: sv ? Math.round(sv.getBoundingClientRect().height) : null,
            tranzitie: cs ? cs.transitionDuration : null, rotita: v ? (Math.abs(v[0]) < 0.01 && Math.abs(v[1] - 1) < 0.01) : false, faraRotire: !cs || cs.transform === 'none'};
  };
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return {fereastra: false};
  const grupuri = [...F.querySelectorAll('section.firme-grup')].map((s) => {
    const h = s.querySelector('h3'), b = s.querySelector('h3 > button.firme-grup-btn');
    const c = b ? document.getElementById(b.getAttribute('aria-controls') || '') : null;
    const rb = b ? b.getBoundingClientRect() : null, rs = s.getBoundingClientRect();
    return {cheie: h ? h.id : null, titlu: b ? b.innerText.replace(/\\s+/g, ' ').trim().toLowerCase() : null,
            expandat: b ? b.getAttribute('aria-expanded') : null, tip: b ? b.getAttribute('type') : null,
            controleaza: !!c && s.contains(c), ascuns: c ? c.hasAttribute('hidden') : null,
            inaltimeContinut: c ? Math.round(c.getBoundingClientRect().height) : null,
            dim: rb ? [Math.round(rb.width), Math.round(rb.height)] : null, latimeSectiune: Math.round(rs.width),
            sageata: !!(b && b.querySelector('svg')), carduri: c ? c.querySelectorAll('button.firme-optiune').length : 0,
            stil: b ? stil(b, h) : null};
  });
  return {fereastra: true, grupuri};
}"""
# modelul „o fereastră are o singură derulare” (comanda 17.1, pct.2 g) și lățimea lui „←” / „✕” (790), pe ultima fereastră care nu e fundal
JS_DERULARI = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return {fereastra: false};
  const corp = F.querySelector('.fereastra-corp'); if (!corp) return {fereastra: false};
  const nume = (e) => e.tagName.toLowerCase() + '.' + (String(e.className).trim().split(/\\s+/)[0] || '');
  const vazut = (e) => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const derulante = [corp, ...corp.querySelectorAll('*')].filter((e) => vazut(e) && /(auto|scroll)/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 2).map(nume);
  const zone = [...corp.querySelectorAll('.zona-derulare')].filter(vazut).map((z) => ({loc: nume(z), inaltime: z.clientHeight, continut: z.scrollHeight}));
  const lat = (sel) => [...F.querySelectorAll(sel)].filter((e) => e.getClientRects().length > 0 && e.getBoundingClientRect().width > 0).map((e) => Math.round(e.getBoundingClientRect().width * 10) / 10);
  return {fereastra: true, eticheta: F.getAttribute('aria-label'), corpInaltime: corp.clientHeight, corpContinut: corp.scrollHeight, derulante, zone,
          inapoi: lat('.fereastra-antet .nav-inapoi:not(.nav-inapoi-la)'), inchidere: lat('.fereastra-antet > .nav-x'),
          antet: (() => { const a = F.querySelector('.fereastra-antet'); return a ? [a.scrollWidth, a.clientWidth] : null; })()};
}"""
JS_OBSERVA = """(sel) => { window.__tranzitii = []; const b = document.querySelector(sel); if (!b) return false;
  new MutationObserver(() => window.__tranzitii.push(b.getAttribute('aria-expanded'))).observe(b, {attributes: true, attributeFilter: ['aria-expanded']}); return true; }"""


def _incarca(nume):
    spec = importlib.util.spec_from_file_location(nume, os.path.join(DOVEZI, nume + ".py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _asteapta_fereastra(pg, titlu):
    """Așteaptă fereastra din față cu aria-label care începe cu `titlu`; -> aria-label-ul ei sau None (nu numără ferestre: navigator.js:245–250 pe 1d99dc02, cauți după nume, păstrează un singur overlay)."""
    try:
        pg.wait_for_selector(TOP + '.fereastra[aria-label^="%s"]' % titlu, timeout=30000)
    except Exception:   # noqa: BLE001
        return None
    return pg.get_attribute(TOP + ".fereastra", "aria-label")


def _cauta(pg, parcurs, interogare, grup, titlu_fereastra, inapoi):
    """Fereastra firmei F1 proaspătă (goto), căutarea `interogare` în căsuța ferestrei, observator pe butonul grupului `grup`, clic pe primul rezultat."""
    parcurs.firma(pg)
    pg.click(ST + "#cautare-fereastra")
    pg.fill(ST + "#cautare-fereastra", interogare)
    pg.wait_for_selector(ST + "#cautare-fereastra-rez .cautare-item", timeout=15000)
    r = {"primul": pg.inner_text(ST + "#cautare-fereastra-rez .cautare-item >> nth=0")}
    r["observator"] = pg.evaluate(JS_OBSERVA, ST + "#fg-%s .firme-grup-btn" % grup)
    pg.locator(ST + "#cautare-fereastra-rez .cautare-item").first.click(timeout=20000)
    try:
        pg.wait_for_selector("#fa-facturi", state="detached", timeout=20000)
        r["fereastra_firmei_dispare"] = True
    except Exception:   # noqa: BLE001
        r["fereastra_firmei_dispare"] = False
        return r
    pg.wait_for_timeout(700)
    r["tranzitii"] = pg.evaluate("() => window.__tranzitii || []")
    r["eticheta"] = pg.get_attribute(TOP + ".fereastra", "aria-label")
    if titlu_fereastra:
        r["fereastra"] = _asteapta_fereastra(pg, titlu_fereastra)
    if inapoi:
        pg.click(TOP + ".nav-inapoi", timeout=10000)
        pg.wait_for_selector("#fa-facturi", timeout=20000)
        pg.wait_for_timeout(500)
        r["dupa_inapoi"] = pg.eval_on_selector(ST + "#fg-%s .firme-grup-btn" % grup, "b => b.getAttribute('aria-expanded')")
    return r


def test_pilot_X06(browser, monkeypatch):
    from core import ceas_proba
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("PARCURS_SHA", sha)
    temp = os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "pilot_x06")
    shutil.rmtree(temp, ignore_errors=True)
    os.makedirs(temp)
    jurnal = os.path.join(temp, "jurnal_verificare.csv")
    pasi_json = os.path.join(DOVEZI, "pasi.json")
    ctx = types.SimpleNamespace(lot=LOT, parcurgere="plasa", verificator="code", pasi_json=pasi_json, csv=jurnal, sha=sha,
                                director=os.path.join(temp, "plasa", "code"))
    os.makedirs(ctx.director, exist_ok=True)
    masuri = {}
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        parcurs = _incarca("parcurs_17_1")
        parcurs.ruleaza(pg, ctx)
        # (2) măsurători directe, pe ferestre deschise de funcțiile parcursului (nu de un al doilea parcurs)
        parcurs.firma(pg)
        pg.mouse.move(0, 0)   # hover-ul titlului are altă culoare (var(--ardezie)): mouse-ul nu stă peste niciun titlu la măsurarea culorii
        masuri["implicit"] = pg.evaluate(JS_GRUPURI)
        # tastatura: butonul de titlu e un buton nativ — Enter deschide, Spațiu pliază
        btn = ST + "#fg-contabilitate .firme-grup-btn"
        pg.focus(btn)
        pg.keyboard.press("Enter")
        pg.wait_for_selector(ST + "#fgc-contabilitate:not([hidden])", state="attached", timeout=5000)
        masuri["enter"] = pg.eval_on_selector(btn, "b => b.getAttribute('aria-expanded')")
        pg.keyboard.press("Space")
        pg.wait_for_selector(ST + "#fgc-contabilitate[hidden]", state="attached", timeout=5000)
        masuri["spatiu"] = pg.eval_on_selector(btn, "b => b.getAttribute('aria-expanded')")
        # un card dintr-un grup pliat, după ce omul îl deschide: clic pe card => se deschide fereastra lui (așteptată după aria-label, nu după numărul de ferestre)
        pg.click(ST + "#fg-termene .firme-grup-btn")
        pg.click(ST + "#fa-declaratii", timeout=10000)
        masuri["card_in_grup_deschis"] = _asteapta_fereastra(pg, "Declarații")
        # căutarea globală, calea 1 (_cardul): „centre de cost” = card din „Contabilitate” (pliat); după clic fereastra firmei dispare din DOM, deci tranziția
        # false -> true a butonului grupului o notează un observator instalat înainte de clic; apoi „←” și grupul trebuie să fi rămas deschis (starea din memorie)
        masuri["cautare_card"] = _cauta(pg, parcurs, "centre de cost", "contabilitate", "Centre de cost", inapoi=True)
        # calea 2 (_pasiiEcranului): „stat de plată” = intrare de catalog (primul clic: #fa-salariati, din „Personal și stocuri”, pliat)
        masuri["cautare_catalog"] = _cauta(pg, parcurs, "stat de plată", "personal", None, inapoi=False)
        # 788 și 790: criteriul „o singură derulare” și lățimea lui „←” / „✕”, măsurate pe DOM la 1366 × 768 și în pagina de 603 × 590 px
        masuri["derulari"] = {}
        for (w, h) in ((1366, 768), (603, 590)):
            pg.set_viewport_size({"width": w, "height": h})
            parcurs._la_meniul_firme(pg)
            masuri["derulari"]["meniul Firme %dx%d" % (w, h)] = pg.evaluate(JS_DERULARI)
            pg.click("#opt-existente")
            pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
            pg.wait_for_timeout(700)
            masuri["derulari"]["Firme existente %dx%d" % (w, h)] = pg.evaluate(JS_DERULARI)
            parcurs._deschide_din_lista(pg, "F1 Comert Stoc")
            masuri["derulari"]["firma F1 %dx%d" % (w, h)] = pg.evaluate(JS_DERULARI)
            parcurs._inapoi_la_lista(pg)
            parcurs._deschide_din_lista(pg, "F4 PFA Sistem Real")
            masuri["derulari"]["firma F4 %dx%d" % (w, h)] = pg.evaluate(JS_DERULARI)
        pg.set_viewport_size({"width": 1366, "height": 768})
    finally:
        b.close()
    asertiuni = [a["id"] for a in json.load(open(pasi_json, encoding="utf-8"))["asertiuni"]]
    verdicte = {}
    if os.path.exists(jurnal):
        with open(jurnal, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["parcurgere"] == "plasa" and r["commit"].startswith(sha[:8]):
                    verdicte[r["pas"]] = r["verdict"]
    picate = ["%s [%s]: %s" % (i, HARTA[i.split(".")[0]][1], verdicte.get(i, "neexecutat")) for i in asertiuni if verdicte.get(i) != "trece"]
    assert not picate, "aserțiuni X06 care nu trec (id [ce se vede]: verdict): %s" % "; ".join(picate)
    rele = []
    m = masuri["implicit"]
    if not m.get("fereastra"):
        rele.append("implicit: nicio fereastră deschisă")
    else:
        g = m["grupuri"]
        if [x["titlu"] for x in g] != TITLURI or [x["cheie"] for x in g] != ["fg-" + c for c in CHEI]:
            rele.append("grupuri: titluri/ids %s" % [(x["cheie"], x["titlu"]) for x in g])
        for x in g:
            if x["tip"] != "button" or not x["controleaza"] or not x["sageata"]:
                rele.append("%s: buton type=%s, aria-controls valid=%s, săgeată=%s" % (x["cheie"], x["tip"], x["controleaza"], x["sageata"]))
            if not x["dim"] or x["dim"][1] != 40 or abs(x["dim"][0] - x["latimeSectiune"]) > 1:
                rele.append("%s: buton %s, secțiune %s (așteptat înălțime 40, lățime = a secțiunii)" % (x["cheie"], x["dim"], x["latimeSectiune"]))
            if (x["expandat"] == "true") == bool(x["ascuns"]) or (x["ascuns"] and x["inaltimeContinut"] != 0):
                rele.append("%s: aria-expanded=%s, hidden=%s, înălțime conținut=%s (trebuie să se potrivească)" % (x["cheie"], x["expandat"], x["ascuns"], x["inaltimeContinut"]))
            if not x["carduri"]:
                rele.append("%s: niciun card în grup" % x["cheie"])
            st = x["stil"] or {}
            if st.get("marime") != "14px" or st.get("majuscule") != "uppercase" or st.get("greutate") != "600" or st.get("culoare") != st.get("culoareH3"):
                rele.append("%s: stil titlu %s (așteptat 14px, uppercase, 600, culoarea titlului de grup)" % (x["cheie"], st))
            if st.get("tranzitie") not in ("0s", None):
                rele.append("%s: săgeata are transition (%s); trebuie fără animație" % (x["cheie"], st.get("tranzitie")))
            if st.get("sagLatime") != 16 or st.get("sagInalt") != 16:
                rele.append("%s: săgeata %s × %s (așteptat 16 × 16)" % (x["cheie"], st.get("sagLatime"), st.get("sagInalt")))
            deschis = x["expandat"] == "true"
            if (deschis and not st.get("rotita")) or (not deschis and not st.get("faraRotire")):
                rele.append("%s: săgeata rotită=%s, fără rotire=%s la aria-expanded=%s (rotită 90° numai când e deschis)" % (x["cheie"], st.get("rotita"), st.get("faraRotire"), x["expandat"]))
        if sum(x["carduri"] for x in g) != 37:
            rele.append("carduri în total: %s (așteptat 37)" % sum(x["carduri"] for x in g))
    if masuri["enter"] != "true" or masuri["spatiu"] != "false":
        rele.append("tastatura: după Enter aria-expanded=%s (așteptat true), după Spațiu %s (așteptat false)" % (masuri["enter"], masuri["spatiu"]))
    if not masuri["card_in_grup_deschis"]:
        rele.append("clic pe #fa-declaratii din grupul „Termene” deschis nu a deschis fereastra „Declarații” (aria-label așteptat: începe cu „Declarații”)")
    for cheie, grup, titlu in (("cautare_card", "contabilitate", "Centre de cost"), ("cautare_catalog", "personal", None)):
        r = masuri[cheie]
        if not r.get("observator"):
            rele.append("%s: nu există butonul grupului %s pentru observator" % (cheie, grup))
        elif not r.get("fereastra_firmei_dispare"):
            rele.append("%s: după clic pe primul rezultat (%r) fereastra firmei nu s-a închis (cardul nu s-a deschis)" % (cheie, r.get("primul")))
        else:
            if "true" not in r.get("tranzitii", []):
                rele.append("%s: grupul %s nu a trecut din pliat în deschis (tranziții aria-expanded: %s)" % (cheie, grup, r.get("tranzitii")))
            if titlu and not r.get("fereastra"):
                rele.append("%s: nu s-a deschis fereastra „%s” (aria-label ferestrei din față: %r)" % (cheie, titlu, r.get("eticheta")))
            if cheie == "cautare_card" and r.get("dupa_inapoi") != "true":
                rele.append("%s: după „←” grupul %s are aria-expanded=%s (așteptat true: starea se reține în memorie)" % (cheie, grup, r.get("dupa_inapoi")))
    if "centre de cost" not in masuri["cautare_card"].get("primul", "").lower():
        rele.append("căutarea „centre de cost”: primul rezultat este %r (așteptat cardul Centre de cost)" % masuri["cautare_card"].get("primul"))
    # modelul „o fereastră are o singură derulare” (pct.2 g): (A) fără zonă, derulează corpul și nimic dinăuntru; (B) cu zonă, corpul nu derulează (scrollHeight <= clientHeight + 2)
    # și zona are cel puțin 50% din înălțimea corpului la 1366 × 768 și cel puțin 40% în pagina de 603 × 590 px; lista „Firme existente” are zonă oricâte firme ar avea (788);
    # „←” și „✕” sunt exact câte unul și au 40 px lățime (790); titlul și antetul nu depășesc lateral (scrollWidth <= clientWidth + 1)
    for nume, m2 in masuri["derulari"].items():
        if not m2.get("fereastra"):
            rele.append("%s: nicio fereastră deschisă" % nume)
            continue
        pagina = int(nume.rsplit(" ", 1)[1].split("x")[0])
        prag = 0.4 if pagina <= 700 else 0.5
        if len(m2["derulante"]) > 1:
            rele.append("%s: %d locuri de derulare verticală (%s)" % (nume, len(m2["derulante"]), ", ".join(m2["derulante"])))
        if m2["zone"]:
            if m2["corpContinut"] > m2["corpInaltime"] + 2:
                rele.append("%s: fereastra derulează (%s px de conținut în %s px) deși are zonă de derulare" % (nume, m2["corpContinut"], m2["corpInaltime"]))
            for z in m2["zone"]:
                if z["inaltime"] < prag * m2["corpInaltime"]:
                    rele.append("%s: zona %s are %s px din %s px ai corpului ferestrei (cel puțin %d%% cerut)" % (nume, z["loc"], z["inaltime"], m2["corpInaltime"], round(prag * 100)))
        if nume.startswith("Firme existente") and not m2["zone"]:
            rele.append("%s: lista de firme nu este zonă de derulare (788: fereastra nu derulează, lista este zona)" % nume)
        if len(m2["inchidere"]) != 1:
            rele.append("%s: %d butoane „✕” vizibile în antet (așteptat exact 1; fără trecere pe gol)" % (nume, len(m2["inchidere"])))
        asteptat = 0 if nume.startswith("meniul Firme") else 1
        if len(m2["inapoi"]) != asteptat:
            rele.append("%s: %d butoane „←” vizibile în antet (așteptat %d; fără trecere pe gol)" % (nume, len(m2["inapoi"]), asteptat))
        for l in m2["inapoi"] + m2["inchidere"]:
            if abs(l - 40) > 0.5:
                rele.append("%s: „←” %s px, „✕” %s px lățime (așteptat 40 ± 0,5)" % (nume, m2["inapoi"], m2["inchidere"]))
                break
        for eticheta, sc in (("antetul", m2.get("antet")),):
            if sc and sc[0] > sc[1] + 1:
                rele.append("%s: %s ferestrei depășește lateral (scrollWidth %s > clientWidth %s + 1)" % (nume, eticheta, sc[0], sc[1]))
    assert not rele, "măsurători directe X06: %s" % "; ".join(rele)
