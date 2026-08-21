# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t005 import deschide_t005
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t005_shots")

def shot(pg, n):
    p = os.path.join(OUT, n + ".png"); pg.screenshot(path=p, full_page=True); print("SHOT", p)

def dump(pg, tag):
    print("=== TEXT", tag, "===")
    for sel in [".pf-frand-nume", ".pf-frand-sub", ".camp-eticheta", "#salariu-msg"]:
        for e in pg.query_selector_all(sel):
            t = (e.inner_text() or "").strip().replace(chr(10), " | ")
            if t and 1 < len(t) < 260: print("  ", sel, "::", t[:250])

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t005(pg)
    pg.query_selector("#fa-salariati").click(); pg.wait_for_timeout(2000)
    shot(pg, "70_stat_baza_lipsa")
    dump(pg, "70_stat_baza_lipsa")
    # apasa butonul Salariu
    btn = pg.query_selector("[data-salariu]")
    print("HAS [data-salariu]:", btn is not None)
    if btn:
        btn.click(); pg.wait_for_timeout(800)
        shot(pg, "71_form_salariu")
        pg.fill("#salariu-input", "5000")
        pg.fill("#salariu-data", "2026-08-14")
        pg.query_selector("#salariu-save").click(); pg.wait_for_timeout(2500)
        shot(pg, "72_dupa_salariu")
        dump(pg, "72_dupa_salariu")
    b.close()
