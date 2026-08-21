# -*- coding: utf-8 -*-
"""Proba #1/#3: statul de plata se RANDEAZA cand pontajul lunii nu e confirmat (nu mai moare ecranul).
Firma ALFA MICRO (cabinet fe_test), salariat POPESCU cu tichete>0 + pontaj neconfirmat pe luna curenta."""
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

OUT = os.path.join(os.path.dirname(__file__), "proba_pontaj_neconfirmat.png")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1280, "height": 1500})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(500)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(400)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-salariati", timeout=10000); pg.wait_for_timeout(300)
    pg.click("#fa-salariati")
    pg.wait_for_selector("h2.pf-titlu, .ecran-nota", timeout=12000); pg.wait_for_timeout(1500)
    body = pg.inner_text("body")
    pontaj_btns = pg.query_selector_all("[data-pontaj]")
    banner = "Pontajul lunii nu e confirmat" in body
    rand_marker = "pontaj neconfirmat" in body.lower()
    eroare_veche = ("Nu am putut" in body and "statul de plat" in body.lower())
    rand_nume = "POPESCU" in body
    print("=== PROBA #1/#3 (ALFA MICRO / POPESCU, pontaj neconfirmat aug 2026) ===")
    print("banner global 'Pontajul lunii nu e confirmat':", banner)
    print("marcaj per-rand 'pontaj neconfirmat':", rand_marker)
    print("randul salariatului (POPESCU) randat:", rand_nume)
    print("butoane Pontaj accesibile:", len(pontaj_btns))
    print("mesaj vechi 'Nu am putut incarca statul de plata':", eroare_veche)
    print("console errors:", errs[:3])
    pg.screenshot(path=OUT, full_page=True)
    print("screenshot:", OUT)
    ok = banner and rand_nume and len(pontaj_btns) >= 1 and not eroare_veche
    print("REZULTAT:", "PASS" if ok else "FAIL")
    b.close()
