# -*- coding: utf-8 -*-
"""«Date firma» — campul de denumire din portofoliu, cu denumirea de la ANAF alaturi.

Se probeaza pe firma pe care a adaugat-o Costin (`Antibiotice Iasi`, CUI 1973096) — PRIMA firma
reala cu `nume_anaf`. Deci divergenta nu mai e fabricata.

NU SCRIE NIMIC: toate cererile de scriere catre `/tenants/**` sunt interceptate si li se raspunde
fara sa ajunga la server. Sonda apasa pana la marginea actului, nu peste ea — lectia din
`sonda-de-audit-nu-e-read-only`.
Ruleaza PE SERVER, din ~/iconta_nou/frontend_test/."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from w_auth import *  # noqa

TINTA = "Antibiotice Iasi"
ANAF = "ANTIBIOTICE SA"
scrieri = []


def opreste_scrierile(pg):
    def h(route):
        m = route.request.method
        if m in ("POST", "PUT", "PATCH", "DELETE"):
            scrieri.append((m, route.request.url, route.request.post_data or ""))
            return route.fulfill(status=200, content_type="application/json",
                                 body=json.dumps({"ok": True}))
        return route.fallback()
    pg.route("**/tenants/**", h)
    pg.route("**/tenants", h)


VALORI = {"df-reg_com": "J22/1234/1991", "df-caen": "2120", "df-adresa": "Str. Valea Lupului 1",
          "df-oras": "Iasi", "df-judet": "Iasi", "df-cod_postal": "707410",
          "df-banca": "BCR", "df-iban": "RO49AAAA1B31007593840000", "df-telefon": "0232209000",
          "df-declarant_nume": "Popescu", "df-declarant_prenume": "Ion",
          "df-declarant_functie": "Administrator"}


def completeaza_obligatoriile(pg):
    """Firma e nou-nouta, deci campurile obligatorii sunt goale si validarea din ecran opreste
    salvarea INAINTE de orice cerere. Fara pasul asta, «0 PUT-uri» ar fi verde din motivul
    gresit — exact forma de verde fals din care s-a invatat de mai multe ori aici."""
    for cid, val in VALORI.items():
        el = pg.locator("#" + cid)
        if el.count() and not (el.input_value() or "").strip():
            el.fill(val)
    for sid, val in [("vf-regim_fiscal", "profit"), ("vf-platitor_tva", "da"),
                     ("vf-operatiuni_ic", "nu"), ("vf-tip_decont", "lunar")]:
        s = pg.locator("#" + sid)
        if s.count():
            try:
                s.select_option(val)
            except Exception:
                pass
    t = pg.locator("#vf-tva_data_inceput")
    if t.count() and t.is_visible() and not (t.input_value() or "").strip():
        t.fill("2020-01-01")


def deschide(pg, nume):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(400)
    pg.locator("button.firme-rand", has_text=nume).first.click(timeout=8000)
    pg.wait_for_selector("#fa-datefirma", timeout=12000); pg.wait_for_timeout(600)


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1000}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    opreste_scrierile(pg)

    # ── 0. pe fisa firmei, divergenta se vede FARA nicio fabricatie ─────────
    deschide(pg, TINTA)
    caseta = pg.locator(".caseta-atentie").first
    print("fisa firmei: caseta de alegere = %s" % ("prezenta" if caseta.count() else "LIPSA"))
    assert caseta.count(), "prima firma reala cu nume_anaf, si ecranul nu cere alegerea"
    but = caseta.locator("button")
    etichete = [but.nth(i).inner_text().strip() for i in range(but.count())]
    print("   butoane: %s" % etichete)
    assert len(etichete) == 2
    for i in range(2):
        assert "buton-primar" not in (but.nth(i).get_attribute("class") or ""), "unul e implicit"
    assert ANAF in caseta.inner_text(), "nu se arata ce spune ANAF"

    # ── 1. in «Date firma», doua campuri, numite DIFERIT ────────────────────
    pg.locator("#fa-datefirma").click()
    pg.wait_for_selector("#df-nume-portofoliu", timeout=12000); pg.wait_for_timeout(600)
    portofoliu, fiscal = pg.locator("#df-nume-portofoliu"), pg.locator("#df-nume")
    print("portofoliu=%r · fiscal=%r" % (portofoliu.input_value(), fiscal.input_value()))
    et = [pg.locator("label:has(#df-nume-portofoliu) .camp-eticheta").inner_text().strip(),
          pg.locator("label:has(#df-nume) .camp-eticheta").inner_text().strip()]
    print("etichete: %s" % et)
    assert et[0] != et[1], "doua campuri cu aceeasi eticheta — omul n-ar sti pe care o editeaza"

    # ── 2. denumirea de la ANAF apare LANGA camp, cu data citirii ───────────
    ajutor = pg.locator("label:has(#df-nume-portofoliu) .camp-ajutor").inner_text()
    print("sub camp: %r" % " ".join(ajutor.split())[:150])
    assert ANAF in ajutor, "nu se arata ce spune ANAF langa campul care se editeaza"
    assert "2026-08-27" in ajutor, "nu se spune CAND s-a citit"

    # ── 3. denumirea goala se refuza in ecran, fara drum la server ──────────
    scrieri.clear()
    portofoliu.fill("")
    pg.locator("#df-salveaza").click(); pg.wait_for_timeout(800)
    print("salvare cu denumire goala -> scrieri catre server: %d" % len(scrieri))
    assert not scrieri, "s-a trimis o denumire goala"

    # ── 4. denumire NESCHIMBATA -> niciun PUT (n-ar fi o alegere) ───────────
    deschide(pg, TINTA); pg.locator("#fa-datefirma").click()
    pg.wait_for_selector("#df-nume-portofoliu", timeout=12000); pg.wait_for_timeout(500)
    completeaza_obligatoriile(pg)
    scrieri.clear()
    pg.locator("#df-salveaza").click(); pg.wait_for_timeout(2000)
    puturi = [s for s in scrieri if s[0] == "PUT"]
    altele = [s for s in scrieri if s[0] != "PUT"]
    print("salvare fara sa ating denumirea -> PUT: %d · alte scrieri: %d" % (len(puturi), len(altele)))
    assert altele, ("[anti-vacuu] salvarea n-a plecat deloc — validarea a oprit-o, deci «0 PUT» "
                    "ar fi verde din motivul gresit")
    assert not puturi, ("s-a trimis un PUT desi denumirea n-a fost atinsa — fiecare salvare ar "
                        "consemna o «alegere» pe care nimeni n-a facut-o")

    # ── 5. denumire SCHIMBATA -> exact un PUT, cu ce trebuie ────────────────
    deschide(pg, TINTA); pg.locator("#fa-datefirma").click()
    pg.wait_for_selector("#df-nume-portofoliu", timeout=12000); pg.wait_for_timeout(500)
    completeaza_obligatoriile(pg)
    scrieri.clear()
    pg.locator("#df-nume-portofoliu").fill(ANAF)
    pg.locator("#df-salveaza").click(); pg.wait_for_timeout(2000)
    puturi = [s for s in scrieri if s[0] == "PUT"]
    print("dupa ce schimb denumirea -> PUT: %d · continut: %s"
          % (len(puturi), puturi[0][2] if puturi else "-"))
    assert len(puturi) == 1 and json.loads(puturi[0][2]).get("nume") == ANAF

    pg.screenshot(path=os.path.join(OUT, "r81_date_firma.png"), full_page=True)
    print()
    print("scrieri ajunse la server: 0 (toate interceptate) — firma lui Costin e neatinsa")
    print("erori de pagina: %s" % (erori or "niciuna"))
    assert not erori, erori
    b.close()
print("Date firma / denumire: VERDE")
