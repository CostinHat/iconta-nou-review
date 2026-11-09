# -*- coding: utf-8 -*-
"""Parcursul lotului 16.6 (poziția F054, editorul de note contabile), cu contul administratorului: cabinet › Firme › F1 Comert Stoc › Registru jurnal › luna 11/2026 (căutare,
filtre, nota 207), Notă nouă în 11/2026 și în 10/2026 (completarea formularului pas cu pas), apoi luna 08/2026 (nota validată 203). Nu salvează nimic: fereastra se închide cu „Renunță”.
După fiecare pas predă pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas."""
import re

import verifica_pas as VP

NOTA_207 = 'tbody.tn-nota[data-nota-id="207"]'
NOTA_203 = 'tbody.tn-nota[data-nota-id="203"]'


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


def _jurnal(pg, luni_inapoi=0):
    """Registrul jurnal al lui F1, pornit mereu de la cabinet; ajunge la 11/2026 − `luni_inapoi` din luna afișată (`_la_luna`)."""
    _cabinet(pg)
    pg.locator("#firme-lista button.firme-rand", has_text="F1 Comert Stoc").first.click()
    pg.wait_for_selector(".fereastra-overlay:not(.fundal) .firme-grup-btn", timeout=20000)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_selector("#fa-jurnal", timeout=20000)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    _la_luna(pg, 2026, 11 - luni_inapoi)


_JS_LUNA = ("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
            "const m = f && f.innerText.match(/Luna (\\d{2})\\/(\\d{4})/); return m ? [+m[2], +m[1]] : null; }")


def _la_luna(pg, an, luna):
    """Din luna AFIȘATĂ a registrului (se deschide pe luna de lucru, nu pe luna de azi) până la `luna/an`: „← luna” sau „luna →”, fiecare așteptând răspunsul lunii cerute."""
    pg.wait_for_function(_JS_LUNA, timeout=20000)
    cur = pg.evaluate(_JS_LUNA)
    cur = cur[0] * 12 + cur[1] - 1
    tinta = an * 12 + luna - 1
    for _ in range(24):
        if cur == tinta:
            break
        inapoi = cur > tinta
        cur += -1 if inapoi else 1
        rg = re.compile(r"/jurnal\?[^ ]*luna=%d(&|$)" % (cur % 12 + 1))
        with pg.expect_response(lambda r: bool(rg.search(r.url)), timeout=20000):
            pg.click("#j-prev" if inapoi else "#j-next")
        pg.wait_for_selector("#j-nota-noua", timeout=20000)
        pg.wait_for_timeout(500)


def _nota_noua(pg):
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-data", timeout=20000)


def _linie(pg, n, debit, credit, suma, partener=None):
    rand = "#je-linii > div:nth-child(%d)" % n
    pg.fill(rand + " .je-deb", debit)
    pg.fill(rand + " .je-cre", credit)
    pg.fill(rand + " .je-sum", suma)
    if partener:
        pg.fill(rand + " .je-pnume", partener)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    _jurnal(pg)
    pas("a")
    pg.fill("#jn-cauta", "7588")
    pas("b")
    pg.fill("#jn-cauta", "NIR nr 7")
    pas("c")
    pg.fill("#jn-cauta", "")
    pg.select_option("#jn-stare", "fara_doc")
    pas("d")
    pg.select_option("#jn-stare", "validata")
    pas("e")
    pg.select_option("#jn-stare", "")
    pg.click(NOTA_207 + " .tn-deschide")
    pas("f")
    pg.click(NOTA_207 + " [data-val]", force=True)   # butonul e inactiv (aria-disabled): clicul se oprește în api.js, nu pleacă nicio cerere
    pas("g")
    _nota_noua(pg)
    pas("h")
    pg.click("#je-salveaza", force=True)
    pas("i")
    pg.click(".fereastra:last-of-type .nav-inapoi")   # [17.3-B] „←” din antet = vechiul „Renunță” (revine la lista jurnalului)
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    _jurnal(pg, 1)
    _nota_noua(pg)
    pas("j")
    pg.click("#je-plus")
    pas("k")
    pg.click("#je-linii > div:nth-child(2) .je-scoate")
    pas("l")
    pg.fill("#je-data", "2026-10-15")
    pg.dispatch_event("#je-data", "change")
    pas("m")
    _linie(pg, 1, "4111", "707", "25.00")
    pas("n")
    pg.fill("#je-linii > div:nth-child(1) .je-pnume", "Client Test SRL")
    pas("o")
    pg.click("#je-plus")
    pas("p")
    _linie(pg, 2, "4111", "707", "25.00")
    pas("q")
    pg.click("#je-linii > div:nth-child(2) .je-scoate")
    pas("r")
    pg.fill("#je-data", "")
    pg.dispatch_event("#je-data", "change")
    pas("s")
    pg.click(".fereastra:last-of-type .nav-inapoi")   # [17.3-B] „←” din antet = vechiul „Renunță”
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    _jurnal(pg, 3)
    pg.click(NOTA_203 + " .tn-deschide")
    pas("t")
