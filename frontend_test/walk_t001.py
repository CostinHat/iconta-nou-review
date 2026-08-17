# -*- coding: utf-8 -*-
"""Audit vizual tenant_001 (Panificatie Salarii Speciale SRL, cabinet 1968) - cap-coada.
Reutilizeaza w_auth (auth cabinet Prisma mintuit). Deschide firma 'Panificatie Salarii Speciale'."""
import os
from w_auth import BAZA, new_page

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't001_shots')
os.makedirs(OUT, exist_ok=True)

def shot(pg, nume):
    p = os.path.join(OUT, nume + '.png'); pg.screenshot(path=p, full_page=True); print('SHOT', p)

def deschide_t001(pg):
    pg.goto(BAZA + '/', wait_until='domcontentloaded')
    pg.wait_for_selector('.cab-card', timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text('Firme', exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text('Firme existente', exact=False).first.click(timeout=8000)
    pg.wait_for_selector('button.firme-rand', timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text('Panificatie Salarii Speciale', exact=False).first.click(timeout=8000)
    pg.wait_for_selector('#fa-import, #fa-datefirma', timeout=12000); pg.wait_for_timeout(400)

def txt(pg, sel):
    e = pg.query_selector(sel)
    return e.inner_text().strip() if e else None

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b, pg = new_page(pw)
        deschide_t001(pg)
        shot(pg, '00_meniu_firma')
        for sel in ['#fa-import','#fa-datefirma','#fa-facturi','#fa-banca','#fa-casa',
                    '#fa-declaratii','#fa-salariati','#fa-control','#fa-semafor']:
            e = pg.query_selector(sel)
            print(sel, '->', (e.inner_text().strip().replace(chr(10),' ') if e else 'ABSENT'))
        b.close()
