# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 5 (Contabilizare / validare jurnal) prin interfata (Playwright).
Valideaza toate notele ciorna -> validata. Vezi asteptari_f1_etapa5.md.
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa5.py
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
            pg.wait_for_selector("#fa-jurnal", timeout=8000)
            pg.click("#fa-jurnal"); pg.wait_for_timeout(1500)
            H.shot(pg, "e5_01_jurnal")
            n0 = len(pg.query_selector_all("[data-val]"))
            print("note ciorna de validat (buton Validează):", n0)
            # valideaza una cate una (lista se re-randeaza dupa fiecare)
            for i in range(20):
                b2 = pg.query_selector("[data-val]")
                if not b2:
                    break
                b2.click(); pg.wait_for_timeout(1200)
            ramase = len(pg.query_selector_all("[data-val]"))
            print("note ciorna ramase dupa validare:", ramase)
            H.shot(pg, "e5_02_dupa_validare")
            print("erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e5_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
