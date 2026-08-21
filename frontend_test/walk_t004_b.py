# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t004 import deschide_t004, shot
from playwright.sync_api import sync_playwright

def dump(pg, label):
    print('=== TEXT', label, '===')
    for sel in ['h1','h2','h3','.pf-titlu','.ecran-nota','.stare-goala','.mig-eroare','.decl-rand','.decl-card']:
        for e in pg.query_selector_all(sel):
            t=e.inner_text().strip().replace(chr(10),' | ')
            if t: print(' ',sel,'::',t[:140])

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t004(pg)
    # Date firma
    pg.click('#fa-datefirma'); pg.wait_for_timeout(1500)
    shot(pg,'10_date_firma'); dump(pg,'DATE FIRMA')
    b.close()
    b, pg = new_page(pw)
    deschide_t004(pg)
    # Declaratii
    pg.click('#fa-declaratii'); pg.wait_for_timeout(1800)
    shot(pg,'20_declaratii'); dump(pg,'DECLARATII')
    b.close()
