# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t005 import deschide_t005, shot
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t005(pg)
    pg.query_selector("#fa-declaratii").click(); pg.wait_for_timeout(1500)
    # dropdown tip declaratie
    sel = pg.query_selector("select")
    if sel:
        opts = [ (o.get_attribute("value"), (o.inner_text() or "").strip()) for o in sel.query_selector_all("option") ]
        print("=== TIPURI DECLARATIE OFERITE (P2) ===")
        for v,t in opts: print("  ", repr(v), "::", t)
    b.close()
