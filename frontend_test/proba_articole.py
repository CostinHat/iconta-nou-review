# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t005 import deschide_t005
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t005_shots")
CSV = "denumire,um,cantitate,pret\nCiment,buc,100,50\nNisip,buc,200,\n"  # Nisip fara pret
CSVP = os.path.join(OUT, "articole_fara_pret.csv"); open(CSVP, "w", encoding="utf-8").write(CSV)

def shot(pg, n):
    p = os.path.join(OUT, n + ".png"); pg.screenshot(path=p, full_page=True); print("SHOT", p)

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t005(pg)
    pg.query_selector("#fa-import").click(); pg.wait_for_timeout(1200)
    pg.get_by_text("Articole", exact=False).first.click(); pg.wait_for_timeout(1200)
    if pg.query_selector("#mig-file") is None:
        for r in pg.query_selector_all(".mig-frand"):
            if "Constructii Profit Trim" in (r.inner_text() or ""):
                r.click(); break
        pg.wait_for_timeout(1200)
    pg.wait_for_selector("#mig-file", timeout=8000, state="attached")
    pg.query_selector("#mig-file").set_input_files(CSVP)
    pg.wait_for_timeout(2000)
    shot(pg, "80_articole_invalid")
    print("=== TEXT ===")
    for sel in [".mig-eticheta", ".mig-rand", ".mig-rand-rosu"]:
        for e in pg.query_selector_all(sel):
            t = (e.inner_text() or "").strip().replace(chr(10), " | ")
            if t and 2 < len(t) < 200: print("  ", sel, "::", t[:190])
    b.close()
os.remove(CSVP)
