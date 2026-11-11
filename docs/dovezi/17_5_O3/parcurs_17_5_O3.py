# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-O3 (continuarea lui 17.5-O) (ferestre cu acțiuni și contoare care spun adevărul), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului (pasul implicit), apoi pe F1 Comert Stoc: cardul «NIR-urile lunii» din Stocuri (săgeata ferestrei de card), Rapoarte comerciale (rândul de jos), Fișa salariatului Ionescu Vasile pe F5 SRL Salariati (butoanele),
fereastra mică «Stornează factura» (deschisă din detaliul unei facturi, lăsată fără a storna), Mișcări și fișe de magazie (lista de articole) și Analitică stoc (Consum și Clasificare ABC).
Pe fiecare pas se judecă texte sau numărul elementelor numite. Nu salvează nimic, nu alege niciun fișier, nu apasă «Confirm stornarea». Nu atinge bonurile.
Un clic sau o așteptare care eșuează ridică eroarea și oprește parcursul (pe commitul de bază elementele există, iar aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc"
F5 = "F5 SRL Salariati"


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

    # AC180: F1, Stocuri > cardul «NIR-urile lunii»: săgeata ferestrei de card
    ecran(pg, F1, "fa-stocuri", TOP + "[data-card='nir']")
    apasa(pg, "[data-card='nir']", "#nir-mesaj", 2000)
    pas("nir")                      # a.1: săgeata nu mai poartă «Înapoi la Stocuri»

    # AC181: F1, Rapoarte comerciale
    ecran(pg, F1, "fa-rapoarte", TOP + "#r-var-salveaza")
    pas("rapoarte")                 # a.2: «Salvează varianta curentă» nu mai e buton principal

    # AC108: F5, Fișa salariatului Ionescu Vasile (Stat de plată > rândul salariatului)
    firma(pg, F5)
    intra(pg, "fa-salariati", TOP + "#sp-tabel tbody tr.sp-rand")
    try:
        pg.locator(TOP + "#sp-tabel tbody tr.sp-rand", has_text="Ionescu").first.locator(".sp-deschide").click(timeout=10000)
        pg.wait_for_selector(TOP + "#ss-butoane", state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.wait_for_timeout(1500)
    pas("salariat")                 # a.3 («Fluturaș» nu mai e în rândul de butoane), f.4 («Fluturaș» rămâne în fereastră)

    # AC143: F1, fereastra mică «Stornează factura» (din detaliul primei facturi; nu se confirmă nimic)
    firma(pg, F1)
    intra(pg, "fa-facturi", TOP + "#fac-istoric")
    apasa(pg, "#fac-istoric", "#fac-prev", 1200)
    apasa(pg, "#fac-prev", "button.fac-frand-btn", 1500)
    try:
        pg.locator(TOP + "button.fac-frand-btn").first.click(timeout=10000)
        pg.wait_for_selector(TOP + "#fd-storno", state="attached", timeout=20000)
        pg.click(TOP + "#fd-storno", timeout=10000)
        pg.wait_for_selector(".fereastra.fer-mic", timeout=20000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.wait_for_timeout(1000)
    pas("storno")                   # a.4 (fără «←» în fereastra mică), f.5 («Renunță» rămâne)

    # AC080 + AC081: F1, Stocuri > «Mișcări, fișe de magazie, coduri, nivel minim» (lista de articole), apoi Analitică stoc
    ecran(pg, F1, "fa-stocuri", TOP + "#cv-toggle")
    apasa(pg, "#cv-toggle", "#cv-art option", 2500)
    pas("miscari")                  # a.5 («Marfa A · stoc 122 buc»), a.6 (lipsește «Marfa A · stoc 145 buc»)
    apasa(pg, "#cv-ana", None, 3000)
    pas("analitica")                # a.7 («cumulat 100%»), a.8 (lipsește «.000 buc»)

    # AC182: cabinet, banda «Suport» (Sesizare nouă): «Trimite sesizarea» o singură dată
    acasa(pg)
    try:
        pg.click("[data-banda='raport']", timeout=10000)
        pg.wait_for_selector(TOP + "#rap-zona-sesizare", state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        raise   # un clic sau o așteptare eșuată oprește parcursul (nu se judecă o fereastră care nu s-a deschis)
    pg.wait_for_timeout(1500)
    pas("suport")                   # a.9 (fără al doilea «Trimite sesizarea» în conținut), f.6 («Trimite sesizarea» rămâne)
