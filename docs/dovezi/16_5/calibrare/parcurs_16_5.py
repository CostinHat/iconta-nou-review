# -*- coding: utf-8 -*-
"""Parcursul calibrării 16.5 (măsura „valoare” a oracolului): cabinet › Firme › F1 Comert Stoc › Registru jurnal › luna 11/2026 › Notă nouă. Pașii „inainte” și „inainte_pica” citesc data propusă a notei,
pasul „dupa_fill” citește data după ce contabilul o scrie în câmp. Fereastra se închide cu „Renunță”; nimic nu se salvează. Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas."""
import verifica_pas as VP


def _cabinet(pg):
    """Din cabinet (copiat din parcurs_16_2_C.py): memoria ferestrei deschise se șterge întâi; dacă cabinetul nu răspunde la clic, pagina se reîncarcă, de cel mult trei ori."""
    for incercare in range(3):
        try:
            pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
            pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
            pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
            pg.wait_for_timeout(800)
            pg.click("button.cab-card:has([data-cheie='firme'])", timeout=10000)
            break
        except Exception:   # noqa: BLE001 — se reia de la începutul cabinetului
            if incercare == 2:
                raise
            pg.reload(wait_until="domcontentloaded")
    pg.wait_for_timeout(600)
    if pg.query_selector("#opt-existente"):
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)


def _nota_noua(pg):
    _cabinet(pg)
    pg.locator("#firme-lista button.firme-rand", has_text="F1 Comert Stoc").first.click()
    pg.wait_for_selector("#fa-jurnal", timeout=20000)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-data", timeout=20000)


def ruleaza(pagina, ctx):
    _nota_noua(pagina)
    for pas in ("inainte", "inainte_pica"):
        rez, v = VP.verifica_pagina(pagina, ctx.lot, pas, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (pas, v, rez))
    pagina.fill("#je-data", "2026-10-15")
    pagina.dispatch_event("#je-data", "change")
    rez, v = VP.verifica_pagina(pagina, ctx.lot, "dupa_fill", ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
    print("[parcurs] pasul dupa_fill: %s %s" % (v, rez))
    pagina.click("#je-renunta")
