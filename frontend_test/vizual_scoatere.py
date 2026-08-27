# -*- coding: utf-8 -*-
"""R78: butonul de scoatere e PE RAND, in lista, si se vede fara derulare.
Masoara, nu presupune: pozitia in pixeli, fereastra, si ce se intampla la fiecare din cele doua
apasari. Ruleaza PE SERVER, din ~/iconta_nou/frontend_test/."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from w_auth import *  # noqa

VP = {"width": 1200, "height": 793}   # aceeasi fereastra pe care s-a masurat 1361 px la R78


def lista(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(400)


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport=VP); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.on("console", lambda m: erori.append("console." + m.type + ": " + m.text)
          if m.type == "error" else None)

    # ── 1. randul e (iar) buton, si are actiunea LANGA el ───────────────────
    lista(pg)
    n_rand = pg.locator("button.firme-rand").count()
    n_linie = pg.locator(".firme-rand-linie").count()
    n_scoate = pg.locator("button.firme-rand-scoate").count()
    print("randuri button.firme-rand = %d | invelisuri = %d | butoane Scoate = %d"
          % (n_rand, n_linie, n_scoate))
    assert n_rand == n_linie == n_scoate and n_rand > 0, "cate un Scoate pe fiecare rand — nu"

    # ── 2. se vede FARA derulare? (asta era defectul masurat: 1361 px in 793) ──
    prim = pg.locator("button.firme-rand-scoate").first
    caseta = prim.bounding_box()
    print("primul Scoate: y=%.0f px, fereastra=%d px -> %s"
          % (caseta["y"], VP["height"], "SE VEDE" if caseta["y"] < VP["height"] else "SUB PLIU"))
    assert caseta["y"] < VP["height"], "butonul e iar sub pliu"
    assert prim.is_visible()
    # tinta de atingere (a11y): minim 32 px
    print("inaltime tinta = %.0f px" % caseta["height"])
    assert caseta["height"] >= 32, "tinta de atingere sub 32 px"

    # ── 3. apasarea pe RAND deschide FIRMA (nu scoaterea) ───────────────────
    pg.locator("button.firme-rand").first.click()
    pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000)
    print("apasare pe rand -> s-a deschis firma: DA")

    # ── 4. apasarea pe SCOATE deschide PREVIZUALIZAREA, si NU sterge ────────
    lista(pg)
    nume = pg.locator("button.firme-rand .firme-rand-nume").first.inner_text().strip()
    pg.locator("button.firme-rand-scoate").first.click()
    pg.wait_for_timeout(1500)
    corp = pg.inner_text("body")
    print("apasare pe Scoate -> ecranul arata:\n----\n%s\n----" % corp[:800])
    for cerut in ("Scoate", nume.split()[0]):
        assert cerut.lower() in corp.lower(), "previzualizarea nu pomeneste %r" % cerut
    # Ecranul are DOUA fete, dupa ce arata evidenta. Amandoua trebuie probate — altfel „merge"
    # inseamna doar „merge pe firma care s-a nimerit prima".
    # Clasific pe STRUCTURA ecranului deschis, nu pe textul din <body>: ecranele anterioare raman
    # in DOM sub cel curent, iar `inner_text(\"body\")` le aduna pe toate — prima versiune a
    # acestei sonde a citit textul unui ecran vechi si a raspuns despre o lume pe care n-o vedea.
    def fata(pg):
        ecran = pg.locator("#sf-corp").last
        camp = ecran.locator("#sf-cui")
        sterge = ecran.locator("#sf-sterge")
        dezactiv = ecran.locator("#sf-dezactiveaza, #sf-dezactiveaza-2")
        if sterge.count() == 0:
            assert camp.count() == 0, ("firma are evidenta, dar ecranul cere totusi CUI-ul — "
                                       "adica ofera un act pe care nu-l poate duce la capat")
            assert dezactiv.count() >= 1, "nu se ofera nici macar dezactivarea"
            return "CU EVIDENTA -> doar dezactivare, fara camp de CUI"
        assert camp.count() == 1 and camp.input_value() == "", \
            "firma fara evidenta, dar confirmarea pe CUI lipseste sau vine precompletata"
        assert sterge.is_disabled(), "butonul ireversibil e deschis inainte de confirmare"
        assert dezactiv.count() >= 1, "nu se ofera si calea reversibila, alaturi de cea definitiva"
        return "FARA EVIDENTA -> camp de CUI gol, butonul ireversibil blocat, dezactivarea alaturi"

    print("  fata 1: %s" % fata(pg))

    # a doua fata: caut, prin cele doua rute de previzualizare, o firma din cealalta clasa
    import json as _j
    vazute = set()
    lista(pg)
    cate = pg.locator("button.firme-rand-scoate").count()
    print("  caut a doua fata printre %d firme" % cate)
    for i in range(cate):
        lista(pg)
        pg.locator("button.firme-rand-scoate").nth(i).click()
        pg.wait_for_timeout(900)
        f = "evidenta" if pg.locator("#sf-corp").last.locator("#sf-sterge").count() == 0 else "curata"
        vazute.add(f)
        if len(vazute) == 2:
            print("  fata 2: %s" % fata(pg))
            break
    print("clase de firme intalnite in date: %s" % _j.dumps(sorted(vazute)))

    if "curata" not in vazute:
        # Nicio firma fara evidenta nu exista in portofoliu (cele doua PROBA PORTAL au fost
        # sterse). Deci fata a doua NU se poate proba pe date reale. O probez pe un raspuns
        # FABRICAT, prin interceptarea rutei — si scriu limpede ce dovedeste asta si ce nu:
        # dovedeste ca ECRANUL randeaza corect poarta pe CUI; nu dovedeste nimic despre ce
        # raspunde serverul pentru o firma curata.
        print("  [fata 2 nu exista in date] o probez pe raspuns fabricat, prin interceptare")
        gol = {"nume": "PROBA FABRICATA SRL", "cui": "12345678", "se_poate_sterge": True,
               "randuri_de_sters": {"audit_log": 3}, "clienti_de_dezactivat": [],
               "urme_de_pastrat": {}}
        pg.route("**/tenants/*/scoatere", lambda r: r.fulfill(
            status=200, content_type="application/json", body=_j.dumps(gol)))
        lista(pg)
        pg.locator("button.firme-rand-scoate").first.click()
        pg.wait_for_timeout(900)
        print("  fata 2 (fabricata): %s" % fata(pg))
        # poarta pe CUI: un CUI GRESIT nu deschide butonul, cel corect il deschide.
        # NU se apasa — firma de sub interceptare e reala; se probeaza doar poarta.
        ec = pg.locator("#sf-corp").last
        camp, btn = ec.locator("#sf-cui"), ec.locator("#sf-sterge")
        camp.fill("99999999"); pg.wait_for_timeout(120)
        gresit = btn.is_disabled()
        camp.fill("12345678"); pg.wait_for_timeout(120)
        corect = btn.is_disabled()
        print("  poarta pe CUI: gresit -> blocat=%s | corect -> blocat=%s" % (gresit, corect))
        assert gresit and not corect, "poarta pe CUI nu discrimineaza"
        pg.screenshot(path=os.path.join(OUT, "r78_fara_evidenta.png"), full_page=True)
        pg.unroute("**/tenants/*/scoatere")

    pg.screenshot(path=os.path.join(OUT, "r78_scoatere.png"), full_page=True)
    lista(pg)
    pg.screenshot(path=os.path.join(OUT, "r78_lista.png"), full_page=False)

    print("erori de pagina: %s" % (erori or "niciuna"))
    assert not erori, erori
    b.close()
print("R78: VERDE")
