from urllib.parse import urlsplit
import verifica_pas as VP


def ruleaza(pg, ctx):
    url = urlsplit(pg.url)
    if (url.scheme, url.hostname, url.port) not in (
        ("http", "localhost", 8019),
        ("http", "127.0.0.1", 8019),
    ):
        raise ValueError("Mediu de probă greșit")
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    top = ".fereastra-overlay:not(.fundal) "
    pg.locator("button.cab-card:has([data-cheie='firme'])").click()
    pg.locator(top + "#opt-existente").click()
    pg.locator(top + "#firme-lista button.firme-rand").filter(
        has=pg.get_by_text("F1 Comert Stoc SRL", exact=True)
    ).click()
    b = pg.locator(top + "#fa-parteneri")
    b.wait_for(state="attached")
    g = b.locator(
        "xpath=ancestor::*[contains(concat(' ',normalize-space(@class),' '),' firme-optiuni ')][1]"
    )
    if g.count() and not g.is_visible():
        pg.locator(
            top + 'button[aria-controls="' + g.get_attribute("id") + '"]'
        ).click()
    b.click()
    pg.locator(top + "#pt-tabel tbody tr").first.wait_for(state="attached")
    pg.evaluate(
        "()=>new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok)))"
    )
    print(
        VP.verifica_pagina(
            pg,
            ctx.lot,
            "parteneri",
            ctx.parcurgere,
            ctx.verificator,
            ctx.pasi_json,
            ctx.csv,
        )
    )
