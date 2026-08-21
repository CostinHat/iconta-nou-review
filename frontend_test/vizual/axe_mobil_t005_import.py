# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # frontend_test
from w_auth import INIT, BAZA
from axe_scan import scaneaza, CONTRAST_RULES, LABEL_RULES
from mobil_scan import HOVER_TITLE_JS, TAP_OVERFLOW_JS
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = "nume,prenume,cnp,angajare,norma,ore,judet\nTestescu,Test,1960101227810,2024-01-08,intreaga,8,B\n"
CSVP = os.path.join(HERE, "_fara_salariu.csv")
open(CSVP, "w", encoding="utf-8").write(CSV)

def nav_import(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("Constructii Profit Trim", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-import", timeout=12000); pg.wait_for_timeout(300)
    pg.click("#fa-import"); pg.wait_for_timeout(1200)
    pg.get_by_text("Salariați", exact=False).first.click(); pg.wait_for_timeout(1200)
    if pg.query_selector("#mig-file") is None:
        for r in pg.query_selector_all(".mig-frand"):
            if "Constructii Profit Trim" in (r.inner_text() or ""):
                r.click(); break
        pg.wait_for_timeout(1200)
    pg.wait_for_selector("#mig-file", timeout=8000, state="attached")
    pg.query_selector("#mig-file").set_input_files(CSVP)
    pg.wait_for_selector(".caseta-atentie", timeout=8000); pg.wait_for_timeout(800)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width":1200,"height":1800}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); nav_import(pg)
    viol, title_only = scaneaza(pg)
    contrast = sum(v["n"] for v in viol if v["id"] in CONTRAST_RULES)
    label = sum(v["n"] for v in viol if v["id"] in LABEL_RULES)
    print("=== AXE Import salariati (preview respins) tenant_005 ===")
    print("reguli violate:", [(v["id"], v["impact"], v["n"]) for v in viol])
    print("contrast noduri:", contrast, " fara-eticheta noduri:", label)
    print("title-only STRICT:", len(title_only["strict"]), " GLIF:", len(title_only["glif"]))
    ctx.close()
    px = pw.devices["Pixel 5"]; ctx2 = b.new_context(**px); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page(); nav_import(pg2)
    ht = pg2.evaluate(HOVER_TITLE_JS); to = pg2.evaluate(TAP_OVERFLOW_JS)
    print("=== MOBIL (Pixel 5) Import salariati ===")
    print("title total:", ht["total_title"], " info UNICA pe touch:", len(ht["unice"]))
    print("overflow-x:", to["overflow_orizontal"], " tinte <44px:", len(to["tinte_mici"]))
    b.close()
os.remove(CSVP)
