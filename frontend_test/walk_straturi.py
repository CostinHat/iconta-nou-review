# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t005 import deschide_t005
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t005_shots")
STRATURI = ["Vector fiscal", "Solduri inițiale", "Solduri parteneri", "Asociați",
            "Mijloace fixe", "Istoric declarații", "Plan de conturi"]

def dump(pg, tag):
    print("=== " + tag + " ===")
    seen = set()
    for sel in ["h2", ".mig-intro", ".stare-goala", ".caseta-info", ".caseta-atentie", "label", "button.mig-buton", ".camp-eticheta"]:
        for e in pg.query_selector_all(sel):
            t = (e.inner_text() or "").strip().replace(chr(10), " | ")
            if t and 2 < len(t) < 160 and t not in seen:
                seen.add(t); print("  ", sel, "::", t[:150])

with sync_playwright() as pw:
    b, pg = new_page(pw)
    for i, strat in enumerate(STRATURI):
        deschide_t005(pg)
        pg.query_selector("#fa-import").click(); pg.wait_for_timeout(1000)
        el = pg.get_by_text(strat, exact=False).first
        if not el.count():
            print("ABSENT:", strat); continue
        el.click(); pg.wait_for_timeout(1400)
        # daca e wizard cu lista de firme, intra pe P2
        if pg.query_selector(".mig-frand"):
            for r in pg.query_selector_all(".mig-frand"):
                if "Constructii Profit Trim" in (r.inner_text() or ""):
                    r.click(); pg.wait_for_timeout(1300); break
        p = os.path.join(OUT, "9%d_%s.png" % (i, strat.split()[0].lower()))
        pg.screenshot(path=p, full_page=True)
        dump(pg, strat)
    b.close()
