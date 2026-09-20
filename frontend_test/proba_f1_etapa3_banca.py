# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 3, D3: extras bancar (o incasare + o plata) prin interfata (Playwright).
Import extras_f1.csv -> reconciliere pe facturi -> contare. Vezi asteptari_f1_etapa3.md.
Incasare client 410001005 1210 (5121=4111) + plata furnizor 420002008 1210 (401=5121).
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa3_banca.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402

EXTRAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extras_f1.csv")


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
            pg.wait_for_selector("#fa-banca", timeout=8000)
            pg.click("#fa-banca"); pg.wait_for_timeout(1000)
            pg.wait_for_selector("#bk-fisier", timeout=8000)
            pg.set_input_files("#bk-fisier", EXTRAS); pg.wait_for_timeout(2500)
            H.shot(pg, "e3_bk_01_import")
            # liniile importate -> butoane [data-cont]
            btns = pg.query_selector_all("[data-cont]")
            print("linii de contat:", len(btns))
            # contate una cate una (lista se re-randeaza dupa fiecare -> re-interoghez)
            for i in range(10):
                b2 = pg.query_selector("[data-cont]")
                if not b2:
                    break
                b2.click(); pg.wait_for_timeout(1500)
            H.shot(pg, "e3_bk_02_dupa_contare")
            print("CONTARE extras: gata. erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e3_bk_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
