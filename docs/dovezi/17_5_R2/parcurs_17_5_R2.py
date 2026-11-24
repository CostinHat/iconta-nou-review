"""Parcurs oficial al celor zece aserțiuni R, la 1366×768."""
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal)"


def ruleaza(pagina, ctx):
    pg = pagina
    origine = pg.evaluate("location.origin")
    def pas(nume):
        rez, verdict = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere,
                                         ctx.verificator, ctx.pasi_json, ctx.csv)
        print(f"[parcurs] {nume}: {verdict} {rez}")
    def acasa():
        pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
        pg.goto(origine + "/", wait_until="domcontentloaded")
        pg.locator("button.cab-card:has([data-cheie='termene'])").wait_for(state="visible")
    def deschide(cheie):
        acasa()
        grup=pg.locator("button[aria-controls='fgc-sef'][aria-expanded='false']")
        if grup.count(): grup.click()
        pg.locator(f"button.cab-card:has([data-cheie='{cheie}'])").click()
    acasa()
    titlu = pg.locator("button.cab-card:has([data-cheie='control']) .cab-card-titlu")
    titlu.wait_for(state="visible")
    titlu.scroll_into_view_if_needed()
    pas("implicit")
    deschide("asistenti")
    pg.locator(TOP+" #asi-lista").wait_for(state="attached")
    pas("asistenti")
    b=pg.locator(TOP+" button.ajutor-btn[data-ajutor='F006']")
    if b.count()==1 and b.is_visible():
        b.click()
        pg.locator(TOP+" .aj-continut").wait_for(state="visible")
    pas("asistenti_ajutor")
    for cheie, reper in (("termene",".mig-intro"),("capacitate",".cap-ecran, .cap-cifre"),("pachete","#pac-firma")):
        deschide(cheie)
        pg.locator(TOP).locator(reper).first.wait_for(state="attached")
        pas(cheie)
    deschide("activitate")
    pg.locator(TOP+" #opt-tipare").click()
    pg.locator(TOP+" #tip-ai").wait_for(state="attached")
    pas("tipare")
