import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from w_auth import INIT, BAZA
from axe_scan import scaneaza, CONTRAST_RULES, LABEL_RULES
from mobil_scan import HOVER_TITLE_JS, TAP_OVERFLOW_JS
from playwright.sync_api import sync_playwright

def nav(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("Constructii Profit Trim", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-salariati", timeout=12000); pg.wait_for_timeout(300)
    pg.click("#fa-salariati"); pg.wait_for_selector(".pf-frand-nume", timeout=12000); pg.wait_for_timeout(1500)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width":1200,"height":1800}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); nav(pg)
    viol, to = scaneaza(pg)
    contrast = sum(v["n"] for v in viol if v["id"] in CONTRAST_RULES)
    label = sum(v["n"] for v in viol if v["id"] in LABEL_RULES)
    print("=== AXE Stat de plata tenant_005 ===")
    print("reguli:", [(v["id"], v["impact"], v["n"]) for v in viol])
    print("contrast:", contrast, " fara-eticheta:", label, " title-only STRICT:", len(to["strict"]), " GLIF:", len(to["glif"]))
    ctx.close()
    px = pw.devices["Pixel 5"]; ctx2 = b.new_context(**px); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page(); nav(pg2)
    ht = pg2.evaluate(HOVER_TITLE_JS); to2 = pg2.evaluate(TAP_OVERFLOW_JS)
    print("=== MOBIL Pixel 5 ===")
    print("info UNICA pe touch:", len(ht["unice"]), " overflow-x:", to2["overflow_orizontal"], " tinte <44px:", len(to2["tinte_mici"]))
    b.close()
