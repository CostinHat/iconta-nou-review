# -*- coding: utf-8 -*-
"""Conduce D112 prin wizardul Declaratii pt tenant_001, luna 06/2026: genereaza + DUKIntegrator.
Citeste ce scrie pe ecran (Regula 14)."""
import json
from w_auth import new_page
from walk_t001 import deschide_t001, shot
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t001(pg)
    pg.click("#fa-declaratii"); pg.wait_for_timeout(1200)
    # enumera tipurile
    opts = pg.eval_on_selector_all("#dec-tip option",
        "els=>els.map(o=>({v:o.value,t:(o.textContent||'').trim()}))")
    print("TIPURI:", json.dumps(opts, ensure_ascii=False))
    # alege D112
    pg.select_option("#dec-tip", "d112"); pg.wait_for_timeout(500)
    # perioada: an 2026, luna 6
    try:
        pg.fill("#dec-an", "2026")
    except Exception as e: print("an fill:", e)
    try:
        pg.select_option("#dec-luna", "6")
    except Exception as e: print("luna sel:", e)
    pg.wait_for_timeout(300)
    shot(pg, "d112_1_pas1")
    pg.click("#dec-continua"); pg.wait_for_timeout(4500)
    shot(pg, "d112_2_rezultat")
    # citeste panoul de rezultat
    panou = {
        "ok": pg.eval_on_selector_all(".dec-ok","els=>els.map(e=>e.innerText.trim())"),
        "avert_cap": pg.eval_on_selector_all(".dec-avert-cap","els=>els.map(e=>e.innerText.trim())"),
        "erori_pre": pg.eval_on_selector_all(".dec-xml-pre","els=>els.slice(0,2).map(e=>e.innerText.trim().slice(0,600))"),
        "eroare": pg.eval_on_selector_all(".eroare,[class*='eroare']","els=>els.map(e=>e.innerText.trim()).filter(Boolean).slice(0,6)"),
        "are_xml": bool(pg.query_selector(".dec-xml")),
        "h2": pg.eval_on_selector_all("h2","els=>els.map(e=>e.innerText.trim())"),
    }
    print("PANOU:", json.dumps(panou, ensure_ascii=False, indent=1)[:2500])
    b.close(); print("DONE")
