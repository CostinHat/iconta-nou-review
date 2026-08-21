# -*- coding: utf-8 -*-
"""Confirm de ce .em-total se micsoreaza: display-ul parintilor + test token lung nespargibil pe .msg-eroare."""
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
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.expanduser("~/iconta_nou/frontend_test")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1100, "height": 1500}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(500)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-facturi", timeout=10000)
    pg.click("#fa-facturi"); pg.wait_for_timeout(500)
    pg.wait_for_selector("#fac-emite", timeout=10000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-da, #em-add-linie", timeout=12000); pg.wait_for_timeout(300)
    if pg.query_selector("#em-da"):
        if pg.query_selector("#em-tva-nu"): pg.click("#em-tva-nu"); pg.wait_for_timeout(150)
        pg.click("#em-nu"); pg.wait_for_timeout(300)
        pg.wait_for_selector("#em-salveaza-config2", timeout=8000); pg.click("#em-salveaza-config2")
    pg.wait_for_selector("#em-add-linie", timeout=12000); pg.wait_for_timeout(500)
    chain = pg.eval_on_selector("#em-total", """el=>{
      const out=[]; let n=el; let i=0;
      while(n && i<6){const c=getComputedStyle(n); const r=n.getBoundingClientRect();
        out.push({tag:n.tagName, cls:n.className||'', display:c.display, flexDir:c.flexDirection,
          alignItems:c.alignItems, w:Math.round(r.width)});
        n=n.parentElement; i++;}
      return out;}""")
    print("=== lant parinti #em-total ===")
    for x in chain: print(x)
    b.close()
