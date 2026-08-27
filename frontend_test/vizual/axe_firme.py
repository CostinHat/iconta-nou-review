# -*- coding: utf-8 -*-
"""axe-core pe ECRANUL DE FIRME, cel pe care l-am schimbat azi (R78: randul are acum o actiune
langa el; R77: caseta de alegere). `axe_scan.py` merge pe cele 5 ecrane din nav_ecrane — lista de
firme nu e printre ele, deci schimbarea de azi n-ar fi fost vazuta de nimeni.
Ruleaza PE SERVER, din ~/iconta_nou/frontend_test/vizual/."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from playwright.sync_api import sync_playwright
from w_auth import INIT, BAZA

AXE = open(os.path.join(HERE, "axe.min.js"), encoding="utf-8").read()
CONTRAST = {"color-contrast", "color-contrast-enhanced"}
ETICHETA = {"label", "select-name", "aria-input-field-name", "button-name", "link-name",
            "input-button-name"}


def scan(pg, unde):
    pg.add_script_tag(content=AXE)
    r = pg.evaluate("async () => await axe.run(document)")
    v = r["violations"]
    # Anti-vacuum: un scan care n-a inspectat nimic raporteaza tot „0 violari". Deci intreb intai
    # cate noduri a apucat sa vada.
    treceri = sum(len(x["nodes"]) for x in r.get("passes", []))
    assert treceri > 20, ("axe n-a inspectat nimic (treceri=%d) — «0 violari» ar fi o afirmatie "
                          "despre o pagina pe care n-a vazut-o" % treceri)
    print("   [anti-vacuum] noduri inspectate cu succes: %d, pe %d reguli"
          % (treceri, len(r.get("passes", []))))
    print("\n== %s ==  violari: %d" % (unde, len(v)))
    for x in v:
        print("   [%-8s] %-28s x%d  %s" % (x.get("impact"), x["id"], len(x["nodes"]),
                                           x["help"][:60]))
        for n in x["nodes"][:2]:
            print("        %s" % (n["html"][:110].replace("\n", " ")))
    return {x["id"]: len(x["nodes"]) for x in v}


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 900}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(500)
    a = scan(pg, "lista de firme (R78: rand + actiune)")

    pg.locator("button.firme-rand-scoate").first.click(); pg.wait_for_timeout(1200)
    c = scan(pg, "ecranul de scoatere")

    # [R81] ecranul de date, unde a intrat campul denumirii din portofoliu
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(400)
    pg.locator("button.firme-rand").first.click()
    pg.wait_for_selector("#fa-datefirma", timeout=12000); pg.wait_for_timeout(400)
    pg.locator("#fa-datefirma").click()
    pg.wait_for_selector("#df-nume-portofoliu", timeout=12000); pg.wait_for_timeout(700)
    e = scan(pg, "Date firma (R81: doua denumiri, numite distinct)")

    total = {}
    for d in (a, c, e):
        for k, n in d.items():
            total[k] = total.get(k, 0) + n
    print("\nrezumat: contrast=%d | fara eticheta=%d | total violari=%d"
          % (sum(n for k, n in total.items() if k in CONTRAST),
             sum(n for k, n in total.items() if k in ETICHETA), sum(total.values())))
    print(json.dumps(total, indent=None, sort_keys=True))
    b.close()
