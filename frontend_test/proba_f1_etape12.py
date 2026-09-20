# -*- coding: utf-8 -*-
"""SESIUNEA B — Faza 1, F1, etapele 1-2 PRIN INTERFATA (Playwright, contabil prima data).

NU importa w_auth: acela mintuieste la import o sesiune pentru un user care nu mai exista (portofoliu
sters in Faza 0) si ar crapa. Aici totul trece prin UI real: inregistrare cabinet -> auto-login ->
adauga firma F1 -> (urmeaza) configurare vector fiscal + preluare sold/plan/parteneri/stoc/salariati.

Rulare: ./venv/bin/python frontend_test/proba_f1_etape12.py
Verificarile de rezultat (Sdebit=Scredit, vector fiscal, 3 salariati) sunt in asteptari_f1.md.
"""
import os
import sys
import time

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
from playwright.sync_api import sync_playwright  # noqa: E402

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010")
OUT = os.path.dirname(os.path.abspath(__file__))

# Contabil "prima data" — cont NOU (nu exista in baza dupa Faza 0)
EMAIL = "contabil.b@sesiuneab.test"
PAROLA = "TestF1parola!2026"
CABINET = "Cabinet Test Sesiunea B SRL"
# F1 (asteptari_f1.md): SRL, CUI cu cifra de control valida
F1_CUI = "401002001"          # RO401002001
F1_NUME = "F1 Comert Stoc SRL"


def _shot(pg, nume):
    try:
        pg.screenshot(path=os.path.join(OUT, "f1_" + nume + ".png"), full_page=True)
    except Exception:
        pass


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1800})
        pg = ctx.new_page()
        erori_consola = []
        pg.on("console", lambda m: erori_consola.append(m.text) if m.type == "error" else None)
        try:
            # ── ETAPA: inregistrare cabinet (contabil prima data) ──
            pg.goto(BAZA + "/", wait_until="domcontentloaded")
            pg.wait_for_timeout(800)
            _shot(pg, "01_landing")
            # Acces (bara landing) -> ecran alegere
            pg.wait_for_selector("#pagina-acces-btn", timeout=8000)
            pg.click("#pagina-acces-btn"); pg.wait_for_timeout(600)
            pg.wait_for_selector("#acces-intra, #acces-client-nou", timeout=8000)
            # exista deja cont? incearca INREGISTRARE prima data; daca esueaza (email exista), LOGIN.
            cont_nou = False
            pg.click("#acces-client-nou"); pg.wait_for_timeout(500)   # -> preturi
            pg.wait_for_selector("#pr-continua", timeout=8000)
            pg.click("#pr-continua"); pg.wait_for_timeout(500)        # -> formular inregistrare
            pg.wait_for_selector("#reg-email", timeout=8000)
            _shot(pg, "02_register_form")
            pg.fill("#reg-cabinet", CABINET)
            na = pg.query_selector("#reg-nume-admin")
            if na: na.fill("Contabil Sesiunea B")
            pg.fill("#reg-email", EMAIL)
            pg.fill("#reg-parola", PAROLA)
            pg.fill("#reg-parola2", PAROLA)
            pg.check("#reg-termeni")
            _shot(pg, "03_register_completat")
            pg.click("#reg-buton"); pg.wait_for_timeout(2500)
            er = pg.query_selector("#reg-eroare")
            deja = bool(er and er.is_visible() and "deja" in (er.inner_text() or "").lower())
            if not deja and pg.query_selector(".cab-card"):
                cont_nou = True
                print("REGISTER: cont NOU creat + auto-login (contabil prima data)")
            else:
                # cont deja creat (rulare anterioara) -> LOGIN, calea de autentificare
                print("REGISTER: email deja inregistrat -> LOGIN pe contul existent")
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(800)
                pg.wait_for_selector("#pagina-acces-btn", timeout=8000)
                pg.click("#pagina-acces-btn"); pg.wait_for_timeout(600)
                pg.wait_for_selector("#acces-intra", timeout=8000)
                pg.click("#acces-intra"); pg.wait_for_timeout(600)
                # al doilea nivel: "Sunt cabinet de contabilitate" (email+parola)
                pg.get_by_text("Sunt cabinet de contabilitate", exact=False).first.click(timeout=8000)
                pg.wait_for_timeout(500)
                pg.wait_for_selector("#login-email", timeout=8000)
                pg.fill("#login-email", EMAIL); pg.fill("#login-parola", PAROLA)
                pg.click("#login-buton")
            pg.wait_for_selector(".cab-card", timeout=15000)
            pg.wait_for_timeout(800)
            _shot(pg, "04_autentificat")
            print("AUTENTIFICAT (cont_nou=%s)" % cont_nou)

            # inchide modalul de "bun venit" (prima logare) daca acopera ecranul
            for _ in range(3):
                pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
            for sel in ("button:has-text('Am înțeles')", "button:has-text('Închide')", ".fereastra-x", "#anunt-x", ".modal-x"):
                el = pg.query_selector(sel)
                if el and el.is_visible():
                    el.click(); pg.wait_for_timeout(300); break
            pg.wait_for_timeout(400)
            _shot(pg, "04b_dupa_bunvenit")

            def la_firme_existente():
                pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
                fe = pg.query_selector("text=Firme existente")
                if fe and fe.is_visible():
                    fe.click(); pg.wait_for_timeout(700)

            # ── ETAPA 2a: adauga firma F1 (idempotent — daca exista, nu re-creeaza) ──
            la_firme_existente()
            _shot(pg, "05a_ecran_firme")
            if not pg.query_selector("text=" + F1_NUME):
                if not pg.query_selector("#firme-adauga"):
                    la_firme_existente()
                pg.wait_for_selector("#firme-adauga", timeout=10000)
                pg.click("#firme-adauga"); pg.wait_for_timeout(500)
                pg.wait_for_selector("#fn-cui", timeout=8000)
                pg.fill("#fn-cui", F1_CUI); pg.fill("#fn-nume", F1_NUME)
                pg.select_option("#fn-tip", "srl"); pg.wait_for_timeout(300)
                pg.eval_on_selector("#fn-salveaza", "b => b.disabled = false")
                pg.click("#fn-salveaza"); pg.wait_for_timeout(2500)
                print("ADAUGA F1: creata")
                la_firme_existente()
            else:
                print("F1 exista deja in lista")

            # ── ETAPA 2b: deschide F1 -> Date firma -> VECTOR FISCAL (micro, da TVA, lunar) ──
            pg.get_by_text(F1_NUME, exact=False).first.click(timeout=8000)
            pg.wait_for_selector("#fa-datefirma, #fa-import", timeout=12000); pg.wait_for_timeout(600)
            _shot(pg, "07_firma_F1")
            pg.click("#fa-datefirma"); pg.wait_for_timeout(800)
            pg.wait_for_selector("#vf-regim_fiscal", timeout=10000)
            # identitate ANAF (obligatorii) — completez doar campurile goale
            IDENT = {"df-nume-portofoliu": F1_NUME, "df-cui": F1_CUI, "df-reg_com": "J40/1000/2026",
                     "df-caen": "4711", "df-adresa": "Str. Comertului 1", "df-oras": "Bucuresti",
                     "df-judet": "Bucuresti", "df-cod_postal": "010101", "df-banca": "Banca Test",
                     "df-iban": "RO49AAAA1B31007593840000", "df-telefon": "0722000000",
                     "df-email": "f1@sesiuneab.test", "df-patron_nume": "Ionescu Ion",
                     "df-declarant_nume": "Ionescu", "df-declarant_prenume": "Ion",
                     "df-declarant_functie": "Administrator"}
            for sel, val in IDENT.items():
                el = pg.query_selector("#" + sel)
                if el and not (el.input_value() or "").strip():
                    el.fill(val)
            # VECTOR FISCAL: micro, platitor TVA, lunar, FARA operatiuni IC
            pg.select_option("#vf-regim_fiscal", "micro")
            pg.select_option("#vf-platitor_tva", "da"); pg.wait_for_timeout(300)
            pg.select_option("#vf-tip_decont", "lunar")
            pg.select_option("#vf-operatiuni_ic", "nu")
            ia = pg.query_selector("#vf-inreg_art317")
            if ia: pg.select_option("#vf-inreg_art317", "nu")
            td = pg.query_selector("#vf-tva_data_inceput")
            if td: pg.fill("#vf-tva_data_inceput", "2026-01-01")
            _shot(pg, "08_vector_completat")
            pg.click("#df-salveaza"); pg.wait_for_timeout(2500)
            _shot(pg, "09_vector_salvat")
            # eroare de camp ramasa?
            ecr = pg.query_selector(".camp-eroare, .eroare-camp")
            if ecr and ecr.is_visible(): print("SALVARE vector — eroare camp:", (ecr.inner_text() or "")[:120])
            print("VECTOR FISCAL: micro + platitor TVA + lunar + fara IC — submit")

            # ── ETAPA 1: PRELUARE (Import date -> upload CSV per pas) ──
            def deschide_import():
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(1000)
                for _ in range(2):
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
                pg.wait_for_selector(".cab-card", timeout=10000)
                la_firme_existente()
                pg.get_by_text(F1_NUME, exact=False).first.click(timeout=8000)
                pg.wait_for_selector("#fa-import", timeout=12000); pg.wait_for_timeout(400)
                pg.click("#fa-import"); pg.wait_for_timeout(1200)
                _shot(pg, "imp_meniu")
                print("dupa #fa-import: #mig-pasi?", bool(pg.query_selector("#mig-pasi")),
                      "| stare-goala?", bool(pg.query_selector(".stare-goala")))
                pg.wait_for_selector("#mig-pasi", timeout=10000)

            def import_pas(titlu, csv):
                deschide_import()
                pg.locator(".mig-frand", has_text=titlu).first.click(timeout=8000)
                pg.wait_for_selector("#mig-drop", timeout=10000)   # drop-zone vizibil; #mig-file e hidden
                pg.set_input_files("#mig-file", os.path.join(OUT, csv))
                pg.wait_for_timeout(2500)   # upload + preview
                _shot(pg, "imp_" + csv.replace(".csv", ""))
                # click butonul primar de salvare din preview
                for sel in ("#mig-salveaza-sold", "#mig-salveaza-part", "#mig-salveaza-art",
                            "#mig-salveaza-sal", "button.mig-buton.buton-primar",
                            "button.buton-primar:has-text('Salv')", "button:has-text('Adaugă')",
                            "button:has-text('Importă')", "button:has-text('Confirmă')"):
                    el = pg.query_selector(sel)
                    if el and el.is_visible() and not el.is_disabled():
                        el.click(); pg.wait_for_timeout(2500); break
                print("IMPORT %s: din %s" % (titlu, csv))

            import_pas("Solduri ini", "solduri_f1.csv")
            import_pas("Solduri parteneri", "parteneri_f1.csv")
            import_pas("Articole", "articole_f1.csv")
            import_pas("Salaria", "salariati_f1.csv")

            print("erori consola:", erori_consola[:5])
        except Exception as e:
            _shot(pg, "EROARE")
            print("EROARE:", str(e)[:300])
            raise
        finally:
            b.close()


if __name__ == "__main__":
    main()
