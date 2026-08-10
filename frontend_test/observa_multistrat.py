# -*- coding: utf-8 -*-
"""OBSERVA multi-strat (fara fix), cabinet 4163. Firul + destinatia back-ului la FIECARE nivel.
Ruleaza: venv/bin/python3 frontend_test/observa_multistrat.py"""
import os, json, urllib.request
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

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
        "e=>{var h=e.querySelector('h2,.pf-titlu,.mig-intro');return (h?h.textContent:e.textContent).trim().slice(0,45);}")
def desktop(pg):
    pg.goto(B + "/", wait_until="domcontentloaded"); pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
def clk(pg, txt, to=10000):
    pg.get_by_text(txt, exact=False).first.click(timeout=to); pg.wait_for_timeout(700)

print("===== MIGRARE MULTI-STRAT (per-firma) — fir + back la fiecare nivel =====")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True); ctx = b.new_context(); ctx.add_init_script(INIT); pg = ctx.new_page()
    try:
        desktop(pg)
        for t in ["Firme", "Firme existente", "ALFA MICRO", "Import date"]:
            clk(pg, t)
        pusher = corp(pg)
        print("pusher (meniu per-firma):", repr(pusher), "| fir:", fir(pg))
        # A) secvential FARA back intre straturi (reproduce acumularea din bug)
        print("\n-- A) click strat dupa strat, FARA back intre ele --")
        for strat in ["Solduri ini", "Salaria", "Istoric"]:
            try:
                clk(pg, strat)
                print("  dupa click %-10s -> corp=%r | FIR=%r" % (strat, corp(pg), fir(pg)))
                # revin la meniu ca sa dau iar click pe alt strat (cum face un contabil)
                pg.click(".nav-inapoi"); pg.wait_for_timeout(700)
                print("    back      %-10s -> corp=%r | fir=%r" % ("", corp(pg), fir(pg)))
            except Exception as e:
                print("  strat %s: %s" % (strat, str(e).splitlines()[0][:80]))
        # B) adancime: intra intr-un strat, apoi sub-pasul lui (mergi Import·firma), back la fiecare nivel
        print("\n-- B) adancime in Solduri: nivel1 (strat) -> back --")
    except Exception as e:
        print("EROARE migrare:", type(e).__name__, str(e)[:120])
    b.close()

print("\n===== PACHETE / SETARI — daca pasul nu se gaseste, dumpez etichetele reale =====")
for card, step in [("Pachete lunare", "Pachetul"), ("Setări cont", "Parol")]:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True); ctx = b.new_context(); ctx.add_init_script(INIT); pg = ctx.new_page()
        try:
            desktop(pg); clk(pg, card, to=12000)
            print("\n[%s] corp dupa deschidere: %r" % (card, corp(pg)))
            btns = pg.eval_on_selector_all("button, .mig-frand, .rap-tab, a", "els=>els.map(e=>e.textContent.trim().slice(0,30)).filter(t=>t)")
            print("  etichete clickabile:", btns[:20])
            try:
                clk(pg, step, to=6000); print("  dupa click '%s' -> corp=%r | fir=%r" % (step, corp(pg), fir(pg)))
            except PWTimeout:
                print("  '%s' NU e clickabil (vezi etichetele reale de mai sus)" % step)
        except Exception as e:
            print("[%s] EROARE deschidere: %s" % (card, str(e).splitlines()[0][:100]))
        b.close()
