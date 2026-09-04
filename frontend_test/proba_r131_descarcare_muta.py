# -*- coding: utf-8 -*-
"""PROBA R131 — mesajul serverului ajunge la OM cand o descarcare esueaza.

Campania intreaba pe rute: *vorbeste aplicatia cand primeste date gresite?* Pe ecran intrebarea
are alta forma: **refuzul serverului ajunge la om, sau se pierde pe drum?**

Cele 13 descarcari de fisier nu pot trece prin `api.get` (raspunsul e binar), deci chemau `fetch`
direct si ocoleau `_refuzNevazut`. Toate aruncau motivul serverului: `throw new Error("eroare " +
r.status)`. Serverul spunea *„chitanta inexistenta"*; omul citea *„eroare 404"*.

CE MASOARA, in browser adevarat, pe codul PUBLICAT:
  1. `descarca()` pe o ruta care refuza ARUNCA o eroare care poarta motivul serverului, verbatim
     — nu numarul, nu o fraza proprie;
  2. bannerul apare in DOM **si e VIZIBIL** (are arie pe ecran, in viewport) — nu doar prezent;
  3. textul bannerului contine motivul serverului;
  4. **nu se dubleaza**: daca ecranul a aratat deja mesajul, bannerul nu mai apare a doua oara
     (altfel omul ar citi acelasi refuz de doua ori, in doua locuri);
  5. `deschide()` — cealalta forma — se poarta la fel.

CE NU MASOARA, declarat: nu parcurge cele 32 de ecrane apasandu-le butoanele. Masoara DRUMUL
COMUN prin care trec acum toate cele 13 descarcari — daca el tace, tac toate; daca el vorbeste,
mesajul are cum sa ajunga. Ce face fiecare ecran cu eroarea DUPA ce o primeste e treaba lui
`scan_refuz_tacut.py` (27.08.2026), care masoara exact acel drum.
"""
import json
import os
import subprocess
import urllib.request

from playwright.sync_api import sync_playwright

CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1)
        CFG[k] = v
BAZA = os.environ.get("PROBE_BAZA") or CFG.get("FE_TEST_BAZA", "http://127.0.0.1:8010")
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRMA = 8396          # ALFA MICRO — firma utilizatorului de proba din ~/.iconta/fe_test.env


def api(path, method="GET", body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(BAZA + path, data=data, headers=h, method=method)
    return json.load(urllib.request.urlopen(req, timeout=90))


d = api("/auth/login", "POST", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
TOK, USER = d["token"], d["user"]
INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(TOK) + ');'
        'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(USER)) + ');')

r = subprocess.run(["./venv/bin/python", "scripts/publica_static.py", "--din-arbore"],
                   cwd=RAD, capture_output=True, text=True, timeout=300)
assert r.returncode == 0, "publicarea a esuat: %s" % ((r.stdout or "") + (r.stderr or ""))[:400]
print("publicat din arbore, ca sa se probeze codul care se va comite")

#: Ruta refuza cu un motiv PROPRIU — cel pe care omul trebuie sa-l citeasca.
CALE = "/tenants/%d/facturi/999999/pdf" % FIRMA
MOTIV = "factură inexistentă"

JS_DESCARCA = """
async (cale) => {
  const m = await import("/static/js/api.js");
  try { await m.descarca(cale, "x.pdf"); return { aruncat: null }; }
  catch (e) { return { aruncat: { cod: e.cod, mesaj: e.mesaj, message: e.message } }; }
}
"""
JS_DESCHIDE = """
async (cale) => {
  const m = await import("/static/js/api.js");
  try { await m.deschide(cale); return { aruncat: null }; }
  catch (e) { return { aruncat: { cod: e.cod, mesaj: e.mesaj } }; }
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1000})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000)

    # ── 1. eroarea poarta motivul serverului ─────────────────────────────────────────────
    rez = pg.evaluate(JS_DESCARCA, CALE)
    a = rez["aruncat"]
    assert a, "descarcarea unei facturi inexistente NU a esuat — proba nu masoara nimic"
    print("1. aruncat:", a)
    assert a.get("mesaj") == MOTIV, (
        "eroarea nu poarta motivul serverului, ci %r — exact defectul reparat: omul citea "
        "„eroare 404” in loc de ce spusese serverul." % (a.get("mesaj"),))
    assert a.get("cod") == 404, "codul s-a pierdut: %r" % (a.get("cod"),)

    # ── 2+3. bannerul apare, e VIZIBIL, si spune motivul ─────────────────────────────────
    pg.wait_for_selector("#refuz-nevazut", timeout=5000)
    cutie = pg.eval_on_selector("#refuz-nevazut", """el => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return { w: r.width, h: r.height, sus: r.top, jos: r.bottom,
               vizibilitate: s.visibility, afisare: s.display, opac: s.opacity,
               text: (el.innerText || "").trim(), rol: el.getAttribute("role") };
    }""")
    print("2. banner:", {k: v for k, v in cutie.items() if k != "text"})
    print("   text:", cutie["text"].replace("\n", " · "))
    assert cutie["w"] > 0 and cutie["h"] > 0, "bannerul e in DOM dar n-are arie pe ecran: %r" % cutie
    assert cutie["afisare"] != "none" and cutie["vizibilitate"] != "hidden", "banner ascuns: %r" % cutie
    assert float(cutie["opac"]) > 0.1, "banner transparent: %r" % cutie
    assert cutie["sus"] < 1000 and cutie["jos"] > 0, (
        "bannerul e in afara ecranului (sus=%s jos=%s) — in DOM, dar omul nu-l vede"
        % (cutie["sus"], cutie["jos"]))
    assert MOTIV in cutie["text"], "bannerul nu spune motivul: %r" % cutie["text"]
    assert cutie["rol"] == "alert", "bannerul nu se anunta cititorului de ecran (role=%r)" % cutie["rol"]

    # ── 4. nu se dubleaza cand ecranul a aratat deja mesajul ─────────────────────────────
    pg.evaluate("() => { document.getElementById('refuz-nevazut')?.remove(); }")
    pg.evaluate("""(motiv) => {
      const d = document.createElement("div");
      d.id = "proba-r131-ecran";
      d.textContent = motiv;              // ecranul si-a aratat singur refuzul
      document.body.appendChild(d);
    }""", MOTIV)
    pg.evaluate(JS_DESCARCA, CALE)
    pg.wait_for_timeout(1500)
    dublat = pg.query_selector("#refuz-nevazut")
    print("4. cand ecranul arata deja mesajul, banner suplimentar:", bool(dublat))
    assert dublat is None, "refuzul se arata de doua ori: o data de ecran, o data de banner"
    pg.evaluate("() => document.getElementById('proba-r131-ecran')?.remove()")

    # ── 5. `deschide()` se poarta la fel ─────────────────────────────────────────────────
    rez2 = pg.evaluate(JS_DESCHIDE, CALE)
    print("5. deschide() ->", rez2["aruncat"])
    assert rez2["aruncat"] and rez2["aruncat"].get("mesaj") == MOTIV, (
        "`deschide()` pierde motivul: %r" % (rez2["aruncat"],))
    pg.wait_for_selector("#refuz-nevazut", timeout=5000)

    assert not erori, "erori JS in pagina: %r" % erori[:3]

print("PROBA R131 OK: refuzul serverului ajunge la om, verbatim si vizibil, prin ambele forme.")
