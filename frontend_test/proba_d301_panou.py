# -*- coding: utf-8 -*-
"""Traseu REAL D301: firma fara operatiuni -> generarea REFUZA pe zero-base, DAR panoul de operatiuni
se randeaza (fix chicken-and-egg 16.08) ca sa poata introduce + Regenereaza."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v
_d = json.load(urllib.request.urlopen(urllib.request.Request(
    BAZA + "/auth/login", json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode(),
    {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem(\"iconta_token\"," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem(\"iconta_user\"," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.dirname(os.path.abspath(__file__))

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(700)
    card = pg.query_selector(".cab-card:has(.cab-card-sinteza[data-cheie=\"declaratii\"])")
    if card:
        card.click()
    else:
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000)
        pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)
    if pg.query_selector("#dec-firma"):
        pg.select_option("#dec-firma", "8396"); pg.wait_for_timeout(1200)
    pg.wait_for_selector("#dec-tip option[value=\"d301\"]", timeout=8000, state="attached")
    pg.select_option("#dec-tip", "d301"); pg.wait_for_timeout(600)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2026"); pg.dispatch_event("#dec-an", "change")
    if pg.query_selector("#dec-luna"):
        pg.select_option("#dec-luna", "9")   # luna fara operatiuni D301 -> refuz zero-base
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_timeout(5000)
    # eroarea de generare (refuz zero-base) + panoul de operatiuni randat TOTUSI
    eroare = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    panou = pg.query_selector("#dec-d301-op") is not None
    add_form = pg.query_selector("#d301-tip") is not None or pg.query_selector("#d301-regen") is not None
    print("EROARE generare (refuz zero-base):", repr(eroare[:120]))
    print("PANOU #dec-d301-op randat:", panou)
    print("FORM adaugare/regen prezent:", add_form)
    pg.screenshot(path=os.path.join(OUT, "d301_panou_pe_eroare.png"), full_page=True)
    assert "zero" in eroare.lower() or "exigibilitate" in eroare.lower() or "operatiune" in eroare.lower(), \
        "asteptam eroarea de refuz zero-base: %r" % eroare[:150]
    assert panou, "PANOUL de operatiuni D301 trebuie randat CHIAR pe eroarea de generare (fix chicken-and-egg)"
    assert add_form, "formularul de adaugare/regenerare trebuie prezent ca utilizatorul sa introduca operatiuni"
    print("PROBA OK: refuz zero-base + panou editabil randat (utilizatorul poate introduce + Regenereaza)")
