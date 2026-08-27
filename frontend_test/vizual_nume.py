# -*- coding: utf-8 -*-
"""R77 pe ecran: doua butoane, niciunul implicit; amandoua SCRIU.
Nicio firma reala n-are `nume_anaf` (0 din 17), deci divergenta nu se vede nicaieri in aplicatie.
O fabric la nivel de RASPUNS, prin interceptarea listei — asta probeaza ce randeaza ECRANUL si ce
trimite la apasare. Partea de server e probata separat, pe date reale, in `proba_r77.py`.
Ruleaza PE SERVER, din ~/iconta_nou/frontend_test/."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from w_auth import *  # noqa

ANAF = "PANIFICATIE SALARII SPECIALE S.R.L."
trimis = []


def cu_divergenta(pg, nume_ales_la=None, nume_anaf_la="2026-08-27T10:00:00+03:00"):
    """Intercepteaza lista si pune `nume_anaf` pe prima firma.

    Se SCOATE intai interceptorul precedent: doua handlere pe acelasi tipar se calca unul pe
    altul, iar sonda pica intermitent — nu pentru ca ecranul ar fi rupt, ci pentru ca sonda e.
    """
    pg.unroute("**/tenants?inactive=true")

    def h(route):
        try:
            r = route.fetch()
            d = r.json()
            t = d["tenants"][0]
        except Exception as e:                      # raspuns care nu e lista de firme
            print("  [interceptor] las sa treaca neatins: %s" % e)
            return route.fallback()
        t["nume_anaf"] = ANAF
        t["nume_anaf_la"] = nume_anaf_la
        t["nume_ales_la"] = nume_ales_la
        route.fulfill(status=r.status, body=json.dumps(d), content_type="application/json")
    pg.route("**/tenants?inactive=true", h)


def deschide_prima(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(400)
    pg.locator("button.firme-rand").first.click()
    pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000); pg.wait_for_timeout(600)


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 900}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.route("**/tenants/*/nume-ales", lambda r: (
        trimis.append(json.loads(r.request.post_data or "{}")),
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"alege": "?", "nume": "?"}))))

    # ── 1. divergenta neraspunsa -> AMANDOUA butoanele, niciunul implicit ────
    cu_divergenta(pg)
    deschide_prima(pg)
    caseta = pg.locator(".caseta-atentie").first
    assert caseta.count(), "divergenta nu se arata deloc"
    but = caseta.locator("button")
    etichete = [but.nth(i).inner_text().strip() for i in range(but.count())]
    print("butoane in caseta: %s" % etichete)
    assert len(etichete) == 2, "nu sunt DOUA cai — deci nu e o alegere"
    for i in range(2):
        assert not but.nth(i).is_disabled(), "un buton vine deja blocat — adica preales"
        assert "buton-primar" not in (but.nth(i).get_attribute("class") or ""), (
            "unul din butoane e desenat ca implicit — alegerea vine cu un raspuns sugerat")
    assert pg.locator("input[type=radio][checked], input[type=checkbox][checked]").count() == 0

    # ── 2. ramura „pastrez denumirea mea" TRIMITE ceva ──────────────────────
    caseta.locator("#dn-pastrez").click(); pg.wait_for_timeout(700)
    print("la «Păstrez denumirea mea» s-a trimis: %s" % trimis)
    assert trimis and trimis[-1].get("alege") == "aplicatie", (
        "«a păstra pe a ta» n-a trimis nimic — deci a rămas «a nu face nimic»")

    # ── 3. ramura ANAF trimite cealalta alegere ─────────────────────────────
    trimis.clear()
    cu_divergenta(pg); deschide_prima(pg)
    pg.locator(".caseta-atentie #dn-ia-anaf").first.click(); pg.wait_for_timeout(700)
    print("la «Ia denumirea de la ANAF» s-a trimis: %s" % trimis)
    assert trimis and trimis[-1].get("alege") == "anaf"

    # ── 4. daca s-a raspuns deja, intrebarea NU se mai pune ─────────────────
    pg.unroute("**/tenants?inactive=true")
    cu_divergenta(pg, nume_ales_la="2026-08-27T12:00:00+03:00")
    deschide_prima(pg)
    n = pg.locator(".caseta-atentie").count()
    print("dupa un raspuns (alegere 12:00 > citire 10:00): casete de atentie = %d" % n)
    assert n == 0, "intrebarea se pune la infinit, desi a primit raspuns"

    # ── 5. o citire ANAF mai NOUA decat alegerea o REDESCHIDE ───────────────
    pg.unroute("**/tenants?inactive=true")
    cu_divergenta(pg, nume_ales_la="2026-08-27T08:00:00+03:00")
    deschide_prima(pg)
    n = pg.locator(".caseta-atentie").count()
    print("citire 10:00 > alegere 08:00: casete de atentie = %d" % n)
    assert n >= 1, ("o denumire schimbata la registru DUPA alegere nu mai intreaba nimic — "
                    "alegerea de ieri a stins o intrebare de azi")
    pg.screenshot(path=os.path.join(OUT, "r77_alegere.png"), full_page=True)

    print("erori de pagina: %s" % (erori or "niciuna"))
    assert not erori, erori
    b.close()
print("R77 ecran: VERDE")
