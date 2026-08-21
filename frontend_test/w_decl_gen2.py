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
        # trimestru: alege prin index 0 (default), doar generez
        g = pg.query_selector("text=Generează")
        rez["are_generare"] = bool(g)
        if g:
            g.click(); pg.wait_for_timeout(3000)
            shot(pg, "decl_20_generat")
            rez["dupa"] = (txt(pg, ".pf-container") or txt(pg, "main") or "")[:900]
            rez["actiuni"] = pg.eval_on_selector_all("button, a",
                "els=>els.map(e=>e.innerText.trim()).filter(t=>t && t.length<32 && /xml|duk|valid|desc|semn|depun|corect|edit/i.test(t))")
    except Exception as e:
        rez["error"] = str(e); shot(pg, "decl_gen2_ERR")
        import traceback; traceback.print_exc()
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:2800])
    b.close()
