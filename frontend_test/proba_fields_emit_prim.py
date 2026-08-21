# -*- coding: utf-8 -*-
"""Traseu 2 (emitere: tert_tara + tip_operatiune) si Traseu 3 (primite: furnizor_tva_incasare)."""
import os, json, urllib.request
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
INIT = ("sessionStorage.setItem(\"iconta_token\"," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem(\"iconta_user\"," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.dirname(os.path.abspath(__file__))

def sc(pg, n):
    p = os.path.join(OUT, n); pg.screenshot(path=p, full_page=True); print("screenshot:", p)

def nav_firma_facturi(pg):
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(600)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-facturi", timeout=10000)
    pg.click("#fa-facturi"); pg.wait_for_timeout(500)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()

    # ===== TRASEU 2: EMITERE =====
    nav_firma_facturi(pg)
    pg.wait_for_selector("#fac-emite", timeout=10000); pg.click("#fac-emite")
    pg.wait_for_selector("#em-da, #em-add-linie", timeout=12000); pg.wait_for_timeout(300)
    if pg.query_selector("#em-da"):
        if pg.query_selector("#em-tva-nu"):
            pg.click("#em-tva-nu"); pg.wait_for_timeout(150)
        pg.click("#em-nu"); pg.wait_for_timeout(300)
        if pg.query_selector("#em-salveaza-config2"):
            pg.click("#em-salveaza-config2")
    pg.wait_for_selector("#em-tara", timeout=12000); pg.wait_for_timeout(300)
    tara_lbl = pg.eval_on_selector("label[for=\"em-tara\"]", "e=>e.innerText")
    tipop_lbl = pg.eval_on_selector("label[for=\"em-tipop\"]", "e=>e.innerText")
    n_tara = pg.eval_on_selector_all("#em-tara option", "els=>els.length")
    has_ro = pg.eval_on_selector_all("#em-tara option", "els=>els.some(o=>o.value==='RO')")
    ue = pg.eval_on_selector_all("#em-tara optgroup", "els=>els.map(g=>g.label)")
    sample_ue = pg.eval_on_selector_all("#em-tara option", "els=>els.filter(o=>['DE','FR','IT'].includes(o.value)).map(o=>o.textContent)")
    tipop = pg.eval_on_selector_all("#em-tipop option", "els=>els.map(o=>o.value+':'+o.textContent)")
    sect_lbl = pg.eval_on_selector(".em-sectiune .em-eticheta:has-text('D300'), .em-eticheta", "e=>e.innerText") if pg.query_selector(".em-eticheta") else "?"
    print("== TRASEU 2 EMITERE (ALFA MICRO) ==")
    print("  sectiune eticheta:", repr(sect_lbl))
    print("  label em-tara:", repr(tara_lbl), "| optiuni:", n_tara, "| RO prezent:", has_ro, "| optgroups:", ue)
    print("  mostre UE:", sample_ue)
    print("  label em-tipop:", repr(tipop_lbl), "| optiuni:", tipop)
    sc(pg, "emit_campuri_noi.png")

    # ===== TRASEU 3: FACTURI PRIMITE =====
    nav_firma_facturi(pg)
    if pg.query_selector("#fac-primite"):
        pg.click("#fac-primite")
        pg.wait_for_selector(".pf-titlu, .stare-goala", timeout=12000); pg.wait_for_timeout(400)
        titlu = pg.eval_on_selector(".pf-titlu", "e=>e.innerText") if pg.query_selector(".pf-titlu") else "?"
        n_prim = pg.eval_on_selector_all(".fac-primita-btn", "els=>els.length")
        goala = pg.eval_on_selector(".stare-goala", "e=>e.innerText") if pg.query_selector(".stare-goala") else None
        print("== TRASEU 3 FACTURI PRIMITE (ALFA MICRO) ==")
        print("  titlu:", repr(titlu), "| facturi in lista:", n_prim)
        print("  stare-goala:", repr(goala))
        sc(pg, "primite_lista.png")
        if n_prim > 0:
            pg.click(".fac-primita-btn")
            pg.wait_for_selector("#pr-furnizor-incasare", timeout=10000); pg.wait_for_timeout(300)
            lbl = pg.eval_on_selector("label:has(#pr-furnizor-incasare) .tip-micut", "e=>e.innerText")
            has_tara = bool(pg.query_selector("#pr-tara"))
            print("  checkbox #pr-furnizor-incasare PREZENT. eticheta:", repr(lbl))
            print("  #pr-tara prezent:", has_tara)
            sc(pg, "primite_detaliu_checkbox.png")
        else:
            print("  NU pot atinge checkbox-ul: lista SPV goala pentru toate firmele de test (0 facturi primite).")
    else:
        print("  #fac-primite absent (rol client?)")
    b.close()
    print("DONE T2/T3")
