# -*- coding: utf-8 -*-
"""Date firma + Vector fiscal: captura + text + campuri obligatorii. Provoc blocaj pe vector (camp gol)."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    # --- DATE FIRMA ---
    try:
        deschide_firma(pg)
        pg.click("#fa-datefirma"); pg.wait_for_timeout(1500)
        shot(pg, "date_firma")
        rez["date_firma"] = {
            "titlu": txt(pg, ".pf-titlu") or txt(pg, "h2"),
            "campuri": pg.eval_on_selector_all("input,select", "els=>els.slice(0,40).map(e=>({id:e.id, name:e.name, val:(e.value||'').slice(0,20), ph:e.placeholder||'', tip:e.tagName}))"),
            "oblig": len(pg.query_selector_all(".oblig")),
            "camp_ajutor": [e.inner_text().strip() for e in pg.query_selector_all(".camp-ajutor")][:6],
            "text": (txt(pg, "main") or "")[:400],
        }
    except Exception as e:
        rez["date_firma"] = {"error": str(e)}; shot(pg, "date_firma_ERR")
    # --- VECTOR FISCAL (din Import date) ---
    try:
        deschide_firma(pg)
        pg.click("#fa-import"); pg.wait_for_timeout(700)
        pg.get_by_text("Vector fiscal", exact=False).first.click(timeout=8000); pg.wait_for_timeout(1200)
        shot(pg, "vector")
        rez["vector"] = {
            "titlu": txt(pg, ".pf-titlu") or txt(pg, "h2"),
            "campuri": pg.eval_on_selector_all("input,select", "els=>els.slice(0,40).map(e=>({id:e.id, name:e.name, tip:e.tagName, val:(e.value||'').slice(0,20)}))"),
            "oblig": len(pg.query_selector_all(".oblig")),
            "camp_ajutor": [e.inner_text().strip() for e in pg.query_selector_all(".camp-ajutor")][:8],
            "are_platitor_tva_inceput": bool(pg.query_selector("text=platitor_tva_anaf_inceput") or pg.query_selector("text=începerii TVA") or pg.query_selector("text=inceperii TVA") or pg.query_selector("text=data TVA")),
        }
    except Exception as e:
        rez["vector"] = {"error": str(e)}; shot(pg, "vector_ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:4000])
    b.close()
