# -*- coding: utf-8 -*-
"""Parcursul lotului 16.8 (poziția X05, navigarea ferestrelor), cu contul administratorului (dovada.71507), 1366×768: fereastra firmei F1 (prima fereastră), Registru jurnal, Emite factură,
Stat de plată F5, Plan de conturi, Model factură, editorul de notă cu Salvează inactiv, fereastra mică de stornare, Declarația D104 pasul 2 (și cu secțiunile pliate), pagina principală (ieșirea din cont) și bannerul de eroare. Nu salvează nimic. După fiecare pas predă
pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas. Așteptările după acțiunea principală mutată în bară folosesc state="attached" (nodul își schimbă locul, nu dispare)."""
import re

import verifica_pas as VP

EROARE = "() => window.dispatchEvent(new ErrorEvent('error', {error: new Error('proba X05'), message: 'proba X05'}))"


def _cabinet(pg):
    """Din parcurs_16_6.py: memoria ferestrei deschise se șterge întâi; dacă cabinetul nu răspunde la clic, pagina se reîncarcă, de cel mult trei ori."""
    for incercare in range(3):
        try:
            pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
            pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
            pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
            pg.wait_for_timeout(800)
            pg.click("button.cab-card:has([data-cheie='firme'])", timeout=10000)
            break
        except Exception:   # noqa: BLE001
            if incercare == 2:
                raise
            pg.reload(wait_until="domcontentloaded")
    pg.wait_for_timeout(600)
    if pg.query_selector("#opt-existente"):
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)


def firma(pg, nume="F1 Comert Stoc"):
    """Fereastra firmei `nume`, pornită de la cabinet; așteaptă butoanele ei."""
    _cabinet(pg)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(500)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    firma(pg)
    pas("a")                                           # fereastra firmei = prima fereastră: numai „✕”, fără acțiune principală
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", state="attached", timeout=20000)
    pas("b")
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-data", timeout=20000)
    pas("g")                                           # editorul de notă: Salvează inactiv, în bară
    firma(pg)
    pg.click("#fa-facturi")
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-emite", state="attached", timeout=20000)
    pas("c")
    firma(pg, "F5 SRL Salariati")
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-contare", state="attached", timeout=30000)
    pas("d")
    firma(pg)
    pg.click("#fa-planconturi")
    pg.wait_for_selector("#pcf-adauga", state="attached", timeout=20000)
    pas("e")
    firma(pg)
    pg.click("#fa-facturi")
    pg.click("#fac-model")
    pg.wait_for_selector("#mf-salveaza", state="attached", timeout=20000)
    pas("f")
    firma(pg)
    pg.click("#fa-facturi")
    pg.click("#fac-istoric")
    pg.click("#fac-prev")                              # 10/2026: facturi emise (ca în core/catalog_ecrane.json, „Fereastră mică — confirmare storno F1”)
    pg.locator("button.fac-frand-btn").first.click()
    pg.click("#fd-storno")
    pg.wait_for_selector(".fereastra.fer-mic", timeout=20000)
    pas("h")
    firma(pg)
    pg.click("#fa-declaratii")
    pg.locator("li.ds-lista-rand", has_text="D104").first.click()
    pg.click("#dec-continua")
    pg.wait_for_selector("#d104-regen", state="attached", timeout=30000)
    pas("i")
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra details').forEach((d) => { d.open = false; })")
    pas("j")                                           # secțiunile pliate: butonul rămâne în bară (M3)
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.wait_for_selector("#nav-iesire", timeout=30000)
    pas("k")
    pg.evaluate(EROARE)
    pg.wait_for_selector("#eroare-globala", timeout=5000)
    pas("l")
    try:
        pg.click("#eroare-globala .nav-x", timeout=3000)   # pe baza bannerul n-are „✕”: pasii m și n pică, parcursul continuă
    except Exception:   # noqa: BLE001
        pass
    pas("m")
    pg.evaluate(EROARE)
    pg.wait_for_selector("#eroare-globala", timeout=5000)
    pas("n")
