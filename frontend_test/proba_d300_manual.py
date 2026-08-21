# -*- coding: utf-8 -*-
"""Traseu 1 REAL: panoul manual D300, din ecranul principal -> Declaratii -> D300 -> ALFA MICRO -> adauga/regen/sterge rand."""
import os, json, re, urllib.request
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v
_body = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(urllib.request.Request(
    BAZA + "/auth/login", _body, {"Content-Type": "application/json"}), timeout=15))
print("USER poate_pregati =", (_d.get("user") or {}).get("poate_pregati"))
INIT = ("sessionStorage.setItem(\"iconta_token\"," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem(\"iconta_user\"," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.dirname(os.path.abspath(__file__))

def sc(pg, n):
    p = os.path.join(OUT, n); pg.screenshot(path=p, full_page=True); print("screenshot:", p)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(700)
    # --- ecran principal: card Declaratii ---
    card = pg.query_selector(".cab-card:has(.cab-card-sinteza[data-cheie=\"declaratii\"])")
    if card:
        print("NAV: dashboard -> card Declaratii")
        card.click()
    else:
        print("NAV: card Declaratii absent -> Firme > ALFA MICRO > Declaratii")
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000)
        pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)
    if pg.query_selector("#dec-firma"):
        pg.select_option("#dec-firma", "8396"); pg.wait_for_timeout(1000)
        print("firma aleasa: ALFA MICRO (8396)")
    pg.wait_for_selector("#dec-tip option[value=\"d300\"]", timeout=8000, state="attached")
    pg.select_option("#dec-tip", "d300"); pg.wait_for_timeout(600)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2026"); pg.dispatch_event("#dec-an", "change")
    if pg.query_selector("#dec-luna"):
        pg.select_option("#dec-luna", "8")
    pg.wait_for_timeout(300)
    an_v = pg.eval_on_selector("#dec-an", "e=>e.value") if pg.query_selector("#dec-an") else "?"
    lu_v = pg.eval_on_selector("#dec-luna", "e=>e.value") if pg.query_selector("#dec-luna") else "?"
    print("perioada: an=%s luna=%s" % (an_v, lu_v))
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=6000)
    pg.click("#dec-continua")
    # --- pas2: panoul manual ---
    pg.wait_for_selector("#dec-d300-manual details", timeout=25000); pg.wait_for_timeout(700)
    summ = pg.eval_on_selector("#dec-d300-manual summary", "e=>e.innerText")
    nopt = pg.eval_on_selector_all("#d300-rand option", "els=>els.length") if pg.query_selector("#d300-rand") else 0
    lbls = pg.eval_on_selector_all("#dec-d300-manual .camp-eticheta", "els=>els.map(e=>e.innerText)")
    r16 = pg.eval_on_selector_all("#d300-rand option", "els=>els.filter(o=>o.value==='R16').map(o=>o.textContent)")
    stare = pg.eval_on_selector(".dec-ok, .dec-eroare, .dec-avert", "e=>e.className+' :: '+e.innerText.slice(0,80)") if pg.query_selector(".dec-ok,.dec-eroare,.dec-avert") else "?"
    print("PANOU RANDAT. summary =", repr(summ))
    print("  stare ANAF:", stare)
    print("  #d300-rand optiuni:", nopt)
    print("  etichete panou:", lbls[:8])
    print("  R16 optiune text:", r16)
    sc(pg, "d300_1_inainte.png")
    # --- adauga R16 baza 1000 ---
    pg.select_option("#d300-rand", "R16"); pg.wait_for_timeout(200)
    pg.fill("#d300-baza", "1000")
    tva_vis = pg.eval_on_selector("#d300-tva-wrap", "e=>getComputedStyle(e).display") if pg.query_selector("#d300-tva-wrap") else "n/a"
    print("  dupa alegere R16: #d300-tva-wrap display =", tva_vis)
    if tva_vis != "none" and pg.query_selector("#d300-tva"):
        pg.fill("#d300-tva", "190")
    sc(pg, "d300_2_form_completat.png")
    pg.click("#d300-add")
    pg.wait_for_function("() => { const s=document.querySelector('#dec-d300-manual summary'); return s && s.innerText.indexOf('(1)')>=0; }", timeout=12000)
    summ2 = pg.eval_on_selector("#dec-d300-manual summary", "e=>e.innerText")
    rand_txt = pg.eval_on_selector(".dec-man-rand", "e=>e.innerText.replace(/\\n/g,' | ')")
    print("DUPA ADAUGARE. summary =", repr(summ2))
    print("  rand adaugat:", repr(rand_txt))
    sc(pg, "d300_3_dupa_adaugare.png")
    # --- Regenereaza D300 ---
    pg.click("#d300-regen")
    pg.wait_for_selector("#dec-d300-manual details", timeout=25000); pg.wait_for_timeout(800)
    summ3 = pg.eval_on_selector("#dec-d300-manual summary", "e=>e.innerText")
    xml = pg.eval_on_selector(".dec-xml-pre", "e=>e.innerText") if pg.query_selector(".dec-xml-pre") else ""
    m = re.search(r"[^\d](1000)[^\d]", xml)
    print("DUPA REGEN. summary =", repr(summ3))
    print("  XML lungime =", len(xml), " | '1000' in XML:", "1000" in xml)
    sc(pg, "d300_4_dupa_regen.png")
    # --- sterge randul ---
    pg.click(".dec-d300-del")
    pg.wait_for_function("() => { const s=document.querySelector('#dec-d300-manual summary'); return s && s.innerText.indexOf('(0)')>=0; }", timeout=12000)
    summ4 = pg.eval_on_selector("#dec-d300-manual summary", "e=>e.innerText")
    print("DUPA STERGERE. summary =", repr(summ4))
    sc(pg, "d300_5_dupa_stergere.png")
    b.close()
    print("TRASEU 1 DONE")
