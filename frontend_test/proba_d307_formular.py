# -*- coding: utf-8 -*-
"""Traseu REAL D307 (Regula 14): din ecranul Declaratii pe firma reala (ALFA MICRO) -> D307 (scos din
_DOAR_API) -> genereaza pe formular gol (refuz cu mesaj de contabil, fara nume interne) -> adauga operatiuni
de ajustare TVA (lista) -> Regenereaza -> DUKIntegrator VALID. Capturi privite + axe + mobil (Pixel5)."""
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
call("/tenants/%d/firma-profil/date" % TARGET_TID,
     {"declarant_nume": "Pop", "declarant_prenume": "Ion", "declarant_functie": "administrator"}, TOK, "POST")
INIT = ("sessionStorage.setItem(\"iconta_token\"," + json.dumps(TOK) + ");"
        "sessionStorage.setItem(\"iconta_user\"," + json.dumps(json.dumps(_d["user"])) + ");")


def adauga_op(pg, tip, cod, den, tva):
    pg.select_option("#d307-tip", tip)
    pg.fill("#d307-cod", cod); pg.fill("#d307-den", den); pg.fill("#d307-tva", str(tva))
    pg.click("#d307-add"); pg.wait_for_timeout(300)


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1950}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(700)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text(TARGET_NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)

    assert pg.query_selector("#dec-tip option[value=\"d307\"]"), "d307 LIPSESTE din selectorul de tipuri"
    pg.select_option("#dec-tip", "d307"); pg.wait_for_timeout(500)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2026"); pg.dispatch_event("#dec-an", "change")
    if pg.query_selector("#dec-luna"):
        pg.select_option("#dec-luna", "6")
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua"); pg.wait_for_timeout(5000)

    # PASUL 1: formular gol -> refuz cu mesaj de CONTABIL + panoul randat
    eroare = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    panou = pg.query_selector("#dec-d307-form") is not None
    print("D307 in dropdown: True")
    print("EROARE pe formular gol:", repr((eroare or "")[:220]))
    print("PANOU #dec-d307-form randat pe eroare:", panou)
    pg.screenshot(path=os.path.join(OUT, "d307_1_gol_refuz.png"), full_page=True)
    assert panou, "formularul D307 trebuie randat CHIAR pe eroarea de generare (chicken-and-egg)"
    assert "operațiune" in (eroare or "").lower(), "eroarea trebuie sa fie in limba contabilului: %r" % (eroare or "")[:200]
    for intern in ("operatiuni", "denO", "codO", "d_anulare", "manual", "declarant_nume"):
        assert intern not in (eroare or ""), "eroarea expune nume intern %r: %s" % (intern, eroare)

    # PASUL 2: adauga operatiuni de ajustare (transfer active + anulare cod TVA cu TVA negativ la regularizare)
    adauga_op(pg, "A", "14399840", "Cedent Active SRL", 5000)
    adauga_op(pg, "C", "8000", "Beneficiar SRL", -1200)
    nr = len(pg.query_selector_all("#dec-d307-form .dec-man-rand"))
    total_txt = pg.eval_on_selector("#dec-d307-form .camp-ajutor", "e=>e.innerText")
    print("OPERATIUNI adaugate:", nr, "| TOTAL afisat:", repr(total_txt))
    pg.screenshot(path=os.path.join(OUT, "d307_2_completat.png"), full_page=True)
    assert nr == 2, "trebuie 2 operatiuni in lista"
    assert "3.800" in total_txt or "3800" in total_txt, "total ajustare = 5000 + (-1200) = 3800: %r" % total_txt

    # PASUL 3: Regenereaza -> DUKIntegrator
    pg.click("#d307-regen"); pg.wait_for_timeout(10000)
    stare_ok = pg.query_selector(".dec-ok") is not None
    ok_txt = pg.eval_on_selector(".dec-ok", "e=>e.innerText") if stare_ok else ""
    er_txt = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    xml_txt = pg.eval_on_selector(".dec-xml-pre", "e=>e.textContent") if pg.query_selector(".dec-xml-pre") else ""
    print("DUK stare valid (.dec-ok):", stare_ok, "|", repr(ok_txt[:140]))
    print("EROARE dupa regen:", repr(er_txt[:200]))
    print("XML tvaA=5000:", 'tvaA="5000"' in xml_txt, "| tvaC=-1200:", 'tvaC="-1200"' in xml_txt, "| operatii:", xml_txt.count("<operatie "))
    pg.screenshot(path=os.path.join(OUT, "d307_3_dupa_regen.png"), full_page=True)
    assert stare_ok, "DUK trebuie sa dea 'valid' pe D307 completat; eroare=%r" % er_txt[:200]
    assert 'tvaA="5000"' in xml_txt and xml_txt.count("<operatie ") == 2, "XML-ul trebuie sa aiba tvaA + 2 operatii"

    # Regula 14: axe pe formularul D307
    AXE = open(os.path.join(OUT, "vizual", "axe.min.js"), encoding="utf-8").read()
    pg.evaluate(AXE)
    axe_res = pg.evaluate("""async () => {
      const r = await axe.run('#dec-d307-form', {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
      const C=new Set(['color-contrast','color-contrast-enhanced']);
      const L=new Set(['label','select-name','aria-input-field-name','button-name','link-name','input-button-name','form-field-multiple-labels']);
      let contrast=0,label=0,alte=[];
      for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
      return {contrast, label, alte};
    }""")
    print("AXE pe #dec-d307-form -> contrast:", axe_res["contrast"], "| fara-eticheta:", axe_res["label"], "| alte:", axe_res["alte"])

    # Regula 14: profil telefon Pixel5
    mob = b.new_context(viewport={"width": 393, "height": 851}, device_scale_factor=2.75, is_mobile=True, has_touch=True)
    mob.add_init_script(INIT)
    mp = mob.new_page()
    mp.goto(BAZA + "/", wait_until="networkidle"); mp.wait_for_selector(".cab-card", timeout=25000); mp.wait_for_timeout(600)
    mp.get_by_text("Firme", exact=True).first.click(timeout=8000); mp.wait_for_timeout(400)
    mp.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    mp.wait_for_selector("button.firme-rand", timeout=10000)
    mp.get_by_text(TARGET_NUME, exact=False).first.click(timeout=8000)
    mp.wait_for_selector("#fa-declaratii", timeout=10000); mp.click("#fa-declaratii")
    mp.wait_for_selector("#dec-tip", timeout=15000); mp.wait_for_timeout(300)
    mp.select_option("#dec-tip", "d307"); mp.wait_for_timeout(400)
    if mp.query_selector("#dec-luna"): mp.select_option("#dec-luna", "6")
    mp.wait_for_selector("#dec-continua:not([disabled])", timeout=8000); mp.click("#dec-continua"); mp.wait_for_timeout(5000)
    mob_form = mp.query_selector("#dec-d307-form") is not None
    body_w = mp.evaluate("() => document.body.scrollWidth")
    print("MOBIL (Pixel5) formular randat:", mob_form, "| body scrollWidth:", body_w, "(<=393 = fara revarsare)")
    mp.screenshot(path=os.path.join(OUT, "d307_4_mobil.png"), full_page=True)

    assert axe_res["contrast"] == 0 and axe_res["label"] == 0, "axe: contrast/eticheta pe formularul D307: %r" % axe_res
    assert mob_form and body_w <= 400, "formularul D307 trebuie randat pe telefon fara revarsare orizontala (body=%s)" % body_w
    print("PROBA OK: D307 in selector, gol refuzat cu mesaj de contabil, completat -> DUK VALID; axe curat; mobil OK")
