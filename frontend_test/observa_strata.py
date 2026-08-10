# -*- coding: utf-8 -*-
"""OBSERVA calea 'Migrare cabinet' (meniu straturi, deschide=ferestre) — reproduce bug-ul? fir la fiecare nivel."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright

def _env(p):
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1); d[k] = v
    return d
C = _env(os.path.expanduser("~/.iconta/fe_test.env")); B = C["FE_TEST_BAZA"]
bd = json.dumps({"email": C["FE_TEST_EMAIL"], "parola": C["FE_TEST_PAROLA"]}).encode()
d = json.load(urllib.request.urlopen(urllib.request.Request(B + "/auth/login", bd, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(d["user"])) + ");")

def fir(pg):
    return pg.eval_on_selector_all(".fereastra-fir .fir-veriga", "els=>els.map(e=>e.textContent.trim())")
def corp(pg):
    return pg.eval_on_selector(".fereastra-corp",
        "e=>{var h=e.querySelector('h2,.pf-titlu,.mig-intro');return (h?h.textContent:e.textContent).trim().slice(0,40);}")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True); ctx = b.new_context(); ctx.add_init_script(INIT); pg = ctx.new_page()
    pg.goto(B + "/", wait_until="domcontentloaded"); pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme", exact=False).first.click(timeout=12000); pg.wait_for_timeout(800)
    pg.get_by_text("Migrare cabinet", exact=False).first.click(timeout=12000); pg.wait_for_timeout(900)
    print("dupa 'Migrare cabinet': corp=%r | FIR=%r" % (corp(pg), fir(pg)))
    for strat in ["Solduri ini", "Salaria", "Istoric declara"]:
        try:
            pg.get_by_text(strat, exact=False).first.click(timeout=10000); pg.wait_for_timeout(900)
            print("\nclick %-14s -> corp=%r\n   FIR=%r" % (strat, corp(pg), fir(pg)))
            pg.click(".nav-inapoi"); pg.wait_for_timeout(900)
            print("   back        -> corp=%r | fir=%r" % (corp(pg), fir(pg)))
        except Exception as e:
            print("\nstrat %s EROARE: %s" % (strat, str(e).splitlines()[0][:90]))
    # acum secvential FARA back intre straturi (cum ar naviga cineva rapid)
    print("\n-- secvential fara back (Solduri->Salariati->Istoric) --")
    pg.get_by_text("Firme", exact=False).first.click(timeout=8000); pg.wait_for_timeout(600)
    pg.get_by_text("Migrare cabinet", exact=False).first.click(timeout=8000); pg.wait_for_timeout(700)
    for strat in ["Solduri ini", "Salaria", "Istoric declara"]:
        try:
            pg.get_by_text(strat, exact=False).first.click(timeout=8000); pg.wait_for_timeout(700)
            print("  dupa %-14s FIR=%r" % (strat, fir(pg)))
            pg.get_by_text("Migrare cabinet", exact=False).first.click(timeout=5000); pg.wait_for_timeout(500)
        except Exception as e:
            print("  %s: %s" % (strat, str(e).splitlines()[0][:70]))
    b.close()
