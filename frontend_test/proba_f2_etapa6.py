# -*- coding: utf-8 -*-
"""SESIUNEA B — F2 ETAPA 6 (amortizare) prin interfata. Genereaza nota de amortizare lunara + valideaza.
Rulare: ./venv/bin/python frontend_test/proba_f2_etapa6.py . Vezi asteptari_f2_etapa6.md.
"""
import os, sys
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402
F2_NUME = "F2 Profit Amortizare SRL"

def deschide_f2(pg):
    pg.goto(H.BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(800)
    for _ in range(2):
        pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    pg.wait_for_selector(".cab-card", timeout=10000)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
    fe = pg.query_selector("text=Firme existente")
    if fe and fe.is_visible(): fe.click(); pg.wait_for_timeout(700)
    pg.get_by_text(F2_NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-jurnal", timeout=12000); pg.wait_for_timeout(500)

def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True); ctx = b.new_context(viewport={"width": 1280, "height": 2000})
        pg = ctx.new_page(); erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok"); deschide_f2(pg); print("F2 deschisa")
            pg.click("#fa-jurnal"); pg.wait_for_timeout(1500)
            pg.wait_for_selector("#j-amort", timeout=8000)
            pg.click("#j-amort"); pg.wait_for_timeout(2500)
            H.shot(pg, "f2_e6_amort")
            # valideaza nota de amortizare (ciorna noua)
            for _ in range(10):
                b2 = pg.query_selector("[data-val]")
                if not b2: break
                b2.click(); pg.wait_for_timeout(1200)
            print("AMORTIZARE generata + validata. erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "f2_e6_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()

if __name__ == "__main__":
    main()
