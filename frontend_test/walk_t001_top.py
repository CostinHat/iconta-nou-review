# -*- coding: utf-8 -*-
"""Walk top-level tenant_001: re-deschide firma pt fiecare modul (meniul e modal)."""
import os
from w_auth import BAZA, new_page
from walk_t001 import deschide_t001, shot
from playwright.sync_api import sync_playwright

def dump(pg, tag):
    pg.wait_for_timeout(800)
    shot(pg, tag)
    for s in ['h1','h2','h3','.eroare','.alert','[class*="err"]','[class*="warn"]']:
        for e in pg.query_selector_all(s)[:5]:
            t=(e.inner_text() or '').strip().replace(chr(10),' ')
            if t: print(f'  [{tag}] {s}: {t[:110]}')

if __name__ == '__main__':
    steps = [
        ('#fa-datefirma', '20_date_firma'),
        ('#fa-salariati', '30_salariati'),
        ('#fa-declaratii','40_declaratii'),
        ('#fa-control',   '50_control_fiscal'),
        ('#fa-casa',      '60_casa'),
        ('#fa-banca',     '70_banca'),
        ('#fa-facturi',   '80_facturi'),
    ]
    with sync_playwright() as pw:
        b, pg = new_page(pw)
        for sel, tag in steps:
            try:
                deschide_t001(pg)
                pg.click(sel, timeout=8000)
                dump(pg, tag)
            except Exception as e:
                print(tag, 'FAIL', repr(e)[:160])
        b.close()
        print('DONE')
