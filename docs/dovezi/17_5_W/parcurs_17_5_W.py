# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-W (decontul care spune ce îi lipsește și Control fiscal care explică diferența), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului (pasul implicit), apoi pe F1 Comert Stoc: Declarații › D300 pe 10/2026 › pasul 2 (avertismentul cu rapoartele Z în ciornă, butonul inactiv, motivul și butoanele notelor),
Declarații › D394 pe 10/2026 › pasul 2 (aceleași) și Control fiscal › «Declarație vs contabilitate» (explicația ciornelor pe conturile 4427, 4426, 4423).
Pe fiecare pas se judecă texte sau numărul elementelor numite. Nu apasă «Pune în „De depus”» (butonul e inactiv în starea de după lot; pe baza lotului nu se apasă), nu salvează, nu depune și nu adaugă nimic în coadă.
Un clic sau o așteptare care eșuează ridică eroarea și oprește parcursul (pe commitul de bază elementele există, iar aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării; luna comparată de Control fiscal vine din data serverului (luna precedentă)
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
    """Clic pe cardul `id_card` din fereastra firmei și așteptarea ecranului (dacă nu apare, parcursul se oprește)."""
    try:
        pg.click(TOP + "#" + id_card, timeout=10000)
        pg.wait_for_selector(asteapta, state="attached", timeout=60000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.wait_for_timeout(600)


def declaratia(pg, tip, an, luna):
    """Declarații › `tip` pe luna `luna` din `an` › „Continuă”, până la pasul 2 (butonul «Pune în „De depus”» sau eroarea generării)."""
    firma(pg, F1)
    intra(pg, "fa-declaratii", TOP + "#dec-tip")
    try:
        optiune = TOP + "#dec-tip option[value='%s']" % tip
        if not pg.locator(optiune).count() and pg.locator(TOP + "#dec-alte").count():   # „Alte declarații” e pliată: tipul se caută acolo
            if pg.get_attribute(TOP + "#dec-alte", "aria-expanded") != "true":
                pg.click(TOP + "#dec-alte", timeout=10000)
            pg.wait_for_selector(optiune, state="attached", timeout=10000)
        pg.select_option(TOP + "#dec-tip", tip)
        pg.fill(TOP + "#dec-an", str(an))
        pg.dispatch_event(TOP + "#dec-an", "change")
        if pg.locator(TOP + "#dec-luna").count():
            pg.select_option(TOP + "#dec-luna", str(luna))
        pg.click(TOP + "#dec-continua", timeout=10000)
        pg.wait_for_selector(TOP + "#dec-trimite, " + TOP + ".dec-eroare", state="attached", timeout=120000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă un pas care nu s-a deschis)
    pg.wait_for_timeout(2500)   # eticheta butonului vine după două cereri (rolul), apoi butoanele notelor


def la_bara(pg):
    """v2: derulează ecranul de verificare până la butonul din bara de jos (#dec-trimite): Constatări, «Avertismente» și bara de jos intră în aceeași captură a pasului."""
    pg.evaluate("() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #dec-trimite'); if (b) b.scrollIntoView(); }")
    pg.wait_for_timeout(500)


def la_comparatie(pg):
    """v2: aduce în ecran titlul secțiunii «Declarație vs contabilitate» (H3 dinaintea lui #cf-incrucisat) cu rândurile ei: perioada comparată și comparațiile 4427, 4426, 4423."""
    pg.evaluate("() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) #cf-incrucisat'); if (e && e.previousElementSibling) e.previousElementSibling.scrollIntoView({block: 'start'}); }")
    pg.wait_for_timeout(500)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal» (aserțiunea probei contractului)

    # AC184: F1, Declarații › D300 pe 10/2026 › pasul 2
    declaratia(pg, "d300", 2026, 10)
    la_bara(pg)
    pas("d300")                     # f.2 (pasul 2 pe D300), a.1–a.2 (avertismentul), a.3 (butonul inactiv), a.4 (motivul), a.5 (butonul notei), a.6 (eticheta)

    # AC184: F1, Declarații › D394 pe 10/2026 › pasul 2
    declaratia(pg, "d394", 2026, 10)
    la_bara(pg)
    pas("d394")                     # f.3 (pasul 2 pe D394), a.7 (butonul inactiv), a.8 (avertismentul)

    # AC185: F1, Control fiscal › Declarație vs contabilitate
    firma(pg, F1)
    intra(pg, "fa-control", TOP + "#cf-incrucisat")
    pg.wait_for_timeout(2500)
    la_comparatie(pg)
    pas("control")                  # f.4 (perioada comparată), a.9–a.11 (ciornele pe 4427, 4426, 4423)
