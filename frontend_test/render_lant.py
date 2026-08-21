# -*- coding: utf-8 -*-
"""Randare autentificata (rule 9) pentru lantul import: ecran Mijloace fixe (Lot 1 amortizare),
Date firma (Q1), Solduri (Q10). Navigare de la ecranul principal. Firma: ALFA MICRO (tenant_013)."""
import os, json, urllib.request, traceback
from playwright.sync_api import sync_playwright

BAZA = "http://127.0.0.1:8010"
OUT = os.path.dirname(os.path.abspath(__file__))
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


def deschide_firma(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-mijloace, #fa-datefirma, #fa-import", timeout=12000); pg.wait_for_timeout(400)


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1600}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    rez = {}

    # --- LOT 1: Mijloace fixe ---
    try:
        deschide_firma(pg)
        pg.click("#fa-mijloace"); pg.wait_for_timeout(400)
        pg.wait_for_selector(".fd-tabel, .ecran-nota", timeout=12000); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(OUT, "lant_mijloace_fixe.png"), full_page=True)
        # extrage randurile (cod, amortizat, ramas, metoda) din tabel
        rows = pg.eval_on_selector_all(".fd-tabel tbody tr",
            "trs => trs.map(tr => Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim()))")
        intro = pg.eval_on_selector(".pf-intro", "e=>e.innerText") if pg.query_selector(".pf-intro") else None
        rez["mijloace"] = {"rows": rows, "intro": intro}
    except Exception as e:
        rez["mijloace"] = {"error": str(e)}; pg.screenshot(path=os.path.join(OUT, "lant_mijloace_fixe_ERR.png"))
        traceback.print_exc()

    # --- Q1: Date firma ---
    try:
        deschide_firma(pg)
        pg.click("#fa-datefirma"); pg.wait_for_timeout(600)
        pg.wait_for_selector("input, .fd-tabel, form, .pf-titlu", timeout=12000); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(OUT, "lant_date_firma_Q1.png"), full_page=True)
        rez["date_firma"] = {"titlu": pg.eval_on_selector(".pf-titlu", "e=>e.innerText") if pg.query_selector(".pf-titlu") else "(fara titlu)"}
    except Exception as e:
        rez["date_firma"] = {"error": str(e)}; pg.screenshot(path=os.path.join(OUT, "lant_date_firma_ERR.png"))
        traceback.print_exc()

    # --- Q10: Solduri (prin Import date) ---
    try:
        deschide_firma(pg)
        pg.click("#fa-import"); pg.wait_for_timeout(700)
        # meniul de migrare per firma: gaseste stratul Solduri
        pg.wait_for_selector("body", timeout=8000); pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, "lant_import_meniu.png"), full_page=True)
        sol = pg.get_by_text("Solduri", exact=False).first
        sol.click(timeout=8000); pg.wait_for_timeout(700)
        pg.screenshot(path=os.path.join(OUT, "lant_solduri_Q10.png"), full_page=True)
        rez["solduri"] = {"ok": True}
    except Exception as e:
        rez["solduri"] = {"error": str(e)}; pg.screenshot(path=os.path.join(OUT, "lant_solduri_ERR.png"))
        traceback.print_exc()

    print(json.dumps(rez, ensure_ascii=False, indent=2))
    b.close()
