# -*- coding: utf-8 -*-
"""Declaratii: meniu -> incearca o generare -> XML -> DUK. Captura + text."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    try:
        deschide_firma(pg)
        pg.click("#fa-declaratii"); pg.wait_for_timeout(1500)
        shot(pg, "decl_00_meniu")
        rez["meniu_text"] = (txt(pg, ".pf-container") or txt(pg, "main") or "")[:900]
        # butoane/carduri de declaratie disponibile
        rez["butoane"] = pg.eval_on_selector_all("button, .pac-card, [data-decl], a",
            "els=>els.slice(0,50).map(e=>e.innerText.trim().replace(/\\n/g,' ')).filter(t=>t && t.length<40)")
    except Exception as e:
        rez["meniu"] = {"error": str(e)}; shot(pg, "decl_00_ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:3500])
    b.close()
