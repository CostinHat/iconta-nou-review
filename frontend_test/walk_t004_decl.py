# -*- coding: utf-8 -*-
from w_auth import new_page
from walk_t004 import deschide_t004, shot
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t004(pg)
    pg.click('#fa-declaratii'); pg.wait_for_timeout(1500)
    # enumera optiunile din selectul Tip declaratie
    sel = pg.query_selector('select')
    if sel:
        opts = sel.query_selector_all('option')
        print('TIP DECLARATIE optiuni:')
        for o in opts:
            print('  val=',repr(o.get_attribute('value')),' text=',repr(o.inner_text().strip()))
    b.close()
