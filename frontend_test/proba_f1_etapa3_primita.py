# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 3, D2: validarea facturii PRIMITE din SPV prin interfata (Playwright).
Presupune ca efactura_primite (SIM-SPV-F1-D2-001) e deja inserata (scratchpad/insert_spv_d2.py).
Valideaza prin UI: Facturi -> Facturi primite -> factura -> cont 371 -> Valideaza.
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa3_primita.py
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
        ctx = b.new_context(viewport={"width": 1280, "height": 1800})
        pg = ctx.new_page()
        erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok")
            H.deschide_f1(pg); print("F1 deschisa")
            # Facturi (card firma)
            pg.wait_for_selector("#fa-facturi", timeout=8000)
            pg.click("#fa-facturi"); pg.wait_for_timeout(1000)
            pg.wait_for_selector("#fac-primite", timeout=8000)
            pg.click("#fac-primite"); pg.wait_for_timeout(1200)
            H.shot(pg, "e3_pr_01_lista")
            # click prima factura primita din lista
            pg.wait_for_selector(".fac-primita-btn", timeout=8000)
            pg.click(".fac-primita-btn"); pg.wait_for_timeout(1000)
            H.shot(pg, "e3_pr_02_detaliu")
            # cont cheltuiala = 371 (marfa)
            pg.fill("#pr-cont", "371")
            pg.wait_for_timeout(300)
            pg.click("#pr-valideaza"); pg.wait_for_timeout(700)
            # confirmaCaseta -> buton cu text EXACT "Validează" (nu butonul principal "Validează (creează cheltuiala)")
            pg.click("button:text-is('Validează')", timeout=6000)
            pg.wait_for_timeout(2500)
            H.shot(pg, "e3_pr_03_dupa")
            print("VALIDARE primita: trimis. erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e3_pr_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
