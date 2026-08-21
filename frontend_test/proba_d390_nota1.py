# -*- coding: utf-8 -*-
"""Traseu REAL D390 NOTA 1: ecran principal -> Declaratii -> D390 -> firma -> panoul de clasificare;
verifica optiunea 'A (NOTA 1)' in selectorul manual + adauga o linie manuala A (cod gol)."""
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
INIT = ("sessionStorage.setItem(\"iconta_token\"," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem(\"iconta_user\"," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.dirname(os.path.abspath(__file__))

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(700)
    card = pg.query_selector(".cab-card:has(.cab-card-sinteza[data-cheie=\"declaratii\"])")
    if card:
        card.click()
    else:
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000)
        pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)
    # ALFA MICRO (8396) are D390 aplicabil (verificat via /declaratii/tipuri)
    if pg.query_selector("#dec-firma"):
        pg.select_option("#dec-firma", "8396"); pg.wait_for_timeout(1200)
    pg.wait_for_selector("#dec-tip option[value=\"d390\"]", timeout=8000, state="attached")
    print("d390 disabled =", pg.eval_on_selector("#dec-tip option[value=\"d390\"]", "e=>e.disabled"))
    pg.select_option("#dec-tip", "d390"); pg.wait_for_timeout(600)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2026"); pg.dispatch_event("#dec-an", "change")
    if pg.query_selector("#dec-luna"):
        pg.select_option("#dec-luna", "8")
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_timeout(5000)
    # DIAGNOSTIC: ce s-a randat dupa continue
    ids = pg.evaluate("() => Array.from(document.querySelectorAll('[id]')).map(e=>e.id).filter(i=>i.indexOf('dec')>=0 || i.indexOf('d390')>=0 || i.indexOf('man')>=0)")
    print("ID-uri prezente:", ids)
    corp_txt = pg.evaluate("() => (document.querySelector('#dec-corp')||document.body).innerText.slice(0,600)")
    print("CORP TEXT[0:600]:", repr(corp_txt))
    pg.screenshot(path=os.path.join(OUT, "d390_pas2.png"), full_page=True)
    if pg.query_selector("#dec-d390-clasif details"):
        pg.eval_on_selector("#dec-d390-clasif details", "e=>e.open=true"); pg.wait_for_timeout(300)
    pg.wait_for_selector("#man-tip", timeout=15000)
    optiuni = pg.eval_on_selector_all("#man-tip option", "els=>els.map(e=>[e.value,e.textContent])")
    print("OPTIUNI #man-tip:", optiuni)
    have_A = any(v == "A" for v, _t in optiuni)
    nota = pg.eval_on_selector_all(".ecran-nota", "els=>els.map(e=>e.textContent).filter(t=>t.indexOf('NOTA 1')>=0)")
    print("NOTA 1 pe ecran:", nota[:1])
    pg.screenshot(path=os.path.join(OUT, "d390_nota1_ecran.png"), full_page=True)
    assert have_A, "optiunea A (NOTA 1) LIPSESTE din selectorul manual D390"
    # adauga o linie manuala A: tara DE, cod gol
    pg.select_option("#man-tip", "A")
    pg.fill("#man-tara", "DE"); pg.fill("#man-cod", ""); pg.fill("#man-den", "FURNIZOR DE FARA COD")
    pg.fill("#man-baza", "5000")
    pg.click("#man-add"); pg.wait_for_timeout(1500)
    randuri = pg.eval_on_selector_all(".dec-man-rand", "els=>els.map(e=>e.innerText.replace(/\\n/g,' | '))")
    print("RANDURI MANUALE dupa adaugare:", randuri)
    eroare = pg.eval_on_selector("#dec-clasif-msg", "e=>e.innerText") if pg.query_selector("#dec-clasif-msg") else ""
    print("mesaj eroare (gol=ok):", repr(eroare))
    pg.screenshot(path=os.path.join(OUT, "d390_nota1_dupa_add.png"), full_page=True)
    ok = any("FURNIZOR DE FARA COD" in r for r in randuri)
    print("REZULTAT: linia manuala A adaugata =", ok)
    assert ok, "linia manuala A (NOTA 1) nu a fost adaugata"
    print("PROBA OK: optiunea A (NOTA 1) se randeaza SI se poate adauga o achizitie fara cod")
