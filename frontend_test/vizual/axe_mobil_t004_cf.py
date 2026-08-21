# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # frontend_test
from w_auth import INIT, BAZA
from axe_scan import scaneaza, CONTRAST_RULES
from mobil_scan import HOVER_TITLE_JS, TAP_OVERFLOW_JS
from playwright.sync_api import sync_playwright

def nav_cf(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("Distributie Profit IC", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-control", timeout=12000); pg.wait_for_timeout(300)
    pg.click("#fa-control")
    pg.wait_for_selector(".pf-titlu", timeout=14000); pg.wait_for_timeout(2200)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    # DESKTOP axe
    ctx = b.new_context(viewport={"width":1200,"height":1800}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); nav_cf(pg)
    viol, title_only = scaneaza(pg)
    contrast = sum(v["n"] for v in viol if v["id"] in CONTRAST_RULES)
    print("=== AXE Control fiscal tenant_004 ===")
    print("reguli violate:", [(v["id"], v["impact"], v["n"]) for v in viol])
    print("contrast noduri:", contrast)
    print("title-only STRICT:", len(title_only["strict"]), " GLIF:", len(title_only["glif"]), " EXTRA:", len(title_only["extra"]))
    for r in title_only["extra"][:5]: print("   extra:", r["cls"], "::", r["title"][:50])
    ctx.close()
    # MOBIL Pixel 5
    px = pw.devices["Pixel 5"]; ctx2 = b.new_context(**px); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page(); nav_cf(pg2)
    ht = pg2.evaluate(HOVER_TITLE_JS); to = pg2.evaluate(TAP_OVERFLOW_JS)
    print("=== MOBIL (Pixel 5) Control fiscal ===")
    print("title total:", ht["total_title"], " info UNICA pe touch:", len(ht["unice"]))
    for u in ht["unice"][:5]: print("   unic:", u["cls"], "::", u["title"][:50])
    print("overflow-x:", to["overflow_orizontal"], " tinte <44px:", len(to["tinte_mici"]))
    b.close()
