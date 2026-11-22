"""Probe 17.5-Q3, exclusiv pe copia oficială de test."""
from urllib.parse import urlsplit

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc SRL"
F7 = "F7 Preluare Test SRL"
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


def import_pas(pg, nume, pas, ancora):
    firma(pg, nume, "#fa-import")
    pg.locator(TOP + "#mig-pasi").get_by_text(pas, exact=True).click()
    pg.locator(TOP + ancora).wait_for(state="attached")


def ruleaza(pagina, ctx):
    import verifica_pas as VP
    def verifica(pas):
        masuri, stare = VP.verifica_pagina(pagina, ctx.lot, pas, ctx.parcurgere,
                                           ctx.verificator, ctx.pasi_json, ctx.csv)
        print(f"[parcurs] {pas} {stare} {masuri}", flush=True)
        if stare == "neexecutat":
            raise RuntimeError(f"Oracol neexecutat la {pas}")
    pagina.set_viewport_size({"width":1366, "height":768})
    acasa(pagina)
    verifica("implicit")
    for nume, pas in [(F1, "solduri_f1"), (F7, "solduri_f7")]:
        import_pas(pagina, nume, "Solduri inițiale", "#mig-alege")
        pagina.locator(TOP + "#mig-drop").scroll_into_view_if_needed()
        verifica(pas)
    acasa(pagina)
    pagina.locator("button.cab-card:has([data-cheie='termene'])").click()
    cap = pagina.locator(TOP + "#term-lista thead")
    cap.wait_for()
    cap.scroll_into_view_if_needed()
    verifica("termene")
    for nume, control, ancora in [("stocuri", "#fa-stocuri", "#s-desc"), ("banca", "#fa-banca", "#bk-lucru tbody[data-linie-id]")]:
        firma(pagina, F1, control)
        pagina.locator(TOP + ancora).first.wait_for()
        pagina.locator(TOP + ".fereastra-jos").wait_for()
        pagina.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        verifica(nume)
