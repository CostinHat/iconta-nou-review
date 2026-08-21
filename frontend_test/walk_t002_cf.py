# -*- coding: utf-8 -*-
from w_auth import new_page
from walk_t002 import deschide_t002, shot
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t002(pg)
    shot(pg, '00_meniu_firma')
    # meniul firmei: ce butoane exista
    print('=== MENIU FIRMA ===')
    for sel in ['#fa-import','#fa-datefirma','#fa-facturi','#fa-declaratii','#fa-salariati','#fa-control','#fa-banca','#fa-casa']:
        e = pg.query_selector(sel)
        print(' ', sel, '->', (e.inner_text().strip() if e else 'ABSENT'))
    # control fiscal / semafor
    cf = pg.query_selector('#fa-control')
    if cf:
        cf.click(); pg.wait_for_timeout(2500)
        shot(pg, '30_control_fiscal')
        print('=== TEXT control fiscal ===')
        for sel in ['h2','h3','.cf-alerta','.alerta','.semafor','.cf-rand','.cf-titlu','li','.pastila','.mesaj']:
            for e in pg.query_selector_all(sel):
                t = e.inner_text().strip().replace(chr(10),' | ')
                if t and len(t) > 2:
                    print(' ', sel, '::', t[:200])
    b.close()
