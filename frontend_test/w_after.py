# -*- coding: utf-8 -*-
"""Randare DUPA fix: C7 (D300 T3 genereaza fara eroare de luna), C6 (dropdown motiv real), C5 (acord singular)."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt
with sync_playwright() as pw:
    b, pg = new_page(pw); rez={}
    # C6: dropdown motiv real
    try:
        deschide_firma(pg); pg.click("#fa-declaratii"); pg.wait_for_timeout(1200)
        rez["C6_optiuni"] = [o for o in pg.eval_on_selector("select", "s=>Array.from(s.options).map(o=>o.text)") if "D301" in o or "D390" in o]
    except Exception as e: rez["C6_err"]=str(e)
    # C7: genereaza D300 T3 -> nu mai apare "luna invalida"
    try:
        pg.select_option("#dec-tip","d300"); pg.wait_for_timeout(700)
        c=pg.query_selector("text=Continuă");
        if c and not c.is_disabled(): c.click(); pg.wait_for_timeout(1500)
        g=pg.query_selector("text=Generează")
        if g: g.click(); pg.wait_for_timeout(3000)
        shot(pg,"after_C7_d300")
        body=txt(pg,".pf-container") or ""
        rez["C7_are_eroare_luna"] = "luna invalidă" in body or "luna invalida" in body
        rez["C7_are_randuri_manuale"] = "Rânduri manuale" in body or "Randuri manuale" in body
    except Exception as e: rez["C7_err"]=str(e)
    # C5: Date firma acord
    try:
        deschide_firma(pg); pg.click("#fa-datefirma"); pg.wait_for_timeout(1500)
        shot(pg,"after_C5_datefirma")
        cap=pg.query_selector(".dec-avert-cap")
        rez["C5_caseta"] = cap.inner_text().strip() if cap else "(fara caseta - profil complet?)"
    except Exception as e: rez["C5_err"]=str(e)
    print(json.dumps(rez, ensure_ascii=False, indent=2)); b.close()
