# -*- coding: utf-8 -*-
import os, json
from playwright.sync_api import sync_playwright
from w_auth import INIT, BAZA, OUT, deschide_firma, shot
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    # locale RO — ca un utilizator roman
    ctx = b.new_context(viewport={"width":1200,"height":1400}, locale="ro-RO"); ctx.add_init_script(INIT)
    pg = ctx.new_page(); rez={}
    try:
        deschide_firma(pg)
        pg.click("#fa-casa"); pg.wait_for_timeout(1500)
        shot(pg, "c8_casa_roRO")
        di = pg.query_selector("input[type=date]")
        rez["are_input_date"] = bool(di)
        rez["placeholder_app"] = di.get_attribute("placeholder") if di else None
        rez["locale_pagina"] = pg.evaluate("navigator.language")
    except Exception as e:
        rez["error"]=str(e); shot(pg,"c8_ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2))
    b.close()
