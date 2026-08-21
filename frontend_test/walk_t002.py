# -*- coding: utf-8 -*-
"""Audit vizual tenant_002 (Coafor Micro Neplatitor SRL, cabinet 1968) - parcurgere cap-coada.
Reutilizeaza w_auth (auth cabinet mintuit). Deschide firma 'Coafor Micro Neplatitor'."""
import os
from w_auth import BAZA, new_page

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't002_shots')
os.makedirs(OUT, exist_ok=True)

def shot(pg, nume):
    p = os.path.join(OUT, nume + '.png'); pg.screenshot(path=p, full_page=True); print('SHOT', p)

def deschide_t002(pg):
    pg.goto(BAZA + '/', wait_until='domcontentloaded')
    pg.wait_for_selector('.cab-card', timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text('Firme', exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text('Firme existente', exact=False).first.click(timeout=8000)
    pg.wait_for_selector('button.firme-rand', timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text('Coafor Micro Neplatitor', exact=False).first.click(timeout=8000)
    pg.wait_for_selector('#fa-import, #fa-datefirma', timeout=12000); pg.wait_for_timeout(400)

def txt(pg, sel):
    e = pg.query_selector(sel)
    return e.inner_text().strip() if e else None
