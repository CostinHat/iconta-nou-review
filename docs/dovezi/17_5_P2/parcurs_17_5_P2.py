# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-P2 (bonul cu codul cumpărătorului și temeiul fiscal lângă TVA), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului (pasul implicit), apoi pe F1 Comert Stoc: Bonuri și chitanțe, bonul martor «Benzinarie Martor P SRL» (semănat de docs/dovezi/17_5_P2/semana_bon.py după restaurarea bazei),
deschis din listă și lăsat necertificat.
Pe fiecare pas se judecă texte. Nu salvează nimic, nu apasă «Certifică și contează», nu adaugă documente. Un clic sau o așteptare care eșuează ridică eroarea și oprește parcursul
(pe commitul de bază elementele există, iar aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc"


def card(cheie):
    return "button.cab-card:has([data-cheie='%s'])" % cheie


def acasa(pg):
    """Pagina principală proaspătă (goto): memoria ferestrei deschise se șterge întâi; se așteaptă cardurile și sintezele lor (nimic „se încarcă”)."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    try:
        pg.wait_for_function("() => ![...document.querySelectorAll('.cab-card-sinteza')].some((e) => e.textContent.includes('se încarcă'))", timeout=20000)
    except Exception:   # noqa: BLE001 — contoarele întârzie: pasul se judecă pe ce s-a desenat
        pass
    pg.wait_for_timeout(800)


def firma(pg, nume):
    """Pagina principală › Firme › Firme existente › firma `nume`, cu toate grupurile ferestrei ei deschise (grupurile sunt pliate implicit)."""
    acasa(pg)
    try:
        pg.click(card("firme"), timeout=10000)
        pg.wait_for_selector("#opt-existente", timeout=20000)
        pg.click("#opt-existente")
        pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
        pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
        pg.wait_for_selector("#fa-facturi", timeout=20000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(400)


def intra(pg, id_card, asteapta):
    """Clic pe cardul `id_card` din fereastra firmei și așteptarea ecranului (dacă nu apare, pasul se judecă pe ce s-a desenat)."""
    try:
        pg.click(TOP + "#" + id_card, timeout=10000)
        pg.wait_for_selector(asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.wait_for_timeout(600)


def apasa(pg, selector, asteapta=None, timp=1500):
    """Clic pe `selector` în fereastra de sus, apoi așteptarea lui `asteapta` (înghițit dacă lipsește)."""
    try:
        pg.click(TOP + selector, timeout=10000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.wait_for_timeout(timp)


def ecran(pg, nume_firma, id_card, asteapta):
    firma(pg, nume_firma)
    intra(pg, id_card, asteapta)
    pg.wait_for_timeout(1500)


def sus(pg):
    """Corpul ferestrei de sus derulat la început."""
    try:
        pg.evaluate("() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); if (c) c.scrollTop = 0; "
                    "const z = document.querySelector('.fereastra-overlay:not(.fundal) .zona-derulare'); if (z) z.scrollTop = 0; }")
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(500)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal» (aserțiunea probei contractului)

    # AC153 + AC154: F1, Bonuri și chitanțe > bonul martor (codul cumpărătorului absent, articol pe contul 6022)
    ecran(pg, F1, "fa-bonuri", TOP + "[data-doc], " + TOP + ".stare-goala")
    try:
        pg.locator(TOP + "[data-doc]", has_text="Benzinarie Martor P SRL").click(timeout=10000)
        pg.wait_for_selector(TOP + "#d-certifica", state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    titlu = pg.locator(TOP + "h2.pf-titlu").inner_text()
    if "Bon fiscal" not in titlu or "P-1" not in titlu:
        raise RuntimeError("Parcurs P: fereastra nu aparține bonului martor")
    pg.wait_for_timeout(1500)
    pas("bon")                      # f.2 («Bon fiscal»), f.3 («Comerciant»), a.1 («CUI cumpărător pe bon»), a.2 (TVA nedeductibil), a.3 (nota combustibilului)
