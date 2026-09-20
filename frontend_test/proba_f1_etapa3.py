# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 3 (intrare documente primare) prin interfata (Playwright).
Partea 1: factura EMISA cu descarcare de gestiune (vanzare 10 buc Marfa A). Vezi asteptari_f1_etapa3.md.
Rulare: ./venv/bin/python frontend_test/proba_f1_etapa3.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402

CLIENT_CUI = "410001005"      # RO410001005 (client din parteneri)
CLIENT_NUME = "Client Test SRL"


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
            # Facturi -> Emite
            pg.get_by_text("Facturi", exact=True).first.click(timeout=8000); pg.wait_for_timeout(800)
            H.shot(pg, "e3_01_facturi")
            for t in ("Emite factură", "Emite factura", "Emite", "Factură nouă"):
                el = pg.query_selector("text=" + t)
                if el and el.is_visible(): el.click(); pg.wait_for_timeout(800); break
            # config numerotare prima data (TVA din profil -> doar "am mai emis?")
            if pg.query_selector("#em-nu"):
                pg.click("#em-nu"); pg.wait_for_timeout(400)
                pg.wait_for_selector("#em-salveaza-config2", timeout=6000)
                pg.click("#em-salveaza-config2"); pg.wait_for_timeout(1000)
                print("CONFIG emitere: serie goala, incep acum")
            pg.wait_for_selector("#em-cui, #em-l0-descriere", timeout=10000); pg.wait_for_timeout(500)
            H.shot(pg, "e3_02_form")
            # client
            if pg.query_selector("#em-cui"):
                pg.fill("#em-cui", CLIENT_CUI)
            if pg.query_selector("#em-nume"):
                pg.fill("#em-nume", CLIENT_NUME)
            # linia 0: articol Marfa A + cant 10 + pret 100
            if pg.query_selector("#em-l0-articol"):
                # alege articolul dupa text (Marfa A)
                pg.select_option("#em-l0-articol", label=None, index=1)  # prima optiune reala (dupa "fara articol")
                pg.wait_for_timeout(800)
            pg.fill("#em-l0-cantitate", "10")
            pg.fill("#em-l0-pret_unitar", "100")
            # cota vine prin AI (/produse/potriveste, round-trip ~3-5s) -> POLL pana se rezolva, NU wait fix
            cota = ""
            for _ in range(30):   # pana la ~15s
                pg.wait_for_timeout(500)
                el = pg.query_selector("#em-l0-cota")
                cota = el.inner_text().strip() if el else ""
                if cota and cota not in ("…", "—", "..."):
                    break
            H.shot(pg, "e3_03_linie")
            print("cota linie auto:", cota)
            if not cota or cota in ("…", "—", "..."):
                raise RuntimeError("cota nu s-a rezolvat (AI): '%s'" % cota)
            btn = pg.query_selector("#em-emite")
            print("emite disabled:", btn.get_attribute("disabled") if btn else "N/A")
            pg.click("#em-emite"); pg.wait_for_timeout(2000)
            H.shot(pg, "e3_04_dupa_emite")
            # poarta descarcare gestiune F172: "pleaca marfa acum?" -> DA (vanzare cu descarcare CMP)
            pg.wait_for_selector("#em-poarta-da", timeout=8000)
            pg.click("#em-poarta-da"); pg.wait_for_timeout(2500)
            H.shot(pg, "e3_05_final")
            print("EMITE factura (cu descarcare gestiune): trimis. erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "e3_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
