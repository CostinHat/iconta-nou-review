# -*- coding: utf-8 -*-
"""Flux generare declaratie: alege tip -> perioada -> genereaza -> XML -> DUK."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    try:
        deschide_firma(pg)
        pg.click("#fa-declaratii"); pg.wait_for_timeout(1500)
        sel = pg.query_selector("select")
        rez["optiuni_tip"] = pg.eval_on_selector("select", "s=>Array.from(s.options).map(o=>o.value+'='+o.text)")
        # alege D300 daca exista, altfel a doua optiune
        opts = pg.eval_on_selector("select", "s=>Array.from(s.options).map(o=>o.value)")
        alege = next((o for o in opts if o and 'd300' in o.lower() or o=='D300'), None) or (opts[1] if len(opts) > 1 else None)
        rez["ales"] = alege
        if alege:
            pg.select_option("select", alege); pg.wait_for_timeout(500)
            shot(pg, "decl_10_pas1")
            # dupa alegere pot aparea alte campuri (perioada). Capturez si continui.
            rez["dupa_alegere_selects"] = pg.eval_on_selector_all("select", "els=>els.map(s=>s.id+':'+Array.from(s.options).slice(0,6).map(o=>o.text).join('|'))")
            # apasa Continua
            cont = pg.query_selector("text=Continuă")
            if cont and not cont.is_disabled():
                cont.click(); pg.wait_for_timeout(1500)
                shot(pg, "decl_11_pas2")
                rez["pas2_text"] = (txt(pg, ".pf-container") or "")[:600]
                # cauta buton de generare
                for et in ["Generează", "Genereaza", "Continuă", "Descarcă XML", "Descarca XML", "Validează DUK"]:
                    el = pg.query_selector("text=%s" % et)
                    if el:
                        rez.setdefault("butoane_pas2", []).append(et + (" [disabled]" if el.is_disabled() else ""))
    except Exception as e:
        rez["error"] = str(e); shot(pg, "decl_flux_ERR")
        import traceback; traceback.print_exc()
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:3500])
    b.close()
