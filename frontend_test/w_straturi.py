# -*- coding: utf-8 -*-
"""Sweep straturi migrare: intra in fiecare, captura + noteaza (Descarca model? upload? intro)."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt

STRATURI = ["Vector fiscal", "Solduri inițiale", "Solduri parteneri", "Asociați",
            "Mijloace fixe", "Istoric declarații", "Plan de conturi",
            "Articole și stoc inițial", "Rețete (HoReCa)"]

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    for i, s in enumerate(STRATURI):
        cheie = "str_%02d_%s" % (i, s.split()[0].lower().replace("ț","t").replace("ș","s").replace("ă","a").replace("â","a"))
        try:
            deschide_firma(pg)
            pg.click("#fa-import"); pg.wait_for_timeout(700)
            pg.get_by_text(s, exact=False).first.click(timeout=8000); pg.wait_for_timeout(1200)
            shot(pg, cheie)
            rez[s] = {
                "intro": txt(pg, ".mig-intro") or txt(pg, ".pf-intro"),
                "descarca_model": bool(pg.query_selector("text=Descarcă model") or pg.query_selector("text=Descarca model")),
                "upload_input": bool(pg.query_selector("#mig-file")),
                "titlu": txt(pg, ".pf-titlu") or txt(pg, "h2"),
                "camp_ajutor": [e.inner_text().strip() for e in pg.query_selector_all(".camp-ajutor")][:3],
                "oblig": len(pg.query_selector_all(".oblig")),
            }
        except Exception as e:
            rez[s] = {"error": str(e)}; shot(pg, cheie + "_ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:4000])
    b.close()
