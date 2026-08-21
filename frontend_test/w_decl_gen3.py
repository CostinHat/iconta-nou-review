# -*- coding: utf-8 -*-
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt
with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    try:
        deschide_firma(pg)
        pg.click("#fa-declaratii"); pg.wait_for_timeout(1200)
        pg.select_option("#dec-tip", "d300"); pg.wait_for_timeout(700)
        c = pg.query_selector("text=Continuă")
        if c and not c.is_disabled():
            c.click(); pg.wait_for_timeout(1800); shot(pg, "decl_15_pas2")
        g = pg.query_selector("text=Generează")
        rez["gaseste_genereaza"] = bool(g)
        if g:
            g.click(); pg.wait_for_timeout(3500); shot(pg, "decl_20_generat")
            rez["dupa"] = (txt(pg, ".pf-container") or txt(pg, "main") or "")[:900]
            rez["actiuni"] = pg.eval_on_selector_all("button,a", "els=>els.map(e=>e.innerText.trim()).filter(t=>t&&t.length<34&&/xml|duk|valid|desc|semn|depun|corect/i.test(t))")
        else:
            rez["pas2_text"] = (txt(pg, ".pf-container") or "")[:500]
    except Exception as e:
        rez["error"] = str(e); shot(pg, "decl_gen3_ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:2600])
    b.close()
