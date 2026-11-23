from urllib.parse import urlsplit

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc SRL"
def origine_proba(url):
    adresa = urlsplit(url)
    if adresa.scheme != "http" or adresa.hostname not in ("localhost", "127.0.0.1") or adresa.port != 8019:
        raise RuntimeError("Proba cere instanța de test pe loopback, portul 8019")
    return f"{adresa.scheme}://{adresa.netloc}"


def acasa(pg):
    origine = origine_proba(pg.url)
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(origine + "/", wait_until="domcontentloaded")
    origine_proba(pg.url)
    pg.locator("button.cab-card:has([data-cheie='firme'])").wait_for()


def firma(pg, nume, control):
    acasa(pg)
    pg.locator("button.cab-card:has([data-cheie='firme'])").click()
    pg.locator(TOP + "#opt-existente").click()
    lista = pg.locator(TOP + "#firme-lista button.firme-rand")
    lista.filter(has=pg.get_by_text(nume, exact=True)).click()
    tinta = pg.locator(TOP + control)
    tinta.wait_for(state="attached")
    grup = tinta.locator("xpath=ancestor::*[contains(concat(' ',normalize-space(@class),' '),' firme-optiuni ')][1]")
    if grup.count() and not grup.is_visible():
        pg.locator(TOP + f'button[aria-controls="{grup.get_attribute("id")}"]').click()
    tinta.click()
def inchidere(pg):
    pg.set_viewport_size({"width": 1366, "height": 768})
    firma(pg, F1, "#fa-inchidere")
    pg.wait_for_function("""sel => {
        const e = document.querySelector(sel);
        const text = id => e?.querySelector(id)?.textContent.trim() || '';
        return text('#il-stare-perioada').startsWith('Luna ') &&
               text('#il-lock') && text('#il-controale') &&
               /Evidența facturilor (?:e (?:deschisă|închisă)|nu se poate închide)/.test(text('#il-facturi')) &&
               !/Nu s-au putut citi/.test(text('#il-controale'));
    }""", arg=TOP.strip())


def balanta(pg):
    pg.set_viewport_size({"width": 603, "height": 590})
    with pg.expect_response(lambda r: urlsplit(r.url).path.endswith("/balanta") and r.request.method == "GET") as resp:
        firma(pg, F1, "#fa-balanta")
    if not resp.value.ok:
        raise RuntimeError("API Balanță indisponibil")
    pg.locator(TOP + "#b-intro").wait_for()
    rows = resp.value.json()["randuri"]
    if not rows or not rows[0].get("cont") or not rows[0].get("denumire"):
        raise RuntimeError("Lipsește un cont cu denumire în balanța perioadei")
    return {"cont": str(rows[0]["cont"]), "denumire": str(rows[0]["denumire"]), "randuri": len(rows)}


def ruleaza(pagina, ctx):
    import verifica_pas as VP
    for pas, deschide in (("implicit", acasa), ("inchidere", inchidere), ("balanta", balanta)):
        deschide(pagina)
        masuri, stare = VP.verifica_pagina(pagina, ctx.lot, pas, ctx.parcurgere,
                                           ctx.verificator, ctx.pasi_json, ctx.csv)
        print(f"[parcurs] {pas} {stare} {masuri}", flush=True)
        if stare == "neexecutat":
            raise RuntimeError(f"Oracol neexecutat la {pas}")
