# -*- coding: utf-8 -*-
"""Proba #7/#8: formularul Salariat nou are * pe Salariu brut si Ocupatie(COR) si blocheaza submit fara ele."""
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
OUT = os.path.join(os.path.dirname(__file__), "proba_salariat_oblig.png")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1100, "height": 1400}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(500)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(400)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-salariati", timeout=10000)
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-salariat-nou", timeout=12000)
    pg.click("#sp-salariat-nou")
    pg.wait_for_selector("#sn-salveaza", timeout=10000); pg.wait_for_timeout(400)
    # asterisks present?
    brut_lbl = pg.eval_on_selector("label[for=sn-salariu_brut]", "e=>e.innerHTML")
    cor_lbl = pg.eval_on_selector("label[for=sn-cor-cauta]", "e=>e.innerHTML")
    print("brut label has *:", "oblig" in brut_lbl)
    print("cor label has *:", "oblig" in cor_lbl)
    # fill only nume, submit -> should block on brut
    pg.fill("#sn-nume", "TEST OBLIG")
    pg.click("#sn-salveaza"); pg.wait_for_timeout(400)
    err_brut = pg.query_selector('.msg-eroare[data-camp="sn-salariu_brut"]')
    print("submit fara brut -> eroare brut:", bool(err_brut), (err_brut.inner_text() if err_brut else ""))
    # fill brut, submit -> should block on COR
    pg.fill("#sn-salariu_brut", "5000")
    pg.click("#sn-salveaza"); pg.wait_for_timeout(400)
    err_cor = pg.query_selector('.msg-eroare[data-camp="sn-cor-cauta"]')
    print("submit fara COR -> eroare COR:", bool(err_cor), (err_cor.inner_text() if err_cor else ""))
    pg.screenshot(path=OUT, full_page=True)
    print("screenshot:", OUT)
    ok = ("oblig" in brut_lbl) and ("oblig" in cor_lbl) and bool(err_brut) and bool(err_cor)
    print("REZULTAT:", "PASS" if ok else "FAIL")
    b.close()
