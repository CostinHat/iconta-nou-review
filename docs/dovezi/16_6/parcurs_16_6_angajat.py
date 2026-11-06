# -*- coding: utf-8 -*-
"""Parcursul lotului 16.6 (poziția F054, editorul de note contabile), cu contul unui angajat fără dreptul de validare (dovada.71508): cabinet › Firme › F1 Comert Stoc › Registru jurnal ›
luna 11/2026 › Notă nouă (data propusă, formularul complet), salvarea notei (628 = 5121, 25,00) și detaliul notei salvate, care așteaptă validarea în cabinet. Salvează o notă: baza se
restaurează înaintea fiecărei parcurgeri. După fiecare pas predă pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas."""
import verifica_pas as VP

ULTIMA_NOTA = "tbody.tn-nota:last-of-type"


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


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    _cabinet(pg)
    pg.locator("#firme-lista button.firme-rand", has_text="F1 Comert Stoc").first.click()
    pg.wait_for_selector(".fereastra-overlay:not(.fundal) .firme-grup-btn", timeout=20000)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_selector("#fa-jurnal", timeout=20000)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-data", timeout=20000)
    pas("u")
    pg.fill("#je-desc", "F054 nota de proba")
    pg.fill("#je-doc", "Chitanță de probă din 03.11.2026")
    pg.fill("#je-linii > div:nth-child(1) .je-deb", "628")
    pg.fill("#je-linii > div:nth-child(1) .je-cre", "5121")
    pg.fill("#je-linii > div:nth-child(1) .je-sum", "25.00")
    pas("v")
    pg.click("#je-salveaza")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    pg.wait_for_function("() => ((document.querySelector('#j-mesaj') || {}).innerText || '').startsWith('Ai salvat')", timeout=20000)
    pas("w")
    pg.click(ULTIMA_NOTA + " .tn-deschide")
    pas("x")
