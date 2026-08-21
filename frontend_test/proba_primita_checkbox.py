# -*- coding: utf-8 -*-
"""Traseu 3 REAL: factura primita SPV -> detaliu -> checkbox furnizor_tva_incasare + tert_tara -> valideaza."""
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

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(600)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-facturi", timeout=10000)
    pg.click("#fa-facturi"); pg.wait_for_timeout(500)
    pg.wait_for_selector("#fac-primite", timeout=10000); pg.click("#fac-primite")
    pg.wait_for_selector(".fac-primita-btn, .stare-goala", timeout=12000); pg.wait_for_timeout(400)
    n = pg.eval_on_selector_all(".fac-primita-btn", "els=>els.length")
    print("== TRASEU 3 (re-run) ALFA MICRO ==")
    print("  facturi in inbox SPV:", n)
    if n == 0:
        print("  INBOX GOL - opresc.")
        sc(pg, "primite_lista_rerun.png"); b.close(); raise SystemExit
    lst = pg.eval_on_selector(".fac-primita-btn", "e=>e.innerText.replace(/\\n/g,' | ')")
    print("  rand lista:", repr(lst))
    sc(pg, "primite_lista_rerun.png")
    pg.click(".fac-primita-btn")
    pg.wait_for_selector("#pr-furnizor-incasare", timeout=10000); pg.wait_for_timeout(400)
    # etichete + prezenta campuri
    chk_lbl = pg.eval_on_selector("label:has(#pr-furnizor-incasare) .tip-micut", "e=>e.innerText")
    tara_lbl = pg.eval_on_selector("label:has(#pr-tara) .camp-eticheta", "e=>e.innerText")
    tara_val = pg.eval_on_selector("#pr-tara", "e=>e.value")
    cont_val = pg.eval_on_selector("#pr-cont", "e=>e.value") if pg.query_selector("#pr-cont") else "(fara)"
    titlu = pg.eval_on_selector(".pf-titlu", "e=>e.innerText")
    print("  detaliu titlu:", repr(titlu))
    print("  checkbox #pr-furnizor-incasare PREZENT. eticheta:", repr(chk_lbl))
    print("  #pr-tara PREZENT. eticheta:", repr(tara_lbl), "| valoare initiala:", repr(tara_val))
    print("  #pr-cont sugerat:", repr(cont_val))
    sc(pg, "primite_detaliu_checkbox.png")
    # bifeaza + completeaza cont + tara
    pg.check("#pr-furnizor-incasare")
    if not cont_val.strip():
        pg.fill("#pr-cont", "628")
    pg.fill("#pr-tara", "RO")
    print("  checkbox bifat:", pg.eval_on_selector("#pr-furnizor-incasare", "e=>e.checked"))
    sc(pg, "primite_detaliu_bifat.png")
    # valideaza -> caseta de confirmare (#caseta-atentie-activa cu #ca-ok text 'Validează')
    pg.click("#pr-valideaza"); pg.wait_for_timeout(500)
    pg.wait_for_selector("#ca-ok", timeout=6000)
    print("  caseta confirmare buton ok text:", repr(pg.eval_on_selector("#ca-ok", "e=>e.innerText")))
    pg.click("#ca-ok")
    pg.wait_for_timeout(1800)
    msg = pg.eval_on_selector("#pr-zona", "e=>e.innerText") if pg.query_selector("#pr-zona") else ""
    print("  mesaj dupa validare:", repr(msg[:200]))
    sc(pg, "primite_dupa_validare.png")
    b.close()
    print("TRASEU 3 DONE")
