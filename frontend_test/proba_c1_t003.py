# -*- coding: utf-8 -*-
"""Proba C1 pe tenant_003 (scenariul real): Popescu Ana (tichet=40) vs Ionescu Radu (tichet=0),
pontaj neconfirmat 08/2026. Verifica: banner .caseta-info GRI (nu rosu), Ana 'tichete blocate' GRI,
Radu FARA marcaj, zero rosu vechi."""
import os, sys, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, OUT, BAZA

TAG = sys.argv[1] if len(sys.argv) > 1 else "after"
with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    try:
        deschide_firma(pg)
        pg.click("#fa-salariati"); pg.wait_for_timeout(300)
        pg.wait_for_selector("h2.pf-titlu, .ecran-nota", timeout=12000); pg.wait_for_timeout(1500)
        html = pg.content()
        casete = pg.query_selector_all(".caseta-info")
        rez["banner_caseta_info_text"] = casete[0].inner_text().strip()[:160] if casete else "(niciun .caseta-info)"
        rez["banner_are_semafor_gri"] = bool(casete and casete[0].query_selector("span[style*='gri-semafor']"))
        randuri = pg.query_selector_all(".pf-frand")
        detalii = []
        for r in randuri:
            nume_el = r.query_selector(".pf-frand-nume")
            nume = nume_el.inner_text().strip() if nume_el else "?"
            subs = [s.inner_text().strip() for s in r.query_selector_all(".pf-frand-sub")]
            detalii.append({"nume": nume, "sub": subs})
        rez["randuri"] = detalii
        rez["rosu_vechi_pontaj_neconfirmat"] = "⚠ pontaj neconfirmat" in html
        rez["ecran_nota_rosu"] = 'ecran-nota" style="color:var(--rosu)' in html
        rez["tichete_blocate_prezent"] = "tichete blocate" in pg.inner_text("body")
        rez["console_errors"] = errs[:3]
        pg.screenshot(path=os.path.join(OUT, "proba_c1_t003_%s.png" % TAG), full_page=True)
    except Exception as e:
        rez["error"] = str(e)
        import traceback; traceback.print_exc()
        pg.screenshot(path=os.path.join(OUT, "proba_c1_t003_%s_ERR.png" % TAG), full_page=True)
    print(json.dumps(rez, ensure_ascii=False, indent=2))
    b.close()
