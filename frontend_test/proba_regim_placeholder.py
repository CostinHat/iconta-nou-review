# -*- coding: utf-8 -*-
"""Proba fix [alege]: Date firma pe tenant_001 (regim/tva/ic = NULL) NU afiseaza default fabricat;
selecturile arata "— alege —"; Salvarea fara alegere -> mesaje de eroare langa camp."""
import json
from w_auth import new_page
from walk_t001 import deschide_t001, shot
from playwright.sync_api import sync_playwright

def sel_state(pg, cid):
    return pg.eval_on_selector(f"#{cid}",
        "el => ({value: el.value, textAfisat: (el.options[el.selectedIndex]||{}).text || ''})")

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t001(pg)
    pg.click("#fa-datefirma"); pg.wait_for_timeout(1200)
    shot(pg, "fix_datefirma_1_initial")
    st = {c: sel_state(pg, "vf-"+c) for c in ("regim_fiscal","platitor_tva","operatiuni_ic","tip_decont")}
    print("STARE SELECTURI:", json.dumps(st, ensure_ascii=False))
    # provoaca blocajul: Salveaza fara a alege
    pg.click("#df-salveaza"); pg.wait_for_timeout(800)
    shot(pg, "fix_datefirma_2_dupa_salvare")
    erori = pg.eval_on_selector_all(".camp-eroare, .eroare-camp, [class*='eroare']",
        "els => els.map(e => (e.innerText||'').trim()).filter(Boolean).slice(0,12)")
    print("ERORI CAMP:", json.dumps(erori, ensure_ascii=False))
    b.close()
    print("DONE")
