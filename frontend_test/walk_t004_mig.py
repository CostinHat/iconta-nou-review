# -*- coding: utf-8 -*-
import os
from w_auth import BAZA, new_page
from walk_t004 import deschide_t004, shot
from playwright.sync_api import sync_playwright

if __name__ == '__main__':
    with sync_playwright() as pw:
        b, pg = new_page(pw)
        deschide_t004(pg)
        pg.click('#fa-import')
        pg.wait_for_selector(".mig-card, .mig-strat, [class*='mig']", timeout=12000)
        pg.wait_for_timeout(800)
        shot(pg, '01_migrare_meniu')
        # enumera straturile
        cards = pg.query_selector_all("[class*='mig-card'], [class*='mig-strat'], .mig-card")
        print('NR carduri mig:', len(cards))
        for i,c in enumerate(cards):
            t = c.inner_text().strip().replace(chr(10),' | ')
            print(i, '::', t[:120])
        b.close()
