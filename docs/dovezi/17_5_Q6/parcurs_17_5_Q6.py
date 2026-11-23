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

def ruleaza(pagina, ctx):
    import verifica_pas as VP
    for pas, latime, inaltime in (("implicit",1366,768),("declaratii",1366,768),("ingust",603,590)):
        pagina.set_viewport_size({"width":latime,"height":inaltime})
        if pas=="implicit":
            acasa(pagina)
        else:
            firma(pagina,F1,"#fa-declaratii")
            pagina.locator(TOP+"#dec-tip + .ds-lista [role=option]").filter(has_text="D300 · 10/2026").first.wait_for(state="attached")
        masuri, stare = VP.verifica_pagina(pagina,ctx.lot,pas,ctx.parcurgere,ctx.verificator,ctx.pasi_json,ctx.csv)
        print(f"[parcurs] {pas} {stare} {masuri}",flush=True)
        if stare=="neexecutat":raise RuntimeError(pas)
