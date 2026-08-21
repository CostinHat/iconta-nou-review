# -*- coding: utf-8 -*-
"""Proba randare reala pentru defectele #6 (latime rand total) si #5 (curgere mesaj eroare).
Ruleaza cu venv Playwright pe server. Arg1: eticheta faza (inainte/dupa)."""
import os, sys, json, urllib.request
from playwright.sync_api import sync_playwright

FAZA = sys.argv[1] if len(sys.argv) > 1 else "faza"
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
OUT = os.path.expanduser("~/iconta_nou/frontend_test")

CS_JS = """el=>{if(!el)return null;const c=getComputedStyle(el);const r=el.getBoundingClientRect();
return {w:Math.round(r.width*100)/100,h:Math.round(r.height*100)/100,
display:c.display,justify:c.justifyContent,maxW:c.maxWidth,flexShrink:c.flexShrink,
width_css:c.width,marginLeft:c.marginLeft};}"""

def measure(pg, sel):
    return pg.eval_on_selector(sel, CS_JS) if pg.query_selector(sel) else None

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)

    # ---------- PROBA #6: randul de total in formularul de emitere ----------
    ctx = b.new_context(viewport={"width": 1100, "height": 1500}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(500)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-facturi", timeout=10000)
    pg.click("#fa-facturi"); pg.wait_for_timeout(500)
    pg.wait_for_selector("#fac-emite", timeout=10000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-da, #em-add-linie", timeout=12000); pg.wait_for_timeout(300)
    if pg.query_selector("#em-da"):
        if pg.query_selector("#em-tva-nu"):
            pg.click("#em-tva-nu"); pg.wait_for_timeout(150)
        pg.click("#em-nu"); pg.wait_for_timeout(300)
        pg.wait_for_selector("#em-salveaza-config2", timeout=8000)
        pg.click("#em-salveaza-config2")
    pg.wait_for_selector("#em-add-linie", timeout=12000); pg.wait_for_timeout(500)
    # completez o linie ca sa apara sume reale
    pg.fill("#em-l0-descriere", "Consultanță contabilă")
    pg.fill("#em-l0-cantitate", "3")
    pg.fill("#em-l0-pret_unitar", "1250.50")
    pg.eval_on_selector("#em-l0-pret_unitar", "e=>e.dispatchEvent(new Event('input',{bubbles:true}))")
    pg.wait_for_timeout(500)

    print("=== #6 TOTAL (%s) ===" % FAZA)
    for sel in ["#em-total", ".em-total-rand:not(.em-total-mare)", ".em-total-mare"]:
        print(sel, "->", measure(pg, sel))
    # pozitia Total vs suma in randul mare
    pos = pg.eval_on_selector(".em-total-mare", """row=>{
      const sp=row.querySelector('span'), b=row.querySelector('b');
      const rs=sp.getBoundingClientRect(), rb=b.getBoundingClientRect();
      return {label_right:Math.round(rs.right), suma_left:Math.round(rb.left),
      gap:Math.round(rb.left-rs.right), label_txt:sp.textContent, suma_txt:b.textContent,
      row_left:Math.round(row.getBoundingClientRect().left),
      row_right:Math.round(row.getBoundingClientRect().right)};}""")
    print("#6 pozitii:", pos)
    print("#6 verdict: label si suma", "SEPARATE" if pos["gap"] > 20 else "LIPITE (gap=%dpx)" % pos["gap"])
    pg.screenshot(path=os.path.join(OUT, "def6_total_%s.png" % FAZA), clip=None, full_page=True)
    # decupaj strans pe zona de total
    el = pg.query_selector("#em-total")
    el.screenshot(path=os.path.join(OUT, "def6_total_crop_%s.png" % FAZA))
    print("screenshot:", os.path.join(OUT, "def6_total_crop_%s.png" % FAZA))
    ctx.close()

    # ---------- PROBA #5: mesaj de eroare lung in poarta de configurare ----------
    ctx2 = b.new_context(viewport={"width": 1100, "height": 1400}); ctx2.add_init_script(INIT)
    pg2 = ctx2.new_page()
    # fortez poarta de numerotare neconfigurata ca sa declansez validarea mesajului lung
    def _ruta(route):
        route.fulfill(status=200, content_type="application/json",
                      body=json.dumps({"serie": None, "urmator_numar": 1, "configurata": False}))
    pg2.route("**/facturi/numerotare", _ruta)
    pg2.goto(BAZA + "/", wait_until="domcontentloaded")
    pg2.wait_for_selector(".cab-card", timeout=15000); pg2.wait_for_timeout(400)
    pg2.get_by_text("Firme", exact=True).first.click(timeout=8000); pg2.wait_for_timeout(500)
    pg2.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg2.wait_for_selector("button.firme-rand", timeout=10000); pg2.wait_for_timeout(300)
    pg2.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg2.wait_for_selector("#fa-facturi", timeout=10000)
    pg2.click("#fa-facturi"); pg2.wait_for_timeout(500)
    pg2.wait_for_selector("#fac-emite", timeout=10000)
    pg2.click("#fac-emite")
    pg2.wait_for_selector("#em-da", timeout=12000); pg2.wait_for_timeout(300)
    pg2.click("#em-da"); pg2.wait_for_timeout(300)
    pg2.wait_for_selector("#em-salveaza-config", timeout=8000)
    # las #em-ultim gol -> mesajul lung
    pg2.click("#em-salveaza-config"); pg2.wait_for_timeout(500)
    pg2.wait_for_selector(".msg-eroare", timeout=6000)
    info = pg2.eval_on_selector(".msg-eroare", """el=>{
      const c=getComputedStyle(el); const r=el.getBoundingClientRect();
      // numar de randuri vizuale ~ inaltime / line-height
      const lh=parseFloat(c.lineHeight)|| (parseFloat(c.fontSize)*1.2);
      const par=el.parentElement.getBoundingClientRect();
      return {w:Math.round(r.width),h:Math.round(r.height),lines:Math.round(r.height/lh),
      whiteSpace:c.whiteSpace, overflowWrap:c.overflowWrap, wordBreak:c.wordBreak,
      overflow:c.overflow, textOverflow:c.textOverflow,
      scrollW:el.scrollWidth, clientW:el.clientWidth,
      clipped_h: el.scrollHeight>Math.ceil(r.height)+1,
      clipped_w: el.scrollWidth>Math.ceil(r.width)+1,
      parent_overflow:getComputedStyle(el.parentElement).overflow,
      fits_in_parent: r.right<=par.right+1, txt:el.textContent};}""")
    print("=== #5 MESAJ EROARE (%s) ===" % FAZA)
    print("#5 info (mesaj real):", info)
    # test stres: token lung nespargibil -> fara overflow-wrap ar depasi/taia parintele de 520px
    tok = pg2.eval_on_selector(".msg-eroare", """el=>{
      el.textContent='Verifica CUI-ul: RO00000000000000000000000000000000000000000000000000 nevalid.';
      const c=getComputedStyle(el); const r=el.getBoundingClientRect();
      const par=el.parentElement.getBoundingClientRect();
      return {w:Math.round(r.width), scrollW:el.scrollWidth,
      overflows_parent: r.right>par.right+1,
      clipped_w: el.scrollWidth>Math.ceil(r.width)+1,
      overflowWrap:c.overflowWrap, wordBreak:c.wordBreak};}""")
    print("#5 token nespargibil:", tok,
          "->", "CONTINUT (nu depaseste parintele)" if not tok["overflows_parent"] and not tok["clipped_w"]
          else "DEPASESTE/TAIE parintele")
    pg2.wait_for_timeout(200)
    print("#5 verdict:", "CURGE pe %d randuri, netaiat" % info["lines"]
          if (info["lines"] >= 2 and not info["clipped_w"] and not info["clipped_h"])
          else "PROBLEMA (taiat sau pe 1 rand)")
    pg2.screenshot(path=os.path.join(OUT, "def5_eroare_%s.png" % FAZA), full_page=True)
    box = pg2.query_selector(".em-config")
    if box: box.screenshot(path=os.path.join(OUT, "def5_eroare_crop_%s.png" % FAZA))
    print("screenshot:", os.path.join(OUT, "def5_eroare_crop_%s.png" % FAZA))
    ctx2.close()
    b.close()
print("GATA", FAZA)
