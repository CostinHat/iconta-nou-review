# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-K (etichete rupte și zone de derulare la rezoluții mici), cu contul administratorului (dovada.71507), ceas înghețat 03.11.2026:
pagina principală a cabinetului la 1366×768 (pasul implicit), apoi, cu pagina de 603×590 px, e-Transport F1 (filele notificării) și Control fiscal (firmă) F1 (rândul D406 01/2026 marcat «în afara iConta.eu»:
butoanele «Modifică marcarea» și «Anulează marcarea»), apoi, cu pagina readusă la 1366×768, Plan de conturi F1.
Pe fiecare pas se judecă ce poate judeca oracolul cu măsurile existente din verifica_pas (text, inaltime_px): f.1 și f.2 pe text vizibil (invariante față de lot), a.2 și a.3 pe înălțimea elementelor (interval_px). Celelalte
măsuri ale lotului (rânduri de text, poziția calculată, acoperirea câmpurilor, locul de derulare, placeholderul) le face numai testul arhitectului e2e_ferestre_17_5_K.py. Nu salvează nimic, nu alege niciun fișier;
singurele acțiuni sunt deschiderea ferestrelor și, în Control fiscal, deschiderea ferestrei «Vezi declarațiile» dacă rândul marcat stă în grupul «Înainte de preluare».
Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
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
        pass
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(400)


def intra(pg, id_card, asteapta):
    """Clic pe cardul `id_card` din fereastra firmei și așteptarea ecranului (dacă nu apare, pasul se judecă pe ce s-a desenat)."""
    try:
        pg.click(TOP + "#" + id_card, timeout=10000)
        pg.wait_for_selector(asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(600)


def ecran(pg, nume_firma, id_card, asteapta):
    firma(pg, nume_firma)
    intra(pg, id_card, asteapta)
    pg.wait_for_timeout(1500)


def centreaza(pg, selector):
    """Aduce elementul în mijlocul zonei vizibile (captura de 603×590 îl arată); înghițit dacă lipsește."""
    try:
        pg.evaluate("(s) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + s); if (e) e.scrollIntoView({block: 'center'}); }", selector)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(500)


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

    pg.set_viewport_size({"width": 1366, "height": 768})
    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal» (aserțiunea probei contractului)

    # AC043: e-Transport F1, la 603×590: cele patru file `.rap-tab` pe un singur rând (înălțime 24–40 px)
    pg.set_viewport_size({"width": 603, "height": 590})
    ecran(pg, F1, "fa-etransport", TOP + ".rap-tabs .rap-tab")
    sus(pg)
    pas("etransport")               # a.2

    # AC057: Control fiscal (firmă) F1, la 603×590: rândul D406 01/2026 (marcat «în afara iConta.eu»): «Modifică marcarea» și «Anulează marcarea» (înălțime 20–30 px)
    ecran(pg, F1, "fa-control", TOP + ".cf-grup-titlu")
    try:   # rândul marcat poate sta în grupul «Înainte de preluare»: fereastra lui se deschide din «Vezi declarațiile»
        if not pg.locator(TOP + ".cf-extern-anuleaza").count():
            pg.click(TOP + ".cf-inainte-btn", timeout=10000)
            pg.wait_for_selector(TOP + ".cf-extern-anuleaza", state="attached", timeout=20000)
            pg.wait_for_timeout(1000)
    except Exception:   # noqa: BLE001
        pass
    centreaza(pg, "tr:has(.cf-extern-anuleaza)")
    pas("control_firma")            # a.3

    # f.2: Plan de conturi F1, la 1366×768: eticheta «Adaugă analitic»
    pg.set_viewport_size({"width": 1366, "height": 768})
    ecran(pg, F1, "fa-planconturi", TOP + "#pcf-lista")
    sus(pg)
    pas("plan_conturi")             # f.2
