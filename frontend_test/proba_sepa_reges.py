# -*- coding: utf-8 -*-
"""Provoaca blocajele SEPA (fara IBAN) si REGES (fara COR) pe Stat de plata tenant_001; citeste mesajele.
Verifica si modelul descarcat de salariati (acum cu cor,iban). Regula 14."""
import json, os
from w_auth import new_page
from walk_t001 import deschide_t001, shot
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t001_shots")

def texte(pg, sel, n=8):
    return pg.eval_on_selector_all(sel, "els=>els.map(e=>(e.innerText||'').trim()).filter(Boolean).slice(0,%d)" % n)

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t001(pg)
    pg.click("#fa-salariati"); pg.wait_for_timeout(1500)
    shot(pg, "sepa_0_statplata")

    # --- SEPA fara IBAN ---
    try:
        pg.get_by_text("Fișier plată card", exact=False).first.click(timeout=6000)
        pg.wait_for_timeout(1500)
        shot(pg, "sepa_1_dupa_click")
        print("SEPA mesaje:", json.dumps(texte(pg, ".eroare, .alert, [class*='eroare'], [class*='avert'], .dec-avert, .mig-eroare"), ensure_ascii=False))
        # dialog nativ? citeste body
        print("SEPA body-fragm:", json.dumps((pg.inner_text('body')[:600]), ensure_ascii=False)[:700])
    except Exception as e:
        print("SEPA click FAIL:", repr(e)[:160])

    # reincarca ecranul salariati
    deschide_t001(pg); pg.click("#fa-salariati"); pg.wait_for_timeout(1200)
    # --- REGES fara COR (buton Chei REGES sus) ---
    try:
        pg.get_by_text("Chei REGES", exact=False).first.click(timeout=6000)
        pg.wait_for_timeout(1500)
        shot(pg, "reges_1_dupa_click")
        print("REGES mesaje:", json.dumps(texte(pg, ".eroare, .alert, [class*='eroare'], [class*='avert'], .dec-avert, .mig-eroare"), ensure_ascii=False))
        print("REGES body-fragm:", json.dumps((pg.inner_text('body')[:600]), ensure_ascii=False)[:700])
    except Exception as e:
        print("REGES click FAIL:", repr(e)[:160])

    # --- model descarcat salariati (cor,iban) ---
    try:
        deschide_t001(pg); pg.click("#fa-import"); pg.wait_for_timeout(800)
        pg.get_by_text("Salariați", exact=False).first.click(timeout=6000); pg.wait_for_timeout(800)
        with pg.expect_download(timeout=6000) as di:
            pg.get_by_text("Descarcă model", exact=False).first.click()
        d = di.value; p = os.path.join(OUT, "model_salariati_descarcat.csv"); d.save_as(p)
        print("MODEL antet:", open(p, encoding="utf-8").read().splitlines()[0])
    except Exception as e:
        print("MODEL FAIL:", repr(e)[:160])
    b.close(); print("DONE")
