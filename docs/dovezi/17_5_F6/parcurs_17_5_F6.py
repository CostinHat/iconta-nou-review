from urllib.parse import urlsplit
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1, F2 = "F1 Comert Stoc SRL", "F2 Profit Amortizare SRL"
# B4 (D8): propunerea pe F2 se cere la 10.000 lei, în profitul reportat existent pe copie (117: 14.600 lei); T1 rămâne a REAL
B4_FORMULAR = (("data", "2026-03-15"), ("brut", "10000"), ("numar_hotarare", "1"), ("data_hotarare", "2026-03-15"))


def _asaza(pg):
    pg.evaluate("()=>new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok)))")


def _firma(pg, nume, control):
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.locator("button.cab-card:has([data-cheie='firme'])").click()
    pg.locator(TOP + "#opt-existente").click()
    pg.locator(TOP + "#firme-lista button.firme-rand").filter(has=pg.get_by_text(nume, exact=True)).click()
    if control is None:
        pg.locator(TOP + "#fg-contabilitate").wait_for(state="attached")
        return
    b = pg.locator(TOP + control)
    b.wait_for(state="attached")
    g = b.locator("xpath=ancestor::*[contains(concat(' ',normalize-space(@class),' '),' firme-optiuni ')][1]")
    if g.count() and not g.is_visible():
        pg.locator(TOP + 'button[aria-controls="' + g.get_attribute("id") + '"]').click()
    b.click()


def _verifica(pg, ctx, pas):
    _asaza(pg)
    print(VP.verifica_pagina(pg, ctx.lot, pas, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv))


def ruleaza(pg, ctx):
    url = urlsplit(pg.url)
    if (url.scheme, url.hostname, url.port) not in (("http", "localhost", 8019), ("http", "127.0.0.1", 8019)):
        raise ValueError("Mediu de probă greșit")
    _firma(pg, F2, "#fa-operatiuni")
    pg.locator(TOP + 'button[data-op="asociati"]').click()
    pg.locator(TOP + "#op-operatie").wait_for(state="attached")
    pg.locator(TOP + "#op-operatie").select_option("dividend")
    for camp, val in B4_FORMULAR:
        loc = pg.locator(TOP + "#op-" + camp)
        loc.fill(val)
        loc.dispatch_event("change")
    pg.locator(TOP + "#op-interimar").select_option("0")
    pg.locator(TOP + "#op-div-tabel tbody tr").first.wait_for(state="visible", timeout=30000)
    # completarea derulează corpul ferestrei; titlul operației (f.1) se aduce înapoi în fereastră, fără alt efect asupra formularului
    pg.evaluate("() => { const h = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra h2.pf-titlu'); if (h) h.scrollIntoView({block: 'start'}); }")
    _verifica(pg, ctx, "decontari")
    _firma(pg, F2, None)
    _verifica(pg, ctx, "meniu")
    _firma(pg, F2, "#fa-banca")
    pg.locator(TOP + "#bk-rezumat h2.pf-titlu").wait_for(state="visible")
    _verifica(pg, ctx, "banca")
    _firma(pg, F1, "#fa-control")
    pg.locator(TOP + "#cf-luna-comparata").wait_for(state="attached", timeout=60000)
    _verifica(pg, ctx, "control")
