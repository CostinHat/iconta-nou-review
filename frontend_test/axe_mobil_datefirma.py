# -*- coding: utf-8 -*-
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizual"))
from w_auth import new_page, INIT
from walk_t001 import deschide_t001
from playwright.sync_api import sync_playwright
from vizual.axe_scan import scaneaza
from vizual.mobil_scan import TAP_OVERFLOW_JS

def open_df(pg):
    deschide_t001(pg); pg.click("#fa-datefirma"); pg.wait_for_timeout(1200)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width":1280,"height":1800}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); open_df(pg)
    viol, title_only = scaneaza(pg)
    print("=== AXE Date firma ===  reguli:", len(viol))
    for v in viol: print("  -", v["id"], v["impact"], "noduri", v["n"])
    print("title_only STRICT/glif/extra:", len(title_only["strict"]), len(title_only["glif"]), len(title_only["extra"]))
    ctx.close()
    ctx2 = b.new_context(**pw.devices["Pixel 5"]); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page(); open_df(pg2)
    to = pg2.evaluate(TAP_OVERFLOW_JS)
    print("=== MOBIL Pixel5 ===  overflow-x:", to["overflow_orizontal"], "| tinte<44px:", len(to["tinte_mici"]))
    ctx2.close(); b.close(); print("DONE")
