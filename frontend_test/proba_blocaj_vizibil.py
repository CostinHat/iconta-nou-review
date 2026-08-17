# -*- coding: utf-8 -*-
"""Proba: pe Stat de plata tenant_001 (fara IBAN, fara chei REGES) apar notele VIZIBILE .caseta-info
(SEPA + REGES indisponibile), nu doar title. Regula 14."""
import json
from w_auth import new_page
from walk_t001 import deschide_t001, shot
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t001(pg)
    pg.click("#fa-salariati"); pg.wait_for_timeout(1800)
    shot(pg, "blocaj_vizibil_statplata")
    note = pg.eval_on_selector_all(".caseta-info .ci-mesaj",
        "els=>els.map(e=>(e.innerText||'').trim())")
    print("CASETE-INFO vizibile:", json.dumps(note, ensure_ascii=False, indent=1))
    # confirma butoanele sunt disabled (blocajul ramane) DAR motivul e vizibil
    sepa_dis = pg.eval_on_selector("#sp-plata-card", "el=>el.disabled")
    reges_dis = pg.eval_on_selector("#sp-reges-poll", "el=>el.disabled")
    print("SEPA disabled:", sepa_dis, "| Raspunsuri REGES disabled:", reges_dis)
    b.close(); print("DONE")
