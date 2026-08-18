# -*- coding: utf-8 -*-
"""Scan 'region' pe TOATE cele 5 ECRANE problematice + dashboard. Confirma 0 app-wide dupa fix-ul de landmarks.
Capturi dashboard + o fereastra pentru privire (Regula 14: restructurarea barelor sa nu schimbe vizual)."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import INIT, BAZA
from nav_ecrane import ECRANE

HERE = os.path.dirname(os.path.abspath(__file__))
AXE = open(os.path.join(HERE, "axe.min.js"), encoding="utf-8").read()
OUT = os.path.expanduser("~/iconta_nou/frontend_test")
RUN = """async () => {
  const r = await axe.run(document, {runOnly:{type:'rule',values:['region','landmark-unique','landmark-one-main','landmark-complementary-is-top-level','landmark-no-duplicate-banner','landmark-banner-is-top-level']}, resultTypes:['violations']});
  return r.violations.map(v => ({id:v.id, n:v.nodes.length, targets:v.nodes.slice(0,8).map(nd=>nd.target.join(' '))}));
}"""

total = 0
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1300, "height": 2200}); ctx.add_init_script(INIT)
    pg = ctx.new_page()

    # dashboard
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(800)
    pg.evaluate(AXE)
    v = pg.evaluate(RUN); n = sum(x["n"] for x in v); total += n
    print("dashboard: region/landmark noduri =", n, ([(x["id"], x["n"]) for x in v] if v else "CURAT"))
    pg.screenshot(path=os.path.join(OUT, "landmarks_dashboard.png"), full_page=True)

    for nume, fn in ECRANE:
        pg2 = ctx.new_page()
        try:
            fn(pg2)
            pg2.evaluate(AXE)
            v = pg2.evaluate(RUN); n = sum(x["n"] for x in v); total += n
            print("%-22s region/landmark noduri = %d %s" % (nume, n, ([(x["id"], x["n"], x["targets"]) for x in v] if v else "CURAT")))
            if nume == "plan_conturi":
                pg2.screenshot(path=os.path.join(OUT, "landmarks_fereastra.png"), full_page=True)
        except Exception as e:
            print("%-22s EROARE navigare: %s" % (nume, str(e)[:120]))
        finally:
            pg2.close()

print("TOTAL region/landmark noduri app-wide:", total)
