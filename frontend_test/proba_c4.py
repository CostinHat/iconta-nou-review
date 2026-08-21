# -*- coding: utf-8 -*-
"""Proba C4: la mijloace fixe (bugul numit) butonul 'Descarca model (CSV)' descarca un model, iar modelul
REINCARCAT e recunoscut de parser (dovada ca formatul = cel real, inclusiv contul de imobilizare)."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import INIT, BAZA, OUT

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1600}, accept_downloads=True)
    ctx.add_init_script(INIT)
    pg = ctx.new_page(); rez = {}
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    try:
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
        pg.get_by_text("Comert Micro TVA", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000); pg.wait_for_timeout(300)
        pg.click("#fa-import"); pg.wait_for_timeout(600)
        pg.get_by_text("Mijloace fixe", exact=False).first.click(timeout=8000); pg.wait_for_timeout(700)
        intro = pg.query_selector(".mig-intro").inner_text()
        rez["intro_mijloace"] = intro
        rez["intro_are_cont_imobilizare"] = "cont imobilizare" in intro
        btn = pg.query_selector("#mig-model")
        rez["buton_model_prezent"] = bool(btn)
        rez["buton_text"] = btn.inner_text() if btn else None
        pg.screenshot(path=os.path.join(OUT, "proba_c4_mijloace.png"), full_page=True)
        # descarca modelul
        with pg.expect_download() as di:
            btn.click()
        dl = di.value
        model_path = os.path.join(OUT, "model_mijloace_descarcat.csv")
        dl.save_as(model_path)
        with open(model_path, encoding="utf-8-sig") as f:
            rez["model_antet"] = f.readline().strip()
            rez["model_rand1"] = f.readline().strip()
        # REINCARCA modelul -> parserul il recunoaste?
        pg.set_input_files("#mig-file", model_path); pg.wait_for_timeout(1800)
        body = pg.inner_text("body")
        rez["preview_recunoaste"] = ("mijloace fixe" in body.lower()) and ("2" in body)
        randuri = [r.inner_text().replace(chr(10), " | ") for r in pg.query_selector_all(".mig-sold-rand")]
        rez["preview_randuri"] = randuri[:4]
        rez["console_errors"] = errs[:3]
        pg.screenshot(path=os.path.join(OUT, "proba_c4_mijloace_reincarca.png"), full_page=True)
    except Exception as e:
        rez["error"] = str(e)
        import traceback; traceback.print_exc()
        pg.screenshot(path=os.path.join(OUT, "proba_c4_ERR.png"), full_page=True)
    print(json.dumps(rez, ensure_ascii=False, indent=2))
    b.close()
