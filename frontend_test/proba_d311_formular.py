# -*- coding: utf-8 -*-
"""Traseu REAL D311 (Regula 14): din ecranul Declaratii pe o firma reala din demo (ALFA MICRO) ->
selecteaza D311 (scos din _DOAR_API) -> genereaza pe formular gol (refuz cu mesaj de CONTABIL, fara nume
interne) -> completeaza situatiile fiscale de dupa anularea codului de TVA -> Regenereaza -> DUKIntegrator
VALID. Capturi privite. Firma trebuie sa aiba declarant (obligatoriu D311) - il setam via API oficial."""
import os, json, urllib.request, urllib.error
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
TARGET_TID = 8396
TARGET_NUME = "ALFA MICRO"
OUT = os.path.dirname(os.path.abspath(__file__))
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v


def call(path, payload=None, tok=None, method=None):
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BAZA + path, data, h, method=method)
    return json.load(urllib.request.urlopen(r, timeout=60))


_d = call("/auth/login", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
TOK = _d["token"]
# firma trebuie sa aiba declarant ca sa depuna orice (D311 il cere) - il asiguram via API oficial
call("/tenants/%d/firma-profil/date" % TARGET_TID,
     {"declarant_nume": "Pop", "declarant_prenume": "Ion", "declarant_functie": "administrator"}, TOK, "POST")
INIT = ("sessionStorage.setItem(\"iconta_token\"," + json.dumps(TOK) + ");"
        "sessionStorage.setItem(\"iconta_user\"," + json.dumps(json.dumps(_d["user"])) + ");")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1950}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(700)
    # navigheaza fix la firma tinta (per-firma) -> ecranul ei de Declaratii
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text(TARGET_NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)

    # D311 in dropdown (scos din _DOAR_API)
    assert pg.query_selector("#dec-tip option[value=\"d311\"]"), "d311 LIPSESTE din selectorul de tipuri"
    pg.select_option("#dec-tip", "d311"); pg.wait_for_timeout(500)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2026"); pg.dispatch_event("#dec-an", "change")
    if pg.query_selector("#dec-luna"):
        pg.select_option("#dec-luna", "6")
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua"); pg.wait_for_timeout(5000)

    # PASUL 1: formular gol -> refuz cu mesaj de CONTABIL + panoul randat (chicken-and-egg)
    eroare = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    panou = pg.query_selector("#dec-d311-form") is not None
    print("D311 in dropdown: True")
    print("EROARE pe formular gol:", repr((eroare or "")[:220]))
    print("PANOU #dec-d311-form randat pe eroare:", panou)
    pg.screenshot(path=os.path.join(OUT, "d311_1_gol_refuz.png"), full_page=True)
    assert panou, "formularul D311 trebuie randat CHIAR pe eroarea de generare (chicken-and-egg)"
    assert "situați" in (eroare or "").lower() or "data anulării" in (eroare or "").lower() or "sumă" in (eroare or "").lower(), \
        "eroarea trebuie sa fie in limba contabilului: %r" % (eroare or "")[:200]
    for intern in ("Data_A", "d_anul1", "d_anul2", "OB_51", "OB_11", "manual"):
        assert intern not in (eroare or ""), "eroarea expune nume intern %r: %s" % (intern, eroare)

    # PASUL 2: completeaza situatiile fiscale dupa anularea codului de TVA
    pg.fill("#d311-data", "2026-03-15")
    pg.select_option("#d311-motiv", "1")
    for cid, val in (("d311-OB_11", "10000"), ("d311-OB_12", "1900"), ("d311-OB_21", "2000"), ("d311-OB_22", "380")):
        pg.fill("#" + cid, val); pg.dispatch_event("#" + cid, "input")
    pg.wait_for_timeout(400)
    total_txt = pg.eval_on_selector("#dec-d311-form .camp-ajutor", "e=>e.innerText")
    print("TOTAL control afisat:", repr(total_txt))
    pg.screenshot(path=os.path.join(OUT, "d311_2_completat.png"), full_page=True)
    # Regula 14.2: cifra afisata (total control) coincide cu ce genereaza serverul (OB_51+OB_52=14280)
    assert "14.280" in total_txt or "14280" in total_txt, "totalul de control afisat trebuie sa fie 14.280 lei: %r" % total_txt

    # PASUL 3: Regenereaza -> DUKIntegrator
    pg.click("#d311-regen"); pg.wait_for_timeout(10000)
    stare_ok = pg.query_selector(".dec-ok") is not None
    ok_txt = pg.eval_on_selector(".dec-ok", "e=>e.innerText") if stare_ok else ""
    er_txt = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    xml_txt = pg.eval_on_selector(".dec-xml-pre", "e=>e.textContent") if pg.query_selector(".dec-xml-pre") else ""
    print("DUK stare valid (.dec-ok):", stare_ok, "|", repr(ok_txt[:140]))
    print("EROARE dupa regen:", repr(er_txt[:200]))
    print("XML totalPlata_A=14280:", 'totalPlata_A="14280"' in xml_txt, "| OB_51=12000:", 'OB_51="12000"' in xml_txt)
    pg.screenshot(path=os.path.join(OUT, "d311_3_dupa_regen.png"), full_page=True)

    assert stare_ok, "DUK trebuie sa dea 'valid' pe D311 completat corect; eroare=%r" % er_txt[:200]
    assert 'totalPlata_A="14280"' in xml_txt and 'OB_51="12000"' in xml_txt, "XML-ul trebuie sa aiba totalul calculat corect"

    # Regula 14: axe-core pe ecranul ATINS (formularul D311, randat in wizard). Injectam axe vandorizat.
    AXE = open(os.path.join(OUT, "vizual", "axe.min.js"), encoding="utf-8").read()
    pg.evaluate(AXE)
    axe_res = pg.evaluate("""async () => {
      const r = await axe.run('#dec-d311-form', {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
      const C=new Set(['color-contrast','color-contrast-enhanced']);
      const L=new Set(['label','select-name','aria-input-field-name','button-name','link-name','input-button-name','form-field-multiple-labels']);
      let contrast=0,label=0,alte=[];
      for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
      return {contrast, label, alte, total:r.violations.length};
    }""")
    print("AXE pe #dec-d311-form -> contrast:", axe_res["contrast"], "| fara-eticheta:", axe_res["label"], "| alte:", axe_res["alte"])

    # Regula 14: profil telefon (Pixel 5) - formularul se randeaza pe ecran mic, tinte de atingere.
    mob = b.new_context(viewport={"width": 393, "height": 851}, device_scale_factor=2.75,
                        is_mobile=True, has_touch=True); mob.add_init_script(INIT)
    mp = mob.new_page()
    mp.goto(BAZA + "/", wait_until="networkidle"); mp.wait_for_selector(".cab-card", timeout=25000); mp.wait_for_timeout(600)
    mp.get_by_text("Firme", exact=True).first.click(timeout=8000); mp.wait_for_timeout(400)
    mp.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    mp.wait_for_selector("button.firme-rand", timeout=10000)
    mp.get_by_text(TARGET_NUME, exact=False).first.click(timeout=8000)
    mp.wait_for_selector("#fa-declaratii", timeout=10000); mp.click("#fa-declaratii")
    mp.wait_for_selector("#dec-tip", timeout=15000); mp.wait_for_timeout(300)
    mp.select_option("#dec-tip", "d311"); mp.wait_for_timeout(400)
    if mp.query_selector("#dec-luna"): mp.select_option("#dec-luna", "6")
    mp.wait_for_selector("#dec-continua:not([disabled])", timeout=8000); mp.click("#dec-continua"); mp.wait_for_timeout(5000)
    mob_form = mp.query_selector("#dec-d311-form") is not None
    # tinta de atingere sub 24px inaltime pe inputurile de suma? (ghid minim ~24px)
    hmin = mp.eval_on_selector_all("#dec-d311-form .camp-input", "els=>Math.min(...els.map(e=>e.getBoundingClientRect().height))") if mob_form else 0
    print("MOBIL (Pixel5) formular randat:", mob_form, "| inaltime minima camp-input:", round(hmin or 0, 1), "px")
    mp.screenshot(path=os.path.join(OUT, "d311_4_mobil.png"), full_page=True)

    assert axe_res["contrast"] == 0 and axe_res["label"] == 0, "axe: contrast/eticheta pe formularul D311: %r" % axe_res
    assert mob_form, "formularul D311 trebuie sa se randeze si pe profil telefon"
    print("PROBA OK: D311 in selector, formular gol refuzat cu mesaj de contabil, completat -> DUK VALID; axe curat; mobil OK")
