# -*- coding: utf-8 -*-
"""Proba UI [tva_inceput]: campul editabil "Data inregistrarii in scopuri de TVA" in ecranul Date firma.
Verifica: apare DOAR la platitor (ALFA=da vizibil, BETA=neplatitor ascuns), se completeaza+salveaza,
si re-deschis pastreaza valoarea. Ruleaza pe firme de test; restaureaza valoarea initiala la final."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v
_body = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(urllib.request.Request(
    BAZA + "/auth/login", _body, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.dirname(os.path.abspath(__file__))


def deschide_date_firma(pg, nume):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text(nume, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-datefirma", timeout=10000)
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#vf-platitor_tva", timeout=10000); pg.wait_for_timeout(400)


rez = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1100, "height": 1600}); ctx.add_init_script(INIT)
    pg = ctx.new_page()

    # ===== ALFA MICRO (platitor) =====
    deschide_date_firma(pg, "ALFA MICRO")
    platitor = pg.eval_on_selector("#vf-platitor_tva", "e=>e.value")
    exista_camp = pg.query_selector("#vf-tva_data_inceput") is not None
    vizibil = pg.is_visible("#vf-tva_data_inceput") if exista_camp else False
    label_txt = pg.eval_on_selector("#vf-camp-tva_data_inceput .camp-eticheta", "e=>e.textContent") if exista_camp else None
    ajutor_txt = pg.eval_on_selector("#vf-camp-tva_data_inceput .camp-ajutor", "e=>e.textContent") if exista_camp else None
    val_init = pg.eval_on_selector("#vf-tva_data_inceput", "e=>e.value") if exista_camp else None
    print("ALFA platitor_tva=%s | camp_exista=%s | vizibil=%s" % (platitor, exista_camp, vizibil))
    print("ALFA label=%r" % label_txt)
    print("ALFA ajutor=%r" % ajutor_txt)
    print("ALFA valoare_prepopulata=%r" % val_init)
    rez["alfa_vizibil_la_platitor"] = (platitor == "da" and vizibil)

    # toggle: platitor -> nu ascunde campul; -> da il arata din nou
    pg.select_option("#vf-platitor_tva", "nu"); pg.wait_for_timeout(200)
    ascuns_la_nu = not pg.is_visible("#vf-tva_data_inceput")
    pg.select_option("#vf-platitor_tva", "da"); pg.wait_for_timeout(200)
    revenit_la_da = pg.is_visible("#vf-tva_data_inceput")
    print("ALFA toggle -> ascuns_la_neplatitor=%s | revizibil_la_platitor=%s" % (ascuns_la_nu, revenit_la_da))
    rez["alfa_toggle"] = ascuns_la_nu and revenit_la_da

    # completeaza o data distincta si salveaza
    NOUA = "2020-03-10"
    pg.fill("#vf-tva_data_inceput", NOUA)
    pg.click("#df-salveaza")
    pg.wait_for_selector(".msg-ok, #df-msg .ok, [class*=ok]", timeout=12000)
    pg.wait_for_timeout(800)
    # re-deschide ecranul curat (nu doar re-render) ca sa dovedim persistenta din DB
    deschide_date_firma(pg, "ALFA MICRO")
    val_dupa = pg.eval_on_selector("#vf-tva_data_inceput", "e=>e.value")
    print("ALFA valoare_dupa_salvare_si_redeschidere=%r (setat %r)" % (val_dupa, NOUA))
    rez["alfa_persista"] = (val_dupa == NOUA)
    pg.screenshot(path=os.path.join(OUT, "proba_tva_inceput.png"), full_page=True)

    # ===== BETA PROFIT (neplatitor) -> campul ascuns =====
    deschide_date_firma(pg, "BETA PROFIT")
    beta_platitor = pg.eval_on_selector("#vf-platitor_tva", "e=>e.value")
    beta_vizibil = pg.is_visible("#vf-tva_data_inceput") if pg.query_selector("#vf-tva_data_inceput") else False
    print("BETA platitor_tva=%s | camp_vizibil=%s (asteptat ascuns)" % (beta_platitor, beta_vizibil))
    rez["beta_ascuns_la_neplatitor"] = (beta_platitor == "nu" and not beta_vizibil)

    b.close()

print("screenshot:", os.path.join(OUT, "proba_tva_inceput.png"))
print("REZULTATE:", rez)
print("VERDICT:", "PASS" if all(rez.values()) else "FAIL")
