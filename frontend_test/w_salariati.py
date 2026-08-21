# -*- coding: utf-8 -*-
"""Salariati: valid -> preview -> SALVARE reala -> confirmare -> ecranul unde apar. + card list complet."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt, OUT, BAZA

VALID = os.path.join(OUT, "valid_salariati.csv")
open(VALID, "w", encoding="utf-8").write(
    "nume,prenume,cnp,data angajare,norma,brut,judet\n"
    "Popescu,Ana,2900215410011,2020-01-15,intreaga,5000,B\n"
    "Ionescu,Radu,1850715410012,2021-03-01,intreaga,6000,CJ\n")

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    try:
        deschide_firma(pg)
        rez["carduri_firma"] = pg.eval_on_selector_all("[id^=fa-]",
            "els => els.map(e => e.id + '=' + e.innerText.trim().split(String.fromCharCode(10))[0])")
        pg.click("#fa-import"); pg.wait_for_timeout(700)
        pg.get_by_text("Salariați", exact=False).first.click(timeout=8000); pg.wait_for_timeout(700)
        pg.set_input_files("#mig-file", VALID); pg.wait_for_timeout(1500)
        shot(pg, "sal_10_preview_valid")
        rez["banda"] = txt(pg, ".mig-coer")
        rez["salveaza_disabled_preview"] = pg.eval_on_selector("#mig-salveaza-sal", "e=>e.disabled")
        rez["randuri_preview"] = pg.eval_on_selector_all(".mig-sold-rand", "els=>els.map(e=>e.innerText.replace(/\\n/g,' | '))")
        # SALVARE reala
        if not pg.query_selector("#mig-salveaza-sal").is_disabled():
            pg.click("#mig-salveaza-sal"); pg.wait_for_timeout(2000)
            shot(pg, "sal_11_dupa_salvare")
            rez["dupa_salvare_url_titlu"] = txt(pg, ".pf-titlu") or txt(pg, "h2") or txt(pg, ".mig-intro")
            rez["mesaj_confirmare"] = txt(pg, ".msg-ok") or txt(pg, ".mig-eroare") or txt(pg, "[class*=ok]") or "(niciun mesaj de confirmare gasit)"
            rez["body_dupa"] = (txt(pg, "main") or txt(pg, "body") or "")[:1200]
    except Exception as e:
        rez["error"] = str(e); shot(pg, "sal_ERR")
        import traceback; traceback.print_exc()
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:3500])
    b.close()
