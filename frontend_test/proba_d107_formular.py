# -*- coding: utf-8 -*-
"""Traseu REAL D107 (Regula 14): din ecranul Declaratii pe firma reala (ALFA MICRO) -> D107 (scos din
_DOAR_API) -> genereaza pe formular gol (refuz cu mesaj de contabil, fara nume interne) -> adauga beneficiari
ai sponsorizarilor (lista, cu trei sume) -> Regenereaza -> DUKIntegrator VALID. Capturi privite + axe + mobil (Pixel5)."""
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


def adauga_benef(pg, den, cif, adr, v1, v2, v3):
    pg.fill("#d107-den", den); pg.fill("#d107-cif", cif); pg.fill("#d107-adr", adr)
    pg.fill("#d107-val1", str(v1)); pg.fill("#d107-val2", str(v2)); pg.fill("#d107-val3", str(v3))
    pg.click("#d107-add"); pg.wait_for_timeout(300)


def deschide_d107(pg):
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(700)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text(TARGET_NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 2100}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    deschide_d107(pg)

    assert pg.query_selector("#dec-tip option[value=\"d107\"]"), "d107 LIPSESTE din selectorul de tipuri"
    pg.select_option("#dec-tip", "d107"); pg.wait_for_timeout(500)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2024"); pg.dispatch_event("#dec-an", "change")
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua"); pg.wait_for_timeout(5000)

    # PASUL 1: formular gol -> refuz cu mesaj de CONTABIL + panoul randat
    eroare = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    panou = pg.query_selector("#dec-d107-form") is not None
    print("D107 in dropdown: True")
    print("EROARE pe formular gol:", repr((eroare or "")[:220]))
    print("PANOU #dec-d107-form randat pe eroare:", panou)
    pg.screenshot(path=os.path.join(OUT, "d107_1_gol_refuz.png"), full_page=True)
    assert panou, "formularul D107 trebuie randat CHIAR pe eroarea de generare (chicken-and-egg)"
    assert "beneficiar" in (eroare or "").lower(), "eroarea trebuie sa fie in limba contabilului: %r" % (eroare or "")[:200]
    for intern in ("denE", "cifE", "adrE", "Val1", "Val2_NI", "cod_oblig", "totalPlata_A", "declarant_nume"):
        assert intern not in (eroare or ""), "eroarea expune nume intern %r: %s" % (intern, eroare)

    # PASUL 2: adauga beneficiari (Asociatia Alfa + Fundatia Beta - CUI-uri valide DUK)
    adauga_benef(pg, "Asociatia Alfa", "12345674", "Str ONG 2 Cluj", 5000, 2000, 3000)
    adauga_benef(pg, "Fundatia Beta", "45678918", "Str ONG 3 Iasi", 3000, 0, 3000)
    nr = len(pg.query_selector_all("#dec-d107-form .dec-man-rand"))
    total_txt = pg.eval_on_selector("#d107-totaluri", "e=>e.innerText")
    print("BENEFICIARI adaugati:", nr, "| TOTALURI afisate:", repr(total_txt))
    pg.screenshot(path=os.path.join(OUT, "d107_2_completat.png"), full_page=True)
    assert nr == 2, "trebuie 2 beneficiari in lista"
    # TVal1=8000, TVal2=2000, TVal3=6000, total control=16000
    assert ("16.000" in total_txt or "16000" in total_txt), "suma de control = 16000: %r" % total_txt

    # PASUL 3: Regenereaza -> DUKIntegrator
    pg.click("#d107-regen"); pg.wait_for_timeout(11000)
    stare_ok = pg.query_selector(".dec-ok") is not None
    ok_txt = pg.eval_on_selector(".dec-ok", "e=>e.innerText") if stare_ok else ""
    er_txt = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    xml_txt = pg.eval_on_selector(".dec-xml-pre", "e=>e.textContent") if pg.query_selector(".dec-xml-pre") else ""
    print("DUK stare valid (.dec-ok):", stare_ok, "|", repr(ok_txt[:140]))
    print("EROARE dupa regen:", repr(er_txt[:200]))
    print("XML Val1=5000:", 'Val1="5000"' in xml_txt, "| TVal1=8000:", 'TVal1="8000"' in xml_txt,
          "| entit:", xml_txt.count("<entit "))
    pg.screenshot(path=os.path.join(OUT, "d107_3_dupa_regen.png"), full_page=True)
    assert stare_ok, "DUK trebuie sa dea 'valid' pe D107 completat; eroare=%r" % er_txt[:200]
    assert 'Val1="5000"' in xml_txt and xml_txt.count("<entit ") == 2, "XML-ul trebuie sa aiba Val1 + 2 <entit>"

    # Regula 14: axe pe formularul D107
    AXE = open(os.path.join(OUT, "vizual", "axe.min.js"), encoding="utf-8").read()
    pg.evaluate(AXE)
    axe_res = pg.evaluate("""async () => {
      const r = await axe.run('#dec-d107-form', {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
      const C=new Set(['color-contrast','color-contrast-enhanced']);
      const L=new Set(['label','select-name','aria-input-field-name','button-name','link-name','input-button-name','form-field-multiple-labels']);
      let contrast=0,label=0,alte=[];
      for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
      return {contrast, label, alte};
    }""")
    print("AXE pe #dec-d107-form -> contrast:", axe_res["contrast"], "| fara-eticheta:", axe_res["label"], "| alte:", axe_res["alte"])

    # Regula 14: profil telefon Pixel5
    mob = b.new_context(viewport={"width": 393, "height": 851}, device_scale_factor=2.75, is_mobile=True, has_touch=True)
    mob.add_init_script(INIT)
    mp = mob.new_page()
    deschide_d107(mp)
    mp.select_option("#dec-tip", "d107"); mp.wait_for_timeout(400)
    if mp.query_selector("#dec-an"):
        mp.fill("#dec-an", "2024"); mp.dispatch_event("#dec-an", "change")
    mp.wait_for_selector("#dec-continua:not([disabled])", timeout=8000); mp.click("#dec-continua"); mp.wait_for_timeout(5000)
    mob_form = mp.query_selector("#dec-d107-form") is not None
    body_w = mp.evaluate("() => document.body.scrollWidth")
    print("MOBIL (Pixel5) formular randat:", mob_form, "| body scrollWidth:", body_w, "(<=393 = fara revarsare)")
    mp.screenshot(path=os.path.join(OUT, "d107_4_mobil.png"), full_page=True)

    assert axe_res["contrast"] == 0 and axe_res["label"] == 0, "axe: contrast/eticheta pe formularul D107: %r" % axe_res
    assert mob_form and body_w <= 400, "formularul D107 trebuie randat pe telefon fara revarsare orizontala (body=%s)" % body_w
    print("PROBA OK: D107 in selector, gol refuzat cu mesaj de contabil, completat -> DUK VALID; axe curat; mobil OK")
