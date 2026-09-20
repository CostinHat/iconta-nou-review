# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 4 (salarizare) prin interfata (Playwright).
Deschide statul de plata (luna curenta), verifica baza din istoric (NU 0), contabilizeaza statul.
Vezi asteptari_f1_etapa4.md. Rulare: ./venv/bin/python frontend_test/proba_f1_etapa4.py
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
            pg.wait_for_selector("#fa-salariati", timeout=8000)
            pg.click("#fa-salariati"); pg.wait_for_timeout(1500)
            pg.wait_for_selector("#sp-contare", timeout=8000)
            pg.wait_for_timeout(1000)
            H.shot(pg, "e4_01_stat")
            # verifica textul afisat: bruturi (nu 0) + "Salariul de baza lipseste" NU trebuie sa apara
            body = pg.inner_text("body")
            print("baza_lipsa in ecran?", "Salariul de bază lipsește" in body)
            for m in ("4.000", "4.500", "2.426", "2.710"):
                print("  contine", m, ":", m in body)
            # contabilizeaza statul
            pg.click("#sp-contare"); pg.wait_for_timeout(1500)
            scrie = pg.query_selector("#sp-contare-scrie")
            if scrie and scrie.is_visible():
                scrie.click(); pg.wait_for_timeout(2000)
                print("CONTARE stat: nota scrisa")
            else:
                print("CONTARE stat: buton scrie indisponibil (poate deja contat)")
            H.shot(pg, "e4_02_dupa_contare")
            print("erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e4_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
