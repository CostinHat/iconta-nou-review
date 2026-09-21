# -*- coding: utf-8 -*-
"""SESIUNEA B — F3 etapele 1-2 PRIN INTERFATA (Playwright).
F3: SRL, NEPLATITOR TVA + art.317, micro 1% (2026), cu operatiuni IC, fara salariati.
Cabinet A exista -> LOGIN. Adauga F3 -> vector micro/neplatitor/art317/IC -> import solduri. Vezi asteptari_f3.md.
Rulare: ./venv/bin/python frontend_test/proba_f3_etape12.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright  # noqa: E402
import f1_helper as H  # noqa: E402

BAZA = H.BAZA
OUT = os.path.dirname(os.path.abspath(__file__))
F3_CUI = "404000013"
F3_NUME = "F3 Intracomunitar SRL"


def _shot(pg, nume):
    try:
        pg.screenshot(path=os.path.join(OUT, "f3_" + nume + ".png"), full_page=True)
    except Exception:
        pass


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1900})
        pg = ctx.new_page(); erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok")

            def la_firme_existente():
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(700)
                for _ in range(2):
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
                pg.wait_for_selector(".cab-card", timeout=10000)
                pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
                fe = pg.query_selector("text=Firme existente")
                if fe and fe.is_visible():
                    fe.click(); pg.wait_for_timeout(700)

            la_firme_existente()
            if not pg.query_selector("text=" + F3_NUME):
                pg.wait_for_selector("#firme-adauga", timeout=10000)
                pg.click("#firme-adauga"); pg.wait_for_timeout(500)
                pg.wait_for_selector("#fn-cui", timeout=8000)
                pg.fill("#fn-cui", F3_CUI); pg.fill("#fn-nume", F3_NUME)
                pg.select_option("#fn-tip", "srl"); pg.wait_for_timeout(300)
                pg.eval_on_selector("#fn-salveaza", "b => b.disabled = false")
                pg.click("#fn-salveaza"); pg.wait_for_timeout(2500)
                print("ADAUGA F3: creata"); la_firme_existente()
            else:
                print("F3 exista deja")

            pg.get_by_text(F3_NUME, exact=False).first.click(timeout=8000)
            pg.wait_for_selector("#fa-datefirma, #fa-import", timeout=12000); pg.wait_for_timeout(600)
            pg.click("#fa-datefirma"); pg.wait_for_timeout(800)
            pg.wait_for_selector("#vf-regim_fiscal", timeout=10000)
            IDENT = {"df-nume-portofoliu": F3_NUME, "df-cui": F3_CUI, "df-reg_com": "J40/3000/2026",
                     "df-caen": "4649", "df-adresa": "Str. Importului 3", "df-oras": "Bucuresti",
                     "df-judet": "Bucuresti", "df-cod_postal": "030303", "df-banca": "Banca Test",
                     "df-iban": "RO49AAAA1B31007593840003", "df-telefon": "0722000003",
                     "df-email": "f3@sesiuneab.test", "df-patron_nume": "Georgescu Gheorghe",
                     "df-declarant_nume": "Georgescu", "df-declarant_prenume": "Gheorghe",
                     "df-declarant_functie": "Administrator"}
            for sel, val in IDENT.items():
                el = pg.query_selector("#" + sel)
                if el and not (el.input_value() or "").strip():
                    el.fill(val)
            # VECTOR: micro, NEPLATITOR TVA, cu operatiuni IC, inreg art.317
            pg.select_option("#vf-regim_fiscal", "micro")
            pg.select_option("#vf-platitor_tva", "nu"); pg.wait_for_timeout(300)
            pg.select_option("#vf-operatiuni_ic", "da")
            ia = pg.query_selector("#vf-inreg_art317")
            if ia: pg.select_option("#vf-inreg_art317", "da")
            _shot(pg, "08_vector")
            pg.click("#df-salveaza"); pg.wait_for_timeout(2500)
            _shot(pg, "09_vector_salvat")
            ecr = pg.query_selector(".camp-eroare, .eroare-camp")
            if ecr and ecr.is_visible(): print("VECTOR eroare camp:", (ecr.inner_text() or "")[:120])
            print("VECTOR: micro + neplatitor + IC + art.317 — submit")

            def deschide_import():
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(1000)
                for _ in range(2):
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
                pg.wait_for_selector(".cab-card", timeout=10000)
                la_firme_existente()
                pg.get_by_text(F3_NUME, exact=False).first.click(timeout=8000)
                pg.wait_for_selector("#fa-import", timeout=12000); pg.wait_for_timeout(400)
                pg.click("#fa-import"); pg.wait_for_timeout(1200)
                pg.wait_for_selector("#mig-pasi", timeout=10000)

            deschide_import()
            pg.locator(".mig-frand", has_text="Solduri ini").first.click(timeout=8000)
            pg.wait_for_selector("#mig-drop", timeout=10000)
            pg.set_input_files("#mig-file", os.path.join(OUT, "solduri_f3.csv")); pg.wait_for_timeout(2500)
            for sel in ("#mig-salveaza-sold", "#mig-salveaza", "button.mig-buton.buton-primar",
                        "button.buton-primar:has-text('Salv')"):
                el = pg.query_selector(sel)
                if el and el.is_visible() and not el.is_disabled():
                    el.click(); pg.wait_for_timeout(2500); break
            print("IMPORT solduri_f3. erori consola:", erc[:5])
        except Exception as e:
            _shot(pg, "EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
