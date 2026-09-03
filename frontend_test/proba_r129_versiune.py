# -*- coding: utf-8 -*-
"""PROBA R129 — aplicatia ANUNTA o publicare noua, si NU intrerupe nimic.

DECIZIA lui Costin (03.09.2026), varianta (a), verbatim: *„aplicatia compara periodic amprenta de
versiune si anunta, fara sa intrerupa. Nu forta reincarcarea — un formular pe jumatate completat
pierdut e mai rau decat defectul."*

CELE PATRU LUCRURI PE CARE LE MASOARA, in ordinea in care conteaza:
  1. inainte de publicare nu exista niciun anunt (altfel „apare mereu" ar trece drept „a detectat");
  2. dupa o publicare noua, anuntul APARE;
  3. **formularul pe jumatate completat SUPRAVIETUIESTE** — textul tastat e neatins, dialogul e inca
     deschis, si pagina NU s-a reincarcat (marcaj pus pe `window` inainte, citit dupa);
  4. anuntul are IESIRE: apasarea lui reincarca — adica omul alege momentul, nu aplicatia.

*A treia e chiar decizia. Fara ea, un anunt care reincarca singur ar trece toate celelalte trei.*
"""
import json
import os
import subprocess
import urllib.error
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
TENANT = 8396          # ALFA MICRO — firma fara constatari CERTE, deci dialogul de depunere e simplu
SPV_TASTAT = "PROBA-R129-4417"


def api(path, method="GET", body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(BAZA + path, data=data, headers=h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=90))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")}


d = api("/auth/login", "POST", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
TOK, USER = d["token"], d["user"]
if (api("/eu/patru-ochi", tok=TOK) or {}).get("activ"):
    api("/eu/patru-ochi", "POST", {"activ": False}, TOK)

coada = (api("/coada", tok=TOK) or {}).get("coada") or []
activ = [c for c in coada if c.get("tenant_id") == TENANT and c.get("stare") in ("la_senior", "aprobata")]
if not activ:
    r = api("/coada", "POST", {"tenant_id": TENANT, "tip": "d300", "an": 2026, "luna": 8}, TOK)
    assert r.get("ok"), "n-am putut pregati un element pentru dialog: %r" % r

INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(TOK) + ');'
        'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(USER)) + ');')


def publica_din_arbore():
    r = subprocess.run(["./venv/bin/python", "scripts/publica_static.py", "--din-arbore"],
                       cwd=RAD, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, "publicarea a esuat: %s" % ((r.stdout or "") + (r.stderr or ""))[:300]
    return json.loads(urllib.request.urlopen(BAZA + "/static/.publicat.json", timeout=30).read())


amprenta_inainte = json.loads(urllib.request.urlopen(BAZA + "/static/.publicat.json",
                                                     timeout=30).read())
print("amprenta servita la pornire:", amprenta_inainte.get("la"))

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1400})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000)
    # Marcaj de RE-INCARCARE: daca pagina se reincarca, `window` e nou si marcajul dispare.
    pg.evaluate("() => { window.__proba_r129 = 'viu'; }")

    # ── 1. inainte de publicare: niciun anunt ─────────────────────────────────────────────────
    assert not pg.query_selector(".versiune-noua"), (
        "anuntul exista INAINTE de vreo publicare noua — atunci n-ar dovedi ca detecteaza ceva")
    stare0 = pg.evaluate("() => window.__stareVersiune ? window.__stareVersiune() : null")
    print("1. fara anunt la pornire. stare modul:", stare0)

    # ── formularul pe jumatate completat: dialogul de depunere, cu index SPV tastat ───────────
    pg.click('.cab-card:has(.cab-card-sinteza[data-cheie="validat"])')
    pg.wait_for_selector(".val-card", timeout=15000)
    subs = pg.eval_on_selector_all(".val-sub", "els=>els.map(e=>e.innerText)")
    i = next(k for k, s in enumerate(subs) if "ALFA MICRO" in (s or ""))
    pg.query_selector_all(".val-depune")[i].click()
    pg.wait_for_selector("#dlg-input", timeout=10000)
    pg.fill("#dlg-input", SPV_TASTAT)
    print("   formular pe jumatate completat: index SPV tastat =", SPV_TASTAT)

    # ── 2. se publica o versiune noua, iar fila afla ──────────────────────────────────────────
    amprenta_dupa = publica_din_arbore()
    print("2. publicat din nou:", amprenta_dupa.get("la"))
    assert amprenta_dupa.get("la") != amprenta_inainte.get("la"), "amprenta nu s-a schimbat"
    # Nu se asteapta cele cinci minute ale ceasului: se foloseste al doilea declansator, cel de la
    # revenirea in fila — exact momentul in care omul se uita oricum la ecran.
    pg.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
    pg.wait_for_selector(".versiune-noua", timeout=20000)
    text = pg.eval_on_selector(".versiune-noua", "e=>e.innerText.trim()")
    titlu = pg.eval_on_selector(".versiune-noua", "e=>e.getAttribute('title')")
    print("   ANUNT:", repr(text), "|", (titlu or "")[:80])
    assert "reîncarcă" in (text or "").lower(), "anuntul nu spune ce are omul de facut: %r" % text

    # ── 3. NU S-A INTRERUPT NIMIC — partea care E decizia ─────────────────────────────────────
    viu = pg.evaluate("() => window.__proba_r129 || null")
    val = pg.eval_on_selector("#dlg-input", "e=>e.value")
    dialog = pg.query_selector("#dlg-ok") is not None
    print("3. dupa anunt -> pagina nereincarcata: %s · text pastrat: %r · dialog deschis: %s"
          % (viu == "viu", val, dialog))
    assert viu == "viu", "PAGINA S-A REINCARCAT — exact ce decizia interzice"
    assert val == SPV_TASTAT, "textul tastat s-a pierdut: %r" % val
    assert dialog, "dialogul s-a inchis — anuntul a intrerupt actul in curs"
    pg.screenshot(path=os.path.join(OUT, "r129_anunt_fara_intrerupere.png"), full_page=True)

    # axe pe antet (bara + bara de stare), cu anuntul in ea
    pg.evaluate(open(os.path.join(OUT, "vizual", "axe.min.js"), encoding="utf-8").read())
    axe_res = pg.evaluate("""async () => {
      const r = await axe.run('.bara-antet', {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
      const C=new Set(['color-contrast','color-contrast-enhanced']);
      const L=new Set(['label','button-name','link-name','aria-input-field-name']);
      let contrast=0,label=0,alte=[];
      for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
      return {contrast, label, alte};
    }""")
    inaltime = pg.eval_on_selector(".versiune-noua", "e=>Math.round(e.getBoundingClientRect().height)")
    print("   axe pe bara:", axe_res, "| inaltimea anuntului:", inaltime)
    assert axe_res["contrast"] == 0 and axe_res["label"] == 0, "axe: %r" % axe_res
    assert inaltime >= 24, "tinta de atingere sub 24px (AA 2.5.8): %s" % inaltime

    # ── 3b. cat timp o fereastra modala e deschisa, anuntul se VEDE dar nu se poate apasa ─────
    # Nu e o scapare, e chiar „nu intrerupe": dialogul deschis pastreaza interactiunea. Anuntul
    # asteapta ca omul sa termine actul in curs — nu i-l ia din fata.
    vizibil = pg.eval_on_selector(".versiune-noua", "e=>e.getBoundingClientRect().height > 0")
    acoperit = pg.evaluate("""() => {
      const b = document.querySelector('.versiune-noua').getBoundingClientRect();
      const el = document.elementFromPoint(b.left + b.width/2, b.top + b.height/2);
      return !!(el && el.closest('.fereastra-overlay'));
    }""")
    print("3b. cu dialogul deschis -> anunt vizibil: %s · acoperit de fereastra: %s"
          % (vizibil, acoperit))
    assert vizibil, "anuntul nu se mai vede cat timp o fereastra e deschisa"
    assert acoperit, "anuntul e apasabil PESTE o fereastra modala — ar fura actul in curs"

    # ── 4. anuntul are IESIRE: dupa ce omul termina actul, apasat, reincarca ──────────────────
    # LIMITA DECLARATA, masurata aici: anuntul e apasabil doar cand nu e nicio fereastra deschisa.
    # Tot ecranul aplicatiei traieste in ferestre peste desktop, deci in practica omul il apasa
    # cand se intoarce la desktop. *E consecinta directa a lui 3b, si e alegerea sigura: un anunt
    # apasabil peste o fereastra ar putea fi lovit din greseala, iar reincarcarea ar lua chiar
    # formularul pe care decizia il apara.*
    pg.click("#dlg-anuleaza")
    pg.wait_for_timeout(400)
    pg.click(".nav-x")                       # inchide si fereastra cozii -> inapoi la desktop
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(300)
    pg.click(".versiune-noua")
    pg.wait_for_selector(".cab-card", timeout=25000)
    viu2 = pg.evaluate("() => window.__proba_r129 || null")
    print("4. dupa apasarea anuntului -> marcajul de dinainte:", viu2, "(None = s-a reincarcat)")
    assert viu2 is None, "apasarea anuntului n-a reincarcat — anuntul n-are iesire"
    assert not pg.query_selector(".versiune-noua"), "anuntul persista dupa reincarcare"

    # ── mobil: anuntul nu revarsa bara ────────────────────────────────────────────────────────
    mob = b.new_context(viewport={"width": 393, "height": 851}, device_scale_factor=2.75,
                        is_mobile=True, has_touch=True)
    mob.add_init_script(INIT)
    mp = mob.new_page()
    mp.goto(BAZA + "/", wait_until="networkidle")
    mp.wait_for_selector(".cab-card", timeout=25000)
    publica_din_arbore()
    mp.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
    mp.wait_for_selector(".versiune-noua", timeout=20000)
    lat = mp.evaluate("() => document.body.scrollWidth")
    mp.screenshot(path=os.path.join(OUT, "r129_mobil.png"), full_page=True)
    print("MOBIL Pixel5 -> body scrollWidth:", lat)
    assert lat <= 400, "revarsare orizontala pe telefon cu anuntul in bara (body=%s)" % lat

    assert not erori, "erori JS: %r" % erori[:3]

print("PROBA R129 OK: anunta o publicare noua, NU reincarca singur, nu pierde formularul, "
      "si are iesire la apasare.")
