# -*- coding: utf-8 -*-
"""SESIUNEA B — F2 ETAPA 3 (documente primare) prin interfata (Playwright).
Factura EMISA serviciu (fara stoc/descarcare) + 2 operatiuni de registru de casa. Vezi asteptari_f2_etapa3.md.
Rulare: ./venv/bin/python frontend_test/proba_f2_etapa3.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402

F2_NUME = "F2 Profit Amortizare SRL"
CLIENT_CUI = "410001005"


def deschide_f2(pg):
    pg.goto(H.BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(800)
    for _ in range(2):
        pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    pg.wait_for_selector(".cab-card", timeout=10000)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
    fe = pg.query_selector("text=Firme existente")
    if fe and fe.is_visible():
        fe.click(); pg.wait_for_timeout(700)
    pg.get_by_text(F2_NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-facturi, #fa-casa", timeout=12000); pg.wait_for_timeout(500)


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1900})
        pg = ctx.new_page()
        erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok")
            deschide_f2(pg); print("F2 deschisa")
            # ── D1: factura serviciu emisa ──
            pg.get_by_text("Facturi", exact=True).first.click(timeout=8000); pg.wait_for_timeout(800)
            for t in ("Emite factură", "Emite factura", "Emite"):
                el = pg.query_selector("text=" + t)
                if el and el.is_visible(): el.click(); pg.wait_for_timeout(800); break
            if pg.query_selector("#em-nu"):
                pg.click("#em-nu"); pg.wait_for_timeout(400)
                pg.wait_for_selector("#em-salveaza-config2", timeout=6000)
                pg.click("#em-salveaza-config2"); pg.wait_for_timeout(1000)
            pg.wait_for_selector("#em-cui, #em-l0-descriere", timeout=10000); pg.wait_for_timeout(400)
            if pg.query_selector("#em-cui"): pg.fill("#em-cui", CLIENT_CUI)
            if pg.query_selector("#em-nume"): pg.fill("#em-nume", "Client Servicii SRL")
            # linia: FARA articol (serviciu)
            if pg.query_selector("#em-l0-articol"):
                pg.select_option("#em-l0-articol", ""); pg.wait_for_timeout(300)
            pg.fill("#em-l0-descriere", "Servicii de productie")
            pg.fill("#em-l0-cantitate", "1")
            pg.fill("#em-l0-pret_unitar", "5000")
            cota = ""
            for _ in range(30):
                pg.wait_for_timeout(500)
                el = pg.query_selector("#em-l0-cota")
                cota = el.inner_text().strip() if el else ""
                if cota and cota not in ("…", "—", "..."): break
            print("cota serviciu:", cota)
            H.shot(pg, "f2_e3_01_factura")
            pg.click("#em-emite"); pg.wait_for_timeout(1500)
            # serviciu -> NU trebuie poarta F172; daca apare totusi, "Nu, doar factura"
            nu = pg.query_selector("#em-poarta-nu")
            if nu and nu.is_visible():
                print("ATENTIE: poarta F172 a aparut pe serviciu (neasteptat)"); nu.click(); pg.wait_for_timeout(1500)
            H.shot(pg, "f2_e3_02_dupa_emite")
            print("EMITE serviciu: trimis")
            # ── D2: registru de casa (2 operatiuni) ──
            deschide_f2(pg)
            pg.click("#fa-casa"); pg.wait_for_timeout(1200)
            def casa_op(cat, suma, doc):
                pg.wait_for_selector("#c-toggle", timeout=8000)
                pg.click("#c-toggle"); pg.wait_for_timeout(400)
                pg.wait_for_selector("#c-data", timeout=6000)
                pg.fill("#c-data", "2026-09-20")
                pg.select_option("#c-cat", cat)
                pg.fill("#c-suma", str(suma))
                if pg.query_selector("#c-doc"): pg.fill("#c-doc", doc)
                pg.click("#c-adauga"); pg.wait_for_timeout(1500)
            casa_op("ridicare_banca", 1000, "DISP-1")
            casa_op("plata_furnizor", 500, "DISP-2")
            H.shot(pg, "f2_e3_03_casa")
            print("CASA: 2 operatiuni. erori consola:", erc[:4])
        except Exception as e:
            H.shot(pg, "f2_e3_EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
