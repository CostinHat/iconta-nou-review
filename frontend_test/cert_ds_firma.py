# -*- coding: utf-8 -*-
"""Certificare DS in browser - ecrane FIRMA-level (cabinet 4163, ALFA).
Navigheaza Firme -> Firme existente -> ALFA -> enumereaza cardurile de operatiuni ale firmei,
verifica pe fiecare DOM randat: modal/panou non-gol, 0 erori consola, clase DS."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"): k, v = ln.split("=", 1); CFG[k] = v
_b = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(urllib.request.Request(BAZA + "/auth/login", _b, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_d["user"])) + ");")
BTN_OK = r"/buton-|btn-|cab-card|nav-|sageata|pastila|optiune|-card|-clic|sa-cifra|mig-|firme-|acces-|meniu-|op-|semafor|strat/"

def intra_firma(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme", exact=True).first.click(); pg.wait_for_timeout(700)
    pg.get_by_text("Firme existente", exact=False).first.click(); pg.wait_for_timeout(700)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(); pg.wait_for_timeout(1000)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True); ctx = b.new_context(); ctx.add_init_script(INIT); pg = ctx.new_page()
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERR:" + str(e)[:50]))
    intra_firma(pg)
    corp = (pg.query_selector(".fereastra").inner_text() or "")[:120].replace("\n", " ")
    print("ecran firma ALFA (corp):", corp)
    # enumereaza cardurile/optiunile de operatiuni ale firmei
    carduri = pg.eval_on_selector_all(".fereastra .cab-card .cab-card-titlu, .fereastra .firme-optiune, .fereastra [class*=op-card]",
        "els=>[...new Set(els.map(e=>e.textContent.trim().split('\\n')[0].slice(0,26)).filter(x=>x&&x.length>1))]")
    print("ECRANE operatiuni firma (%d):" % len(carduri), carduri)
    rez = []
    for t in carduri:
        errs.clear()
        try:
            intra_firma(pg)  # reincarca stare curata
            pg.get_by_text(t, exact=False).first.click(timeout=5000); pg.wait_for_timeout(800)
        except Exception as e:
            rez.append((t, "CLICK-FAIL", str(e).splitlines()[0][:34])); continue
        fer = pg.query_selector_all(".fereastra")
        top = fer[-1] if fer else None
        if not top:
            rez.append((t, "FARA-PANOU", "nimic randat")); continue
        txt = (top.inner_text() or "").strip()
        btns = pg.eval_on_selector_all(".fereastra button",
            "els=>els.filter(e=>!(e.className||'').match(" + BTN_OK + ")).map(e=>e.className||'(fara)')")
        st = "BLANK" if len(txt) < 3 else ("CERR" if errs else "OK")
        det = "cerr=%d btn_neDS=%d" % (len(errs), len(btns))
        if btns: det += " " + str(btns[:2])
        rez.append((t, st, det))
    print("\n%-24s %-10s %s" % ("ECRAN FIRMA", "STARE", "DETALII"))
    for t, st, det in rez:
        print("  %-24s %-10s %s%s" % (t[:24], st, det, "" if st == "OK" else "  <<<"))
    b.close()
