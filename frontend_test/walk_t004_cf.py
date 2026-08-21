# -*- coding: utf-8 -*-
from w_auth import new_page
from walk_t004 import deschide_t004, shot
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t004(pg)
    pg.click('#fa-control'); pg.wait_for_timeout(2000)
    shot(pg,'30_control_fiscal')
    print('=== TEXT control fiscal ===')
    for sel in ['h2','h3','.cf-alerta','.alerta','.semafor','.cf-rand','.cf-titlu','li']:
        for e in pg.query_selector_all(sel):
            t=e.inner_text().strip().replace(chr(10),' | ')
            if t and len(t)>2: print(' ',sel,'::',t[:160])
    b.close()
