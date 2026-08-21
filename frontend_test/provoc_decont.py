# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t005 import deschide_t005
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t005_shots")
with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t005(pg)
    pg.query_selector("#fa-datefirma").click(); pg.wait_for_timeout(1800)
    # seteaza Periodicitate TVA la gol (""), pastreaza platitor=Da, salveaza
    sel = pg.query_selector("#vf-tip_decont")
    print("HAS #vf-tip_decont:", sel is not None)
    if sel:
        sel.select_option(value="")
        pg.wait_for_timeout(300)
        # click Salveaza
        pg.get_by_text("Salvează", exact=True).first.click()
        pg.wait_for_timeout(1200)
        p = os.path.join(OUT, "95_decont_provocat.png"); pg.screenshot(path=p, full_page=True); print("SHOT", p)
        print("=== erori camp ===")
        for e in pg.query_selector_all(".msg-eroare, .camp-eroare, [class*=eroare]"):
            t = (e.inner_text() or "").strip()
            if t and 2 < len(t) < 200: print("  ::", t[:190])
    b.close()
