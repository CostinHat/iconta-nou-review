# -*- coding: utf-8 -*-
"""Scan tintit axe 'region'/'landmark-*' pe dashboard + o fereastra deschisa. Raporteaza nodurile (selectori)."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
TID = 8396
NUME = "ALFA MICRO"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v


def call(path, payload=None, tok=None, method=None):
    h = {"Content-Type": "application/json"}
    if tok: h["Authorization"] = "Bearer " + tok
    data = json.dumps(payload).encode() if payload is not None else None
    return json.load(urllib.request.urlopen(urllib.request.Request(BAZA + path, data, h, method=method), timeout=60))


_d = call("/auth/login", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
TOK = _d["token"]
INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(TOK) + ');'
        'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(_d["user"])) + ');')
AXE = open(os.path.expanduser("~/iconta_nou/frontend_test/vizual/axe.min.js"), encoding="utf-8").read()

RUN = """async () => {
  const r = await axe.run(document, {runOnly:{type:'rule',values:['region','landmark-unique','landmark-one-main','landmark-complementary-is-top-level','landmark-no-duplicate-banner','landmark-no-duplicate-contentinfo','landmark-banner-is-top-level']}, resultTypes:['violations']});
  return r.violations.map(v => ({id:v.id, impact:v.impact, n:v.nodes.length,
    targets:v.nodes.slice(0,12).map(nd => nd.target.join(' '))}));
}"""

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1300, "height": 2200}); ctx.add_init_script(INIT)
    pg = ctx.new_page()

    # 1) DASHBOARD
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(800)
    pg.evaluate(AXE)
    print("=== DASHBOARD ===")
    for v in pg.evaluate(RUN):
        print(" %-42s impact=%-8s noduri=%d" % (v["id"], v["impact"], v["n"]))
        for t in v["targets"]:
            print("      -", t)

    # 2) FEREASTRA DESCHISA (firma -> declaratii)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text(NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(600)
    pg.evaluate(AXE)
    print("=== FEREASTRA DESCHISA (Declaratii) ===")
    for v in pg.evaluate(RUN):
        print(" %-42s impact=%-8s noduri=%d" % (v["id"], v["impact"], v["n"]))
        for t in v["targets"]:
            print("      -", t)
    # structura landmark curenta
    print("=== LANDMARKS in DOM ===")
    lm = pg.evaluate("""() => {
      const q = s => [...document.querySelectorAll(s)].length;
      return {header:q('header'), main:q('main'), nav:q('nav'), footer:q('footer'),
              role_dialog:q('[role=dialog]'), overlay:q('.fereastra-overlay'),
              subbara:q('.subbara'), bara3:q('.bara3')};
    }""")
    print(json.dumps(lm))
