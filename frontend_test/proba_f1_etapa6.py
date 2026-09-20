# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 6 (Sfarsit de luna) prin interfata (Playwright).
Inchide luna facturi (septembrie 2026) din Istoric facturi. Vezi asteptari_f1_etapa6.md.
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa6.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 2000})
        pg = ctx.new_page()
        erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok")
            H.deschide_f1(pg); print("F1 deschisa")
            pg.wait_for_selector("#fa-facturi", timeout=8000)
            pg.click("#fa-facturi"); pg.wait_for_timeout(1000)
            pg.wait_for_selector("#fac-istoric", timeout=8000)
            pg.click("#fac-istoric"); pg.wait_for_timeout(1500)
            H.shot(pg, "e6_01_istoric")
            inch = pg.query_selector("#fac-inchide")
            print("buton Inchide luna prezent:", bool(inch and inch.is_visible()))
            if inch and inch.is_visible():
                inch.click(); pg.wait_for_timeout(700)
                # confirmaCaseta -> buton confirmare cu id stabil #ca-ok (NU butonul principal)
                pg.click("#ca-ok", timeout=6000)
                pg.wait_for_timeout(2000)
            H.shot(pg, "e6_02_dupa_inchidere")
            print("erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e6_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
