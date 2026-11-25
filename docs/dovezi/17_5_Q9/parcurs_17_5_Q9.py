import verifica_pas as VP

def ruleaza(pg,ctx):
    def pas(nume):
        print(VP.verifica_pagina(pg,ctx.lot,nume,ctx.parcurgere,ctx.verificator,ctx.pasi_json,ctx.csv))
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin")+"/",wait_until="domcontentloaded")
    card=pg.locator("button.cab-card:has([data-cheie='validat'])")
    card.wait_for(state="attached")
    if not card.is_visible():
        grupa=card.locator("xpath=ancestor::*[@id][@hidden]").last
        if grupa.count():
            pg.locator('button[aria-controls="'+grupa.get_attribute("id")+'"]').click()
    titlu = card.locator(".cab-card-titlu")
    titlu.wait_for(state="visible")
    titlu.evaluate("n => n.scrollIntoView({block:'center', inline:'nearest', behavior:'instant'})")
    pas("implicit");card.click()
    randuri = pg.locator(".fereastra-overlay:not(.fundal) #val-ciorne tbody.tn-nota")
    randuri.first.wait_for(state="visible")
    validare = randuri.get_by_role("button", name="Validează", exact=True).first
    if validare.count():
        validare.scroll_into_view_if_needed()
    pas("ciorne")
