# -*- coding: utf-8 -*-
"""Proba #16 (cabinet): poza bonului se afiseaza prin data:URL (nu blob:), img randata (naturalWidth>0)."""
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
OUT = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1400}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme", exact=True).first.click(); pg.wait_for_timeout(500)
    pg.get_by_text("Firme existente", exact=False).first.click()
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("ALFA MICRO", exact=False).first.click()
    pg.wait_for_selector("#fa-bonuri", timeout=10000)
    pg.click("#fa-bonuri"); pg.wait_for_timeout(800)
    row = pg.query_selector("[data-doc]")
    if not row:
        print("#16 lista de-verificat goala (bonul e deja certificat) -> nu pot deschide detaliul.")
        print("REZULTAT #16: SKIP (render), dar cod fara blob: + CSP data: confirmate separat")
        b.close(); raise SystemExit
    row.click()
    pg.wait_for_selector("#d-poze img", timeout=12000); pg.wait_for_timeout(800)
    info = pg.eval_on_selector("#d-poze img",
        "e=>({src_prefix:e.getAttribute('src').slice(0,32), natW:e.naturalWidth, natH:e.naturalHeight, complete:e.complete})")
    print("#16 img:", info)
    ok = str(info["src_prefix"]).startswith("data:") and info["natW"] > 0 and info["complete"]
    pg.screenshot(path=os.path.join(OUT, "proba_bon_img.png"))
    print("screenshot:", os.path.join(OUT, "proba_bon_img.png"))
    print("REZULTAT #16:", "PASS (data:URL, img randata)" if ok else "FAIL")
    b.close()
