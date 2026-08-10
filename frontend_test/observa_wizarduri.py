# -*- coding: utf-8 -*-
"""OBSERVA (fara fix) back-ul real per wizard, cabinet 4163. Nu modifica cod, nu aserteaza verdict.
Ruleaza: venv/bin/python3 frontend_test/observa_wizarduri.py"""
import os, json, urllib.request
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

def _env(p):
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            d[k] = v
    return d

CFG = _env(os.path.expanduser("~/.iconta/fe_test.env"))
BAZA = CFG["FE_TEST_BAZA"]
_body = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(
    urllib.request.Request(BAZA + "/auth/login", _body, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token', " + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user', " + json.dumps(json.dumps(_d["user"])) + ");")

def fir(pg):
    return pg.eval_on_selector_all(".fereastra-fir .fir-veriga", "els => els.map(e => e.textContent.trim())")

def corp(pg):
    return pg.eval_on_selector(".fereastra-corp",
        "e => { var h = e.querySelector('h2, .pf-titlu, .mig-intro'); "
        "var t = h ? h.textContent : e.textContent; return t.trim().slice(0, 55); }")

def desktop(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(400)

def clk(pg, txt):
    pg.get_by_text(txt, exact=False).first.click(timeout=12000)
    pg.wait_for_timeout(800)

def obs(pg, wizard, path, step):
    r = {"w": wizard, "reach": "?", "acum": "?", "dest": "?", "div": "?", "note": ""}
    try:
        desktop(pg)
        for t in path:
            clk(pg, t)
        c_before = corp(pg)          # ecranul-pusher (de unde se cheama mergi spre step)
        clk(pg, step)                # ecran intrat prin mergi
        r["reach"] = "da"
        f1 = fir(pg)
        pg.click(".nav-inapoi"); pg.wait_for_timeout(800)
        dest = corp(pg)
        clk(pg, step)                # re-enter
        f2 = fir(pg)
        r["acum"] = "DA" if (len(f2) > len(f1) or any(f2.count(x) > 1 for x in f2)) else "nu"
        r["dest"] = dest
        r["div"] = "SCHIMBA->pusher" if dest[:18] != c_before[:18] else "nu (back=pusher)"
        r["note"] = "pusher=%r f1=%r f2=%r dest=%r" % (c_before, f1, f2, dest)
    except PWTimeout as e:
        r["note"] = "TIMEOUT: " + str(e).splitlines()[0][:110]
    except Exception as e:
        r["note"] = "EROARE %s: %s" % (type(e).__name__, str(e)[:110])
    return r

REZ = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context()
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    REZ.append(obs(pg, "migrare(per-firma)", ["Firme", "Firme existente", "ALFA MICRO", "Import date"], "Solduri ini"))
    REZ.append(obs(pg, "firme(salariati)", ["Firme", "Firme existente", "ALFA MICRO"], "Salaria"))
    REZ.append(obs(pg, "facturi_ecran", ["Firme", "Firme existente", "ALFA MICRO"], "Facturi"))
    REZ.append(obs(pg, "pachete", ["Pachete lunare"], "Pachetul"))
    REZ.append(obs(pg, "setari", ["Setări cont"], "Parol"))
    b.close()

print("WIZARD | reachable | antet acumuleaza | dest back ACUM | fix pop-priority schimba?")
for r in REZ:
    print("  %-20s | %-8s | %-16s | %-28s | %s" % (r["w"], r["reach"], r["acum"], str(r["dest"])[:28], r["div"]))
for r in REZ:
    print("  [%s] %s" % (r["w"], r["note"]))
