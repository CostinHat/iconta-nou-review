# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 3, D2: achizitie marfa prin NIR (Stocuri) prin interfata (Playwright).
Cumpara 20 buc Marfa A x 50 = 1.000 baza + 21% 210 = 1.210. Vezi asteptari_f1_etapa3.md.
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa3_nir.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402

FURN_CUI = "420002008"   # furnizor F1 (cifra de control verificata)
FURN_NUME = "Furnizor Test SRL"


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1800})
        pg = ctx.new_page()
        erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)

        def _resp(r):
            if "/stocuri/nir" in r.url and r.request.method == "POST":
                try:
                    print("NIR REQ:", r.request.post_data)
                    print("NIR RESP %d:" % r.status, r.text()[:400])
                except Exception as ex:
                    print("resp log err:", ex)
        pg.on("response", _resp)
        try:
            H.login(pg); print("LOGIN ok")
            H.deschide_f1(pg); print("F1 deschisa")
            pg.wait_for_selector("#fa-stocuri", timeout=8000)
            pg.click("#fa-stocuri"); pg.wait_for_timeout(1000)
            pg.wait_for_selector("#sn-toggle", timeout=8000)
            H.shot(pg, "e3_nir_01_stocuri")
            pg.click("#sn-toggle"); pg.wait_for_timeout(500)
            pg.wait_for_selector("#sn-numar", timeout=6000)
            pg.fill("#sn-numar", "1")
            pg.fill("#sn-data", "2026-09-20")
            pg.fill("#sn-furn", FURN_NUME)
            pg.fill("#sn-cui", FURN_CUI)
            # linia 0: Marfa A, 20 buc, pret achizitie 50, pret raft 121 (cu TVA), cota 21
            pg.fill("#nir-l0-denumire", "Marfa A")
            pg.fill("#nir-l0-cantitate", "20")
            pg.fill("#nir-l0-pret_achizitie", "50")
            pg.fill("#nir-l0-pret_vanzare", "121")
            pg.select_option("#nir-l0-cota_tva", "21")
            pg.dispatch_event("#nir-l0-cota_tva", "change")   # asigura listenerul l.cota_tva=21
            pg.wait_for_timeout(400)
            print("cota select value:", pg.eval_on_selector("#nir-l0-cota_tva", "el => el.value"))
            H.shot(pg, "e3_nir_02_completat")
            pg.click("#sn-salveaza"); pg.wait_for_timeout(2500)
            H.shot(pg, "e3_nir_03_dupa_salvare")
            print("NIR salvat. erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e3_nir_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
