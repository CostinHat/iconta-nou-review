# -*- coding: utf-8 -*-
"""SESIUNEA B — Faza 1, F2, etapele 1-2 PRIN INTERFATA (Playwright).
F2: SRL, TVA TRIMESTRIAL, impozit pe PROFIT 16%, cu MIJLOC FIX (amortizare), fara salariati.
Cabinet A exista deja (din F1) -> LOGIN. Adauga F2 -> vector profit/trimestrial -> import solduri + mijloc fix.
Rulare: ./venv/bin/python frontend_test/proba_f2_etape12.py . Vezi asteptari_f2.md.
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
F2_CUI = "403000015"          # RO403000015 (cifra de control verificata)
F2_NUME = "F2 Profit Amortizare SRL"


def _shot(pg, nume):
    try:
        pg.screenshot(path=os.path.join(OUT, "f2_" + nume + ".png"), full_page=True)
    except Exception:
        pass


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1900})
        pg = ctx.new_page()
        erc = []
        pg.on("console", lambda m: erc.append(m.text) if m.type == "error" else None)
        try:
            H.login(pg); print("LOGIN ok (cabinet A din F1)")

            def la_firme_existente():
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(700)
                for _ in range(2):
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
                pg.wait_for_selector(".cab-card", timeout=10000)
                pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
                fe = pg.query_selector("text=Firme existente")
                if fe and fe.is_visible():
                    fe.click(); pg.wait_for_timeout(700)

            # ── ETAPA 2a: adauga F2 (idempotent) ──
            la_firme_existente()
            _shot(pg, "05_firme")
            if not pg.query_selector("text=" + F2_NUME):
                pg.wait_for_selector("#firme-adauga", timeout=10000)
                pg.click("#firme-adauga"); pg.wait_for_timeout(500)
                pg.wait_for_selector("#fn-cui", timeout=8000)
                pg.fill("#fn-cui", F2_CUI); pg.fill("#fn-nume", F2_NUME)
                pg.select_option("#fn-tip", "srl"); pg.wait_for_timeout(300)
                pg.eval_on_selector("#fn-salveaza", "b => b.disabled = false")
                pg.click("#fn-salveaza"); pg.wait_for_timeout(2500)
                print("ADAUGA F2: creata"); la_firme_existente()
            else:
                print("F2 exista deja")

            # ── ETAPA 2b: Date firma -> VECTOR FISCAL (profit, da TVA, TRIMESTRIAL, fara IC) ──
            pg.get_by_text(F2_NUME, exact=False).first.click(timeout=8000)
            pg.wait_for_selector("#fa-datefirma, #fa-import", timeout=12000); pg.wait_for_timeout(600)
            pg.click("#fa-datefirma"); pg.wait_for_timeout(800)
            pg.wait_for_selector("#vf-regim_fiscal", timeout=10000)
            IDENT = {"df-nume-portofoliu": F2_NUME, "df-cui": F2_CUI, "df-reg_com": "J40/2000/2026",
                     "df-caen": "2511", "df-adresa": "Str. Productiei 2", "df-oras": "Bucuresti",
                     "df-judet": "Bucuresti", "df-cod_postal": "020202", "df-banca": "Banca Test",
                     "df-iban": "RO49AAAA1B31007593840001", "df-telefon": "0722000002",
                     "df-email": "f2@sesiuneab.test", "df-patron_nume": "Popescu Petru",
                     "df-declarant_nume": "Popescu", "df-declarant_prenume": "Petru",
                     "df-declarant_functie": "Administrator"}
            for sel, val in IDENT.items():
                el = pg.query_selector("#" + sel)
                if el and not (el.input_value() or "").strip():
                    el.fill(val)
            pg.select_option("#vf-regim_fiscal", "profit")
            pg.select_option("#vf-platitor_tva", "da"); pg.wait_for_timeout(300)
            pg.select_option("#vf-tip_decont", "trimestrial")
            pg.select_option("#vf-operatiuni_ic", "nu")
            ia = pg.query_selector("#vf-inreg_art317")
            if ia: pg.select_option("#vf-inreg_art317", "nu")
            td = pg.query_selector("#vf-tva_data_inceput")
            if td: pg.fill("#vf-tva_data_inceput", "2026-01-01")
            _shot(pg, "08_vector")
            pg.click("#df-salveaza"); pg.wait_for_timeout(2500)
            _shot(pg, "09_vector_salvat")
            print("VECTOR: profit + TVA trimestrial + fara IC — submit")

            # ── ETAPA 1: PRELUARE (solduri + mijloc fix) ──
            def deschide_import():
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(1000)
                for _ in range(2):
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
                pg.wait_for_selector(".cab-card", timeout=10000)
                la_firme_existente()
                pg.get_by_text(F2_NUME, exact=False).first.click(timeout=8000)
                pg.wait_for_selector("#fa-import", timeout=12000); pg.wait_for_timeout(400)
                pg.click("#fa-import"); pg.wait_for_timeout(1200)
                pg.wait_for_selector("#mig-pasi", timeout=10000)

            def import_pas(titlu, csv):
                deschide_import()
                pg.locator(".mig-frand", has_text=titlu).first.click(timeout=8000)
                pg.wait_for_selector("#mig-drop", timeout=10000)
                pg.set_input_files("#mig-file", os.path.join(OUT, csv)); pg.wait_for_timeout(2500)
                _shot(pg, "imp_" + csv.replace(".csv", ""))
                for sel in ("#mig-salveaza-sold", "#mig-salveaza", "button.mig-buton.buton-primar",
                            "button.buton-primar:has-text('Salv')", "button:has-text('Adaugă')",
                            "button:has-text('Importă')", "button:has-text('Confirmă')"):
                    el = pg.query_selector(sel)
                    if el and el.is_visible() and not el.is_disabled():
                        el.click(); pg.wait_for_timeout(2500); break
                print("IMPORT %s din %s" % (titlu, csv))

            import_pas("Solduri ini", "solduri_f2.csv")
            import_pas("Mijloace fixe", "mijloace_f2.csv")
            print("erori consola:", erc[:5])
        except Exception as e:
            _shot(pg, "EROARE"); print("EROARE:", str(e)[:300]); raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
