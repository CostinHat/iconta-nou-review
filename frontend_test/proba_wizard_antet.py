# -*- coding: utf-8 -*-
"""GARD browser (Playwright) pentru defectul de antet al wizardurilor — calea REALA 'Migrare cabinet'.
NU e in poarta verde (decizia lui Costin cand ruleaza). Ruleaza:
    venv/bin/python3 frontend_test/test_wizard_antet.py
Exit 0 = trecut, exit 1 = picat. Probeaza pe CODUL VECHI: pica (antetul acumuleaza + back nu revine).
Cauza (observata in browser): pe calea 'Migrare cabinet' fiecare strat se deschide ca fereastra noua
(nav.deschide); wizardSolduri/fratii fac setInapoi(()=>meniuMigrare) care re-randeaza meniul IN LOC in loc
de pop pe fereastra -> ferestrele se stivuiesc si antetul acumuleaza (Firme > Migrare cabinet > Solduri >
Salariati > ...). Fix: back prefera pop-ul natural (pas, altfel fereastra) inaintea setInapoi custom.
"""
import os, json, sys, urllib.request
from playwright.sync_api import sync_playwright

def _env(p):
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1); d[k] = v
    return d

C = _env(os.path.expanduser("~/.iconta/fe_test.env")); B = C["FE_TEST_BAZA"]
bd = json.dumps({"email": C["FE_TEST_EMAIL"], "parola": C["FE_TEST_PAROLA"]}).encode()
d = json.load(urllib.request.urlopen(urllib.request.Request(B + "/auth/login", bd, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(d["user"])) + ");")

def fir(pg):
    return pg.eval_on_selector_all(".fereastra-fir .fir-veriga", "els=>els.map(e=>e.textContent.trim())")
def corp(pg):
    return pg.eval_on_selector(".fereastra-corp",
        "e=>{var h=e.querySelector('h2,.pf-titlu,.mig-intro');return (h?h.textContent:e.textContent).trim().slice(0,40);}")
def clk(pg, txt, to=10000):
    pg.get_by_text(txt, exact=False).first.click(timeout=to); pg.wait_for_timeout(800)

esecuri = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True); ctx = b.new_context(); ctx.add_init_script(INIT); pg = ctx.new_page()
    pg.goto(B + "/", wait_until="domcontentloaded"); pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    clk(pg, "Firme"); clk(pg, "Migrare cabinet")
    baza_fir = fir(pg)                       # [Firme] (parintii pana la Migrare cabinet)
    print("Migrare cabinet: corp=%r fir=%r" % (corp(pg), baza_fir))

    # (1) intra pe un strat, back -> trebuie sa REVINA la 'Migrare cabinet'
    clk(pg, "Solduri ini")
    fir_solduri = fir(pg)
    print("dupa Solduri: corp=%r fir=%r" % (corp(pg), fir_solduri))
    pg.click(".nav-inapoi"); pg.wait_for_timeout(800)
    corp_back = corp(pg)
    print("back: corp=%r fir=%r" % (corp_back, fir(pg)))
    if "Migrare cabinet" not in corp_back:
        esecuri.append("back de pe Solduri NU revine la 'Migrare cabinet' (corp=%r)" % corp_back)

    # (2) navigheaza al doilea strat -> antetul NU trebuie sa acumuleze straturi vizitate
    clk(pg, "Salaria")
    fir_salariati = fir(pg)
    print("dupa Salariati: corp=%r fir=%r" % (corp(pg), fir_salariati))
    if "Solduri inițiale" in fir_salariati or "Solduri initiale" in fir_salariati:
        esecuri.append("antet ACUMULEAZA: 'Solduri' apare in firul de la Salariati %r" % fir_salariati)
    if len(fir_salariati) > len(fir_solduri):
        esecuri.append("antet CRESTE intre straturi: %d -> %d noduri" % (len(fir_solduri), len(fir_salariati)))
    # duplicate consecutive
    if any(fir_salariati[i] == fir_salariati[i+1] for i in range(len(fir_salariati)-1)):
        esecuri.append("noduri duplicate consecutive in antet: %r" % fir_salariati)
    b.close()

if esecuri:
    print("REZULTAT: PICAT")
    for e in esecuri:
        print("  - " + e)
    sys.exit(1)
print("REZULTAT: TRECUT (antet nu acumuleaza; back revine la meniu)")
sys.exit(0)
