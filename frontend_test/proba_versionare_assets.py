# -*- coding: utf-8 -*-
"""Proba: dupa stampilarea ?v=<hash>, SPA-ul se incarca fara 404 pe module.
Verifica STATUS pe TOATE cererile de retea (.js/.css), erori de consola, si randare
login -> cabinet -> firma -> emitere. Screenshot. Auth ca in proba_ui_emitere.py."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright

BAZA = os.environ.get("FE_BAZA", "http://127.0.0.1:8010")
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

net = []        # (url, status, resource_type)
console_err = []
page_err = []

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1100, "height": 1500}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.on("response", lambda r: net.append((r.url, r.status, r.request.resource_type)))
    pg.on("console", lambda m: console_err.append((m.type, m.text)) if m.type == "error" else None)
    pg.on("pageerror", lambda e: page_err.append(str(e)))

    pg.goto(BAZA + "/", wait_until="networkidle")
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
        if pg.query_selector("#em-tva-nu"):
            pg.click("#em-tva-nu"); pg.wait_for_timeout(150)
        pg.click("#em-nu"); pg.wait_for_timeout(300)
        pg.wait_for_selector("#em-salveaza-config2", timeout=8000)
        pg.click("#em-salveaza-config2")
    pg.wait_for_selector("#em-add-linie", timeout=12000); pg.wait_for_timeout(500)
    ecran_ok = pg.query_selector("#em-add-linie") is not None
    pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(OUT, "proba_versionare_assets.png"), full_page=True)
    b.close()

# ---- analiza ----
assets = [(u, s, t) for (u, s, t) in net if (".js" in u or ".css" in u)]
rele = [(u, s, t) for (u, s, t) in assets if s >= 400]
print("=== cereri asset (.js/.css): %d ; cu status >=400: %d ===" % (len(assets), len(rele)))
for u, s, t in sorted(set(assets)):
    marca = "  BAD" if s >= 400 else "ok"
    print("  [%s] %d  %s" % (marca, s, u.replace(BAZA, "")))
print("=== erori consola: %d ; pageerror: %d ===" % (len(console_err), len(page_err)))
for t, m in console_err: print("  CONSOLE", t, m[:200])
for m in page_err: print("  PAGEERR", m[:200])
print("=== ecran emitere randat: %s ===" % ecran_ok)
print("=== screenshot:", os.path.join(OUT, "proba_versionare_assets.png"))
verdict = (not rele) and (not page_err) and ecran_ok
print("VERDICT:", "PASS" if verdict else "FAIL")
