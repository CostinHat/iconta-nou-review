# -*- coding: utf-8 -*-
"""Genereaza D300 T2 -> captura rezultat -> cauta/apasa XML + DUK."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    try:
        deschide_firma(pg)
        pg.click("#fa-declaratii"); pg.wait_for_timeout(1200)
        pg.select_option("#dec-tip", "d300"); pg.wait_for_timeout(600)
        if pg.query_selector("#dec-trim"):
            pg.select_option("#dec-trim", "T2"); pg.wait_for_timeout(400)
        g = pg.query_selector("text=Generează")
        if g:
            g.click(); pg.wait_for_timeout(2500)
            shot(pg, "decl_20_generat")
            rez["dupa_generare"] = (txt(pg, ".pf-container") or txt(pg, "main") or "")[:800]
            rez["butoane_dupa"] = pg.eval_on_selector_all("button, a",
                "els=>els.map(e=>e.innerText.trim()).filter(t=>t && t.length<30 && (/xml|duk|valid|desc|genere|semn|depun/i.test(t)))")
            # incearca XML
            for et in ["Descarcă XML", "Descarca XML", "XML", "Validează DUK", "Valideaza DUK", "DUK"]:
                el = pg.query_selector("text=%s" % et)
                if el and not el.is_disabled():
                    rez.setdefault("actiuni_disponibile", []).append(et)
    except Exception as e:
        rez["error"] = str(e); shot(pg, "decl_gen_ERR")
        import traceback; traceback.print_exc()
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:3000])
    b.close()
