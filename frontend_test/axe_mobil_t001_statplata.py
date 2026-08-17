# -*- coding: utf-8 -*-
"""axe-core + emulare mobil (Pixel 5) pe Stat de plata tenant_001 (ecran atins: note SEPA/REGES).
Regula 14 addendum."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizual"))
from w_auth import new_page, INIT, BAZA
from walk_t001 import deschide_t001
from playwright.sync_api import sync_playwright
from vizual.axe_scan import AXE, AXE_RUN_JS, TITLE_ONLY_JS, scaneaza
from vizual.mobil_scan import TAP_OVERFLOW_JS

def deschide_statplata(pg):
    deschide_t001(pg)
    pg.click("#fa-salariati"); pg.wait_for_timeout(1800)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    # --- AXE (desktop) ---
    ctx = b.new_context(viewport={"width": 1280, "height": 1800}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); deschide_statplata(pg)
    viol, title_only = scaneaza(pg)
    print("=== AXE Stat plata tenant_001 ===")
    print("reguli incalcate:", len(viol))
    for v in viol:
        print("  -", v["id"], "| impact:", v["impact"], "| noduri:", v["n"], "|", v["help"][:70])
    print("title_only STRICT:", len(title_only["strict"]), "| glif:", len(title_only["glif"]), "| extra:", len(title_only["extra"]))
    if title_only["strict"]:
        print("  strict ex:", json.dumps(title_only["strict"][:4], ensure_ascii=False))
    ctx.close()
    # --- MOBIL (Pixel 5) ---
    pixel5 = pw.devices["Pixel 5"]; ctx2 = b.new_context(**pixel5); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page(); deschide_statplata(pg2)
    to = pg2.evaluate(TAP_OVERFLOW_JS)
    print("=== MOBIL Pixel 5 Stat plata ===")
    print("viewport:", to["viewport"], "| overflow-x:", to["overflow_orizontal"], "(scrollWidth", to["scrollWidth"], ")")
    print("tinte <44px:", len(to["tinte_mici"]))
    for t in to["tinte_mici"][:10]:
        print("  -", t["tag"], t["w"], "x", t["h"], "|", t["txt"], "|", t["cls"][:26])
    ctx2.close(); b.close(); print("DONE")
