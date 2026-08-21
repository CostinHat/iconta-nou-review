# -*- coding: utf-8 -*-
"""Audit vizual tenant_004 (Distributie Profit IC SRL, cabinet 1968) — parcurgere cap-coada.
Reutilizeaza w_auth (auth cabinet mintuit). Deschide firma 'Distributie Profit IC'."""
import os, sys
from w_auth import BAZA, new_page, INIT
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't004_shots')
os.makedirs(OUT, exist_ok=True)

def shot(pg, nume):
    p = os.path.join(OUT, nume + '.png'); pg.screenshot(path=p, full_page=True); print('SHOT', p)

def deschide_t004(pg):
    pg.goto(BAZA + '/', wait_until='domcontentloaded')
    pg.wait_for_selector('.cab-card', timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text('Firme', exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text('Firme existente', exact=False).first.click(timeout=8000)
    pg.wait_for_selector('button.firme-rand', timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text('Distributie Profit IC', exact=False).first.click(timeout=8000)
    pg.wait_for_selector('#fa-import, #fa-datefirma', timeout=12000); pg.wait_for_timeout(400)

if __name__ == '__main__':
    with sync_playwright() as pw:
        b, pg = new_page(pw)
        deschide_t004(pg)
        shot(pg, '00_meniu_firma')
        # textul butoanelor din meniul firmei
        for sel in ['#fa-import','#fa-datefirma','#fa-facturi','#fa-declaratii','#fa-salariati']:
            e = pg.query_selector(sel)
            print(sel, '->', (e.inner_text().strip() if e else 'ABSENT'))
        b.close()
