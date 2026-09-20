# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 7 (Verificari interne / Control fiscal) prin interfata (Playwright).
Deschide Control fiscal, confirma ca verdictul se randeaza. Vezi asteptari_f1_etapa7.md.
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa7.py
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
        ctx = b.new_context(viewport={"width": 1280, "height": 2200})
        pg = ctx.new_page()
        erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok")
            H.deschide_f1(pg); print("F1 deschisa")
            pg.wait_for_selector("#fa-control", timeout=8000)
            pg.click("#fa-control"); pg.wait_for_timeout(2500)
            H.shot(pg, "e7_01_control")
            body = pg.inner_text("body")
            print("contine 'Control fiscal':", "Control fiscal" in body)
            print("contine 'reconcil' (verificari):", "econcil" in body.lower())
            print("erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e7_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
