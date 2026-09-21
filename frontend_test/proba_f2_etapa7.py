# -*- coding: utf-8 -*-
"""SESIUNEA B — F2 ETAPA 7 (Control fiscal) prin interfata. Vezi asteptari_f2_etapa7.md."""
import os, sys
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402
F2_NUME = "F2 Profit Amortizare SRL"
def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True); pg = b.new_context(viewport={"width":1280,"height":2000}).new_page()
        erc=[]; pg.on("console", lambda m: erc.append(m.text) if m.type=="error" else None)
        try:
            H.login(pg); print("LOGIN ok")
            pg.goto(H.BAZA+"/",wait_until="domcontentloaded"); pg.wait_for_timeout(700)
            for _ in range(2): pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
            pg.wait_for_selector(".cab-card",timeout=10000)
            pg.get_by_text("Firme",exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
            fe=pg.query_selector("text=Firme existente")
            if fe and fe.is_visible(): fe.click(); pg.wait_for_timeout(700)
            pg.get_by_text(F2_NUME,exact=False).first.click(timeout=8000)
            pg.wait_for_selector("#fa-control",timeout=12000); pg.wait_for_timeout(500)
            pg.click("#fa-control"); pg.wait_for_timeout(2500)
            H.shot(pg,"f2_e7_control")
            print("contine 'Control fiscal':", "Control fiscal" in pg.inner_text("body"))
            print("erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg,"f2_e7_EROARE"); print("EROARE:", str(e)[:200]); raise
        finally: b.close()
if __name__=="__main__": main()
