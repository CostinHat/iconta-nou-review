# -*- coding: utf-8 -*-
"""Proba: pe Date firma, declarant_nume + declarant_functie au asterisc (ob) si Salvarea fara ele blocheaza
cu eroare pe camp (client-side, date_firma.js servit proaspat). Regula 14."""
import json
from w_auth import new_page
from walk_t001 import deschide_t001, shot
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t001(pg)
    pg.click("#fa-datefirma"); pg.wait_for_timeout(1200)
    # asterisc pe declarant_nume + declarant_functie?
    for k in ("declarant_nume", "declarant_functie", "declarant_prenume"):
        el = pg.query_selector(f"#df-{k}")
        lbl = pg.evaluate("(id)=>{const i=document.getElementById(id); if(!i)return null; const l=i.closest('.camp'); return l? l.querySelector('.oblig')? 'OBLIG*':'fara' : null;}", f"df-{k}")
        print(f"  {k}: asterisc={lbl}")
    # provoaca salvarea fara declarant
    pg.click("#df-salveaza"); pg.wait_for_timeout(800)
    shot(pg, "declarant_dupa_salvare")
    erori = pg.eval_on_selector_all("[class*='eroare']", "els=>els.map(e=>(e.innerText||'').trim()).filter(t=>t.toLowerCase().includes('declarant')||t.toLowerCase().includes('func')).slice(0,6)")
    print("ERORI declarant:", json.dumps(erori, ensure_ascii=False))
    b.close(); print("DONE")
