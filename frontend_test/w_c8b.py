# -*- coding: utf-8 -*-
import os, json
from playwright.sync_api import sync_playwright
from w_auth import INIT, BAZA, OUT, deschide_firma, shot
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True, args=["--lang=ro-RO"])
    ctx = b.new_context(viewport={"width":900,"height":900}, locale="ro-RO"); ctx.add_init_script(INIT)
    pg = ctx.new_page(); rez={}
    try:
        deschide_firma(pg)
        pg.click("#fa-casa"); pg.wait_for_timeout(1500)
        # focus pe input date + screenshot doar pe zona
        di = pg.query_selector("input[type=date]")
        rez["are_input"]=bool(di)
        di.screenshot(path=os.path.join(OUT,"t003_c8_input_roRO.png"))
        # citeste ce format afiseaza (nu se poate direct; capturam)
    except Exception as e:
        rez["error"]=str(e)
    print(json.dumps(rez, ensure_ascii=False)); b.close()
