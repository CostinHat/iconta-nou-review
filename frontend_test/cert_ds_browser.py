# -*- coding: utf-8 -*-
"""Certificare DS IN BROWSER (pagina randata, nu verificator static) - cabinet 4163.
Pentru fiecare card din grila cabinetului: click -> verifica pe DOM randat."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright

BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"): k, v = ln.split("=", 1); CFG[k] = v
_body = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(urllib.request.Request(
    BAZA + "/auth/login", _body, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_d["user"])) + ");")

# clase de buton legitime DS (regex JS)
BTN_OK = r"/buton-|btn-|cab-card|nav-|sageata|pastila|optiune|-card|-clic|sa-cifra|mig-|firme-|acces-|meniu-/"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERR:" + str(e)[:60]))
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(600)
    titluri = pg.eval_on_selector_all(".cab-card .cab-card-titlu", "els=>els.map(e=>e.textContent.trim())")
    print("CARDURI in grila cabinet:", len(titluri))
    rez = []
    for t in titluri:
        errs.clear()
        # stare curata: reincarca grila inainte de fiecare card (evita modaluri lipite)
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
        errs.clear()
        try:
            pg.get_by_text(t, exact=True).first.click(timeout=6000); pg.wait_for_timeout(700)
        except Exception as e:
            rez.append((t, "CLICK-FAIL", str(e).splitlines()[0][:38])); continue
        fer = pg.query_selector(".fereastra")
        if not fer:
            rez.append((t, "FARA-MODAL", "nu s-a deschis .fereastra"))
        else:
            txt = (fer.inner_text() or "").strip()
            btns = pg.eval_on_selector_all(".fereastra button",
                "els=>els.filter(e=>!(e.className||'').match(" + BTN_OK + ")).map(e=>e.className||'(fara-clasa)')")
            inp = pg.eval_on_selector_all(
                ".fereastra input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=file]), .fereastra select",
                "els=>els.filter(e=>!(e.className||'').match(/camp-input/)).map(e=>e.tagName.toLowerCase()+'.'+(e.className||'(fara)'))")
            st = "BLANK" if len(txt) < 3 else ("CERR" if errs else "OK")
            det = "cerr=%d btn_neDS=%d inp_neDS=%d" % (len(errs), len(btns), len(inp))
            if btns: det += " | btn:" + str(btns[:2])
            if inp: det += " | inp:" + str(inp[:2])
            rez.append((t, st, det))
        x = pg.query_selector(".fereastra .nav-x, .fereastra .nav-inapoi")
        try:
            (x.click(timeout=2000) if x else pg.keyboard.press("Escape")); pg.wait_for_timeout(300)
        except Exception:
            pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    print("\n%-24s %-10s %s" % ("CARD", "STARE", "DETALII"))
    for t, st, det in rez:
        print("  %-24s %-10s %s%s" % (t[:24], st, det, "" if st == "OK" else "  <<<"))
    b.close()
