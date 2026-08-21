# -*- coding: utf-8 -*-
"""Traseu REAL D207 (Regula 14): din ecranul Declaratii pe firma reala (ALFA MICRO) -> D207 (scos din
_DOAR_API) -> genereaza pe formular gol (refuz cu mesaj de contabil, fara nume interne) -> adauga un
beneficiar nerezident (dividende, tip impozabil) -> Regenereaza -> DUKIntegrator VALID.
Capturi privite + axe + mobil (Pixel5)."""
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


def setval(pg, sel, val):
    pg.fill(sel, str(val)); pg.dispatch_event(sel, "change"); pg.wait_for_timeout(150)


def deschide_d207(pg):
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
    ctx = b.new_context(viewport={"width": 1300, "height": 2400}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    deschide_d207(pg)

    assert pg.query_selector("#dec-tip option[value=\"d207\"]"), "d207 LIPSESTE din selectorul de tipuri"
    pg.select_option("#dec-tip", "d207"); pg.wait_for_timeout(500)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2025"); pg.dispatch_event("#dec-an", "change")
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua"); pg.wait_for_timeout(5000)

    # PASUL 1: formular gol -> refuz cu mesaj de CONTABIL + panoul randat
    eroare = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    panou = pg.query_selector("#dec-d207-form") is not None
    print("D207 in dropdown: True")
    print("EROARE pe formular gol:", repr((eroare or "")[:240]))
    print("PANOU #dec-d207-form randat pe eroare:", panou)
    pg.screenshot(path=os.path.join(OUT, "d207_1_gol_refuz.png"), full_page=True)
    assert panou, "formularul D207 trebuie randat CHIAR pe eroarea de generare (chicken-and-egg)"
    assert "beneficiar" in (eroare or "").lower(), "eroarea trebuie sa fie in limba contabilului: %r" % (eroare or "")[:200]
    for intern in ("tip_venit", "Stat_R", "cifR", "cifS", "den1", "baza1", "imp1", "imps1", "Act_N", "totalPlata_A", "Tbaza", "Tscutit", "nrben"):
        assert intern not in (eroare or ""), "eroarea expune nume intern %r: %s" % (intern, eroare)

    # verifica nomenclatorul sursat in dropdown (impozabile + scutite)
    n_opt = len(pg.query_selector_all("#d207-tip option"))
    has_scutit = pg.query_selector("#d207-tip option[value=\"12\"]") is not None
    print("TIP VENIT optiuni:", n_opt, "| are cod scutit 12:", has_scutit)
    assert n_opt >= 25 and has_scutit, "nomenclatorul tip venit trebuie complet (25 coduri, impozabile+scutite)"

    # PASUL 2: adauga un beneficiar nerezident impozabil (dividende, tip 01)
    pg.select_option("#d207-tip", "01")
    pg.fill("#d207-den", "Nonresident Holdings Ltd")
    pg.fill("#d207-stat", "DE")
    pg.fill("#d207-cifs", "DE811234567")
    pg.select_option("#d207-act", "1")
    pg.fill("#d207-baza", "10000")
    pg.fill("#d207-imp", "800")
    pg.fill("#d207-imps", "0")
    pg.click("#d207-add"); pg.wait_for_timeout(400)
    nr = len(pg.query_selector_all("#dec-d207-form .dec-man-rand"))
    total_txt = pg.eval_on_selector("#d207-totaluri", "e=>e.innerText")
    print("BENEFICIARI adaugati:", nr, "| TOTALURI afisate:", repr(total_txt))
    pg.screenshot(path=os.path.join(OUT, "d207_2_completat.png"), full_page=True)
    assert nr == 1, "trebuie 1 beneficiar in lista"
    # suma de control = nrben(1)+Tbaza(10000)+Timp(800) = 10801 (oglinda calcul_d207)
    assert "10801" in total_txt, "suma de control trebuie 10801: %r" % total_txt
    assert ("10.000" in total_txt or "10000" in total_txt) and "800" in total_txt, "baza 10000 + impozit 800: %r" % total_txt

    # verifica comportarea scutit: la selectarea unui tip scutit, impozitul se dezactiveaza
    pg.select_option("#d207-tip", "12"); pg.wait_for_timeout(200)
    imp_dis = pg.eval_on_selector("#d207-imp", "e=>e.disabled")
    nota_sc = pg.eval_on_selector("#d207-scutit-nota", "e=>e.innerText")
    print("SCUTIT: #d207-imp dezactivat:", imp_dis, "| nota:", repr(nota_sc[:80]))
    assert imp_dis and "scutit" in nota_sc.lower(), "la tip scutit impozitul trebuie dezactivat + nota"
    pg.select_option("#d207-tip", "01"); pg.wait_for_timeout(150)  # revino la impozabil

    # PASUL 3: Regenereaza -> DUKIntegrator
    pg.click("#d207-regen"); pg.wait_for_timeout(12000)
    stare_ok = pg.query_selector(".dec-ok") is not None
    ok_txt = pg.eval_on_selector(".dec-ok", "e=>e.innerText") if stare_ok else ""
    er_txt = pg.eval_on_selector(".dec-eroare", "e=>e.innerText") if pg.query_selector(".dec-eroare") else ""
    xml_txt = pg.eval_on_selector(".dec-xml-pre", "e=>e.textContent") if pg.query_selector(".dec-xml-pre") else ""
    print("DUK stare valid (.dec-ok):", stare_ok, "|", repr(ok_txt[:140]))
    print("EROARE dupa regen:", repr(er_txt[:220]))
    print("XML: benef=", xml_txt.count("<benef "), "| sect_II=", xml_txt.count("<sect_II "),
          "| tip_venit1=01:", 'tip_venit1="01"' in xml_txt, "| baza1=10000:", 'baza1="10000"' in xml_txt,
          "| imp1=800:", 'imp1="800"' in xml_txt)
    pg.screenshot(path=os.path.join(OUT, "d207_3_dupa_regen.png"), full_page=True)
    assert stare_ok, "DUK trebuie sa dea 'valid' pe D207 completat; eroare=%r" % er_txt[:240]
    assert xml_txt.count("<benef ") == 1 and 'tip_venit1="01"' in xml_txt and 'baza1="10000"' in xml_txt, \
        "XML-ul trebuie sa aiba 1 benef cu tip_venit1=01, baza1=10000"

    # Regula 14: axe pe formularul D207
    AXE = open(os.path.join(OUT, "vizual", "axe.min.js"), encoding="utf-8").read()
    pg.evaluate(AXE)
    axe_res = pg.evaluate("""async () => {
      const r = await axe.run('#dec-d207-form', {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
      const C=new Set(['color-contrast','color-contrast-enhanced']);
      const L=new Set(['label','select-name','aria-input-field-name','button-name','link-name','input-button-name','form-field-multiple-labels']);
      let contrast=0,label=0,alte=[];
      for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
      return {contrast, label, alte};
    }""")
    print("AXE pe #dec-d207-form -> contrast:", axe_res["contrast"], "| fara-eticheta:", axe_res["label"], "| alte:", axe_res["alte"])

    # Regula 14: profil telefon Pixel5
    mob = b.new_context(viewport={"width": 393, "height": 851}, device_scale_factor=2.75, is_mobile=True, has_touch=True)
    mob.add_init_script(INIT)
    mp = mob.new_page()
    deschide_d207(mp)
    mp.select_option("#dec-tip", "d207"); mp.wait_for_timeout(400)
    if mp.query_selector("#dec-an"):
        mp.fill("#dec-an", "2025"); mp.dispatch_event("#dec-an", "change")
    mp.wait_for_selector("#dec-continua:not([disabled])", timeout=8000); mp.click("#dec-continua"); mp.wait_for_timeout(5000)
    mob_form = mp.query_selector("#dec-d207-form") is not None
    body_w = mp.evaluate("() => document.body.scrollWidth")
    print("MOBIL (Pixel5) formular randat:", mob_form, "| body scrollWidth:", body_w, "(<=393 = fara revarsare)")
    mp.screenshot(path=os.path.join(OUT, "d207_4_mobil.png"), full_page=True)

    assert axe_res["contrast"] == 0 and axe_res["label"] == 0, "axe: contrast/eticheta pe formularul D207: %r" % axe_res
    assert mob_form and body_w <= 400, "formularul D207 trebuie randat pe telefon fara revarsare orizontala (body=%s)" % body_w
    print("PROBA OK: D207 in selector, gol refuzat cu mesaj de contabil, completat -> DUK VALID; axe curat; mobil OK")
