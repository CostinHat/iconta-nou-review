# -*- coding: utf-8 -*-
"""Parcursul de probă al comenzii 16.3 (scenariul F017, Casă › Dispoziție nouă, pe F1 Comert Stoc SRL): acțiunile pașilor a, b, c, p, q, executate ca un contabil, apoi pagina vie se predă oracolului
(verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai playwright, biblioteca standard și verifica_pas (regula lansatorului).
PARCURS_PASI=a,b,... (variabilă de mediu) alege pașii rulați; implicit toți, în ordinea a, b, c, p, q."""
import os

import verifica_pas as VP

PASI = ("a", "b", "c", "p", "q")


def _firma_casa(pg):
    """Din cabinet: Firme › F1 Comert Stoc › Casă (luna curentă a ceasului fix, 11/2026). Dacă cabinetul nu răspunde la clic (după o filă deschisă de PDF), pagina se reîncarcă și pasul se reia, de cel mult trei ori."""
    for incercare in range(3):
        try:
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
    pg.locator("#firme-lista button.firme-rand", has_text="F1 Comert Stoc").first.click()
    pg.wait_for_selector("#fa-casa", timeout=20000)
    pg.click("#fa-casa")
    pg.wait_for_selector("#c-sold-inceput", timeout=20000)


def _pas_a(pg, ctx):
    _firma_casa(pg)


def _pas_b(pg, ctx):
    pg.click("#c-toggle")
    pg.wait_for_selector("#c-adauga", timeout=20000)


def _pas_c(pg, ctx):
    pg.select_option("#c-cat", "incasare_client", force=True)
    pg.fill("#c-cui", "410001005")
    pg.dispatch_event("#c-cui", "change")
    pg.wait_for_timeout(2000)


def _pas_p(pg, ctx):
    """Chitanța CHF1 nr. 1 (octombrie): luna precedentă în Casă, rândul ei, apoi clic pe „PDF chitanță”; PDF-ul descărcat prin clic se salvează în directorul parcurgerii."""
    _firma_casa(pg)
    pg.click("#c-prev")
    pg.wait_for_selector("tbody.tn-nota:has-text('CHF1-1')", timeout=20000)
    pg.locator("tbody.tn-nota:has-text('CHF1-1') .tn-deschide").first.click()
    os.makedirs(ctx.director, exist_ok=True)
    with pg.expect_download(timeout=30000) as primit:
        pg.locator("button[data-chpdf='15']").first.click()
    primit.value.save_as(os.path.join(ctx.director, "chitanta_CHF1_1.pdf"))
    for alta in pg.context.pages[1:]:   # fila goală deschisă de aplicație pentru PDF (în browserul fără ecran PDF-ul se descarcă)
        alta.close()


def _pas_q(pg, ctx):
    """Dispoziție nouă › Depunere la bancă, 1,00 lei › Adaugă; Casa se redesenează cu rândul nou."""
    _firma_casa(pg)
    pg.click("#c-toggle")
    pg.wait_for_selector("#c-adauga", timeout=20000)
    pg.select_option("#c-cat", "depunere_banca", force=True)
    pg.fill("#c-suma", "1.00")
    pg.dispatch_event("#c-suma", "change")
    pg.wait_for_timeout(800)
    pg.click("#c-adauga")
    pg.wait_for_selector("#c-confirmare, #c-tabel", timeout=20000)
    pg.wait_for_timeout(800)


ACTIUNI = {"a": _pas_a, "b": _pas_b, "c": _pas_c, "p": _pas_p, "q": _pas_q}


def ruleaza(pagina, ctx):
    for pas in [p for p in os.environ.get("PARCURS_PASI", ",".join(PASI)).split(",") if p in ACTIUNI]:
        try:
            ACTIUNI[pas](pagina, ctx)
        except Exception as e:   # noqa: BLE001 — o acțiune care nu s-a putut face nu oprește parcursul: pagina vie, așa cum a rămas, merge oracolului
            print("[parcurs] pasul %s: acțiune neterminată (%s: %s)" % (pas, type(e).__name__, str(e)[:200]))
        rez, v = VP.verifica_pagina(pagina, ctx.lot, pas, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (pas, v, rez))
