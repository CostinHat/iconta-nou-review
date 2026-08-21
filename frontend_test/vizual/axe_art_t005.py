import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from w_auth import INIT, BAZA
from axe_scan import scaneaza, CONTRAST_RULES, LABEL_RULES
from mobil_scan import HOVER_TITLE_JS, TAP_OVERFLOW_JS
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = "denumire,um,cantitate,pret\nCiment,buc,100,50\nNisip,buc,200,\n"
CSVP = os.path.join(HERE, "_art.csv"); open(CSVP,"w",encoding="utf-8").write(CSV)
def nav(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("Constructii Profit Trim", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-import", timeout=12000); pg.wait_for_timeout(300)
    pg.click("#fa-import"); pg.wait_for_timeout(1000)
    pg.get_by_text("Articole", exact=False).first.click(); pg.wait_for_timeout(1000)
    if pg.query_selector("#mig-file") is None:
        for r in pg.query_selector_all(".mig-frand"):
            if "Constructii Profit Trim" in (r.inner_text() or ""): r.click(); break
        pg.wait_for_timeout(1000)
    pg.wait_for_selector("#mig-file", timeout=8000, state="attached")
    pg.query_selector("#mig-file").set_input_files(CSVP)
    pg.wait_for_selector(".mig-rand-rosu", timeout=8000); pg.wait_for_timeout(600)
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width":1200,"height":1800}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); nav(pg)
    viol, to = scaneaza(pg)
    print("=== AXE Import articole tenant_005 ===")
    print("contrast:", sum(v["n"] for v in viol if v["id"] in CONTRAST_RULES), " fara-eticheta:", sum(v["n"] for v in viol if v["id"] in LABEL_RULES), " title-only STRICT:", len(to["strict"]))
    ctx.close()
    px = pw.devices["Pixel 5"]; ctx2 = b.new_context(**px); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page(); nav(pg2)
    ht = pg2.evaluate(HOVER_TITLE_JS); to2 = pg2.evaluate(TAP_OVERFLOW_JS)
    print("=== MOBIL === info-touch:", len(ht["unice"]), " overflow-x:", to2["overflow_orizontal"], " tinte<44:", len(to2["tinte_mici"]))
    b.close()
os.remove(CSVP)
