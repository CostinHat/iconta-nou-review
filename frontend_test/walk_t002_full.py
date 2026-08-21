# -*- coding: utf-8 -*-
from w_auth import new_page
from walk_t002 import deschide_t002, shot
from playwright.sync_api import sync_playwright

ECRANE = [
    ("#fa-import",   "10_import"),
    ("#fa-datefirma","20_datefirma"),
    ("#fa-facturi",  "40_facturi"),
    ("#fa-banca",    "41_banca"),
    ("#fa-casa",     "42_casa"),
    ("#fa-salariati","43_salariati"),
    ("#fa-declaratii","50_declaratii"),
]

def dump_text(pg, tag):
    print("=== TEXT", tag, "===")
    for sel in ['h1','h2','h3','.gol','.empty','.stare-goala','.avert','.eroare','.alerta','button']:
        for e in pg.query_selector_all(sel):
            t = (e.inner_text() or '').strip().replace(chr(10),' | ')
            if t and 2 < len(t) < 120:
                print("  ", sel, "::", t[:110])

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t002(pg)
    for sel, nume in ECRANE:
        el = pg.query_selector(sel)
        if not el:
            print("ABSENT", sel); continue
        el.click(); pg.wait_for_timeout(1800)
        shot(pg, nume)
        dump_text(pg, nume)
        # revin la meniul firmei
        back = pg.query_selector('.fa-inapoi, [aria-label="Inapoi"], .modal-inchide')
        # daca e modal, inchide; altfel re-deschide firma
        try:
            deschide_t002(pg)
        except Exception:
            pg.goto(pg.url)
    b.close()
