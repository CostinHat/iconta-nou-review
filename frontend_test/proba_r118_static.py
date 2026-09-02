# -*- coding: utf-8 -*-
"""PROBA R118 — o eroare de sintaxa scrisa in arborele de lucru NU MAI AJUNGE la un browser.

**Conditia de deblocare a lui R118, luata literal:** *„se inchide cand o eroare de sintaxa introdusa
deliberat intr-un modul importat de `cabinet.js` nu mai poate ajunge la un browser fara sa treaca o
poarta."* Proba o executa, pe acelasi modul si pe aceeasi clasa de greseala ca instanta masurata pe
01.09 (ghilimea romaneasca inchisa cu `"` ASCII, in `supervizor.js`, importat de `cabinet.js`).

CELE PATRU LUCRURI PE CARE LE MASOARA:
  1. ce se serveste ACUM vine din directorul PUBLICAT, nu din arbore (amprenta o spune);
  2. dupa ce arborele e stricat, octetii serviti prin HTTP raman NESCHIMBATI;
  3. publicarea REFUZA sa duca mai departe un `.js` care nu se parseaza — cu numele fisierului;
  4. desktopul cabinetului se randeaza in continuare, cu arborele stricat pe disc.

**Arborele se reface in `finally`, si refacerea se VERIFICA pe octeti.** O proba care strica un
fisier al repo-ului si nu dovedeste ca l-a pus la loc e mai rea decat lipsa ei.
"""
import hashlib
import io
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
OUT = os.path.dirname(os.path.abspath(__file__))

#: Modulul pe care s-a produs instanta reala (01.09) — si care e importat de `cabinet.js`.
TINTA = os.path.join(RAD, "static", "js", "ecrane", "supervizor.js")
#: Aceeasi clasa de greseala ca instanta reala: sirul se DESCHIDE cu ghilimea romaneasca `„` si se
#: inchide cu `"` ASCII. `„` nu e un inceput de token valid -> `Invalid or unexpected token`.
#:
#: **Prima forma a mutatiei era JS VALID** — pusesem `„` INAUNTRUL unui sir normal, ceea ce e doar
#: un caracter oarecare. Instrumentul a raspuns corect (n-avea ce refuza), iar proba a picat pe
#: aserttiunea EI, nu pe aplicatie. *O mutatie care nu muta nimic n-are ce dovedi — si e chiar
#: felul de calibrare pe care METODA §22 il cere verificat in amandoua directiile.*
STRICARE = '\nconst _proba_r118 = „text cu ghilimea gresita";\n'


def servit(cale_web):
    r = urllib.request.urlopen(BAZA + cale_web, timeout=30)
    return r.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


ORIGINAL = io.open(TINTA, "rb").read()
SHA_ORIGINAL = sha(ORIGINAL)
print("modul tinta: %s (sha %s, %d octeti)" % (os.path.relpath(TINTA, RAD), SHA_ORIGINAL,
                                               len(ORIGINAL)))

d = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
req = urllib.request.Request(BAZA + "/auth/login", d, {"Content-Type": "application/json"})
_d = json.load(urllib.request.urlopen(req, timeout=60))
INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(_d["token"]) + ');'
        'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(_d["user"])) + ');')

try:
    # ── 1. ce se serveste vine din directorul publicat ────────────────────────────────────────
    amprenta = json.loads(servit("/static/.publicat.json").decode("utf-8"))
    print("1. amprenta a ce se serveste:", amprenta)
    assert amprenta.get("sursa") in ("commit", "arbore de lucru"), amprenta
    inainte = servit("/static/js/ecrane/supervizor.js")
    print("   servit acum: sha %s (%d octeti)" % (sha(inainte), len(inainte)))

    # ── 2. arborele se strica; ce se serveste NU se misca ─────────────────────────────────────
    io.open(TINTA, "wb").write(ORIGINAL + STRICARE.encode("utf-8"))
    stricat_pe_disc = io.open(TINTA, "rb").read()
    assert sha(stricat_pe_disc) != SHA_ORIGINAL, "stricarea n-a schimbat fisierul"
    dupa = servit("/static/js/ecrane/supervizor.js")
    print("2. dupa stricarea arborelui, servit: sha %s" % sha(dupa))
    assert dupa == inainte, (
        "STRICAREA A AJUNS LA BROWSER: octetii serviti s-au schimbat odata cu arborele de lucru. "
        "Asta e chiar R118, nereparata.")

    # ── 3. publicarea REFUZA sa duca mai departe un .js care nu se parseaza ───────────────────
    r = subprocess.run(["./venv/bin/python", "scripts/publica_static.py", "--din-arbore"],
                       cwd=RAD, capture_output=True, text=True, timeout=300)
    iesire = (r.stdout or "") + (r.stderr or "")
    print("3. publicarea din arbore stricat -> cod %d" % r.returncode)
    print("   %s" % iesire.strip().splitlines()[0] if iesire.strip() else "")
    assert r.returncode != 0, "publicarea a ACCEPTAT un .js care nu se parseaza"
    assert "supervizor.js" in iesire, (
        "refuzul nu numeste fisierul vinovat, deci nu se poate repara din el: %r" % iesire[:300])
    dupa2 = servit("/static/js/ecrane/supervizor.js")
    assert dupa2 == inainte, "publicarea refuzata a atins totusi ce se serveste"

    # ── 4. desktopul cabinetului se randeaza in continuare ────────────────────────────────────
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1250, "height": 1400})
        ctx.add_init_script(INIT)
        pg = ctx.new_page()
        erori = []
        pg.on("pageerror", lambda e: erori.append(str(e)))
        pg.goto(BAZA + "/", wait_until="networkidle")
        pg.wait_for_selector(".cab-card", timeout=25000)
        carduri = len(pg.query_selector_all(".cab-card"))
        pg.screenshot(path=os.path.join(OUT, "r118_desktop_cu_arborele_stricat.png"), full_page=True)
        print("4. desktop randat cu arborele stricat: %d carduri · erori JS: %r" % (carduri, erori))
        assert carduri >= 10, "desktopul nu s-a randat (%d carduri)" % carduri
        assert not erori, "erori JS in pagina: %r" % erori[:2]
finally:
    # Arborele se reface, SI se republica: pasul 3 incearca o publicare, iar daca modulul ar fi fost
    # valid ea ar fi reusit — deci ce se serveste trebuie readus la starea de dinainte, nu presupus.
    io.open(TINTA, "wb").write(ORIGINAL)
    refacut = io.open(TINTA, "rb").read()
    assert sha(refacut) == SHA_ORIGINAL, (
        "ARBORELE N-A FOST REFACUT: sha %s != %s" % (sha(refacut), SHA_ORIGINAL))
    subprocess.run(["./venv/bin/python", "scripts/publica_static.py", "--din-arbore"],
                   cwd=RAD, capture_output=True, text=True, timeout=300)
    servit_final = servit("/static/js/ecrane/supervizor.js")
    assert sha(servit_final) == SHA_ORIGINAL, (
        "CE SE SERVESTE n-a revenit la original: sha %s != %s" % (sha(servit_final), SHA_ORIGINAL))
    print("arborele refacut si republicat, verificat pe octeti: sha %s" % sha(refacut))

print("PROBA R118 OK: arborele stricat NU ajunge la browser; publicarea refuza si numeste "
      "fisierul; desktopul ramane intreg.")
