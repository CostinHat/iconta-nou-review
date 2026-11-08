# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-B, cu contul administratorului (dovada.71507): pagina principală a cabinetului la 1366×768 (pasul implicit), apoi, după schimbarea rezoluției la 603×590 și reîncărcarea paginii, trei ferestre de lucru ale firmei F1 Comert Stoc:
Bancă, Stocuri și Registru jurnal (octombrie 2026, după un „← luna”). Nu salvează nimic. După fiecare pas predă pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas.
ATENȚIE: rezoluția se schimbă ÎNAINTE de reîncărcarea paginii (firma() face goto), iar fiecare fereastră se deschide de la zero. Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă: aserțiunile pasului judecă ce s-a desenat
(pe commitul de bază aserțiunile lotului pot pica)."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
ZONA = TOP + ".zona-derulare"
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
    except Exception:   # noqa: BLE001 — pasul se judecă pe ce s-a desenat (aserțiunile pică), parcursul continuă
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


def asteapta_zona(pg):
    """Zona de derulare a ferestrei o pune navigatorul după desenarea tabelului; dacă nu apare, aserțiunea pasului o constată."""
    try:
        pg.wait_for_selector(ZONA, state="attached", timeout=10000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(500)


def ecran_banca(pg):
    firma(pg, F1)
    intra(pg, "fa-banca", TOP + "#bk-lista")
    asteapta_zona(pg)


def ecran_jurnal(pg):
    """Registru jurnal se deschide pe luna ceasului înghețat (noiembrie 2026); „← luna” o dată, necondiționat, ca e2e_pilot_x09.py: pasul se judecă pe 10/2026."""
    firma(pg, F1)
    intra(pg, "fa-jurnal", TOP + "#j-prev")
    try:
        pg.click(TOP + "#j-prev", timeout=10000)
    except Exception:   # noqa: BLE001 — butonul lipsește: pasul se judecă pe ce s-a desenat (aserțiunea pică), parcursul continuă
        pass
    pg.wait_for_timeout(1500)
    asteapta_zona(pg)


def ecran_stocuri(pg):
    """Stocuri se deschide pe luna ceasului înghețat (noiembrie 2026); datele de test sunt din octombrie: „← luna” o dată, ca e2e_pilot_x09.py."""
    firma(pg, F1)
    intra(pg, "fa-stocuri", TOP + ".fereastra-corp")
    try:
        pg.locator(TOP + ".fereastra-corp button", has_text="← luna").first.click(timeout=10000)
    except Exception:   # noqa: BLE001 — pasul se judecă pe ce s-a desenat, parcursul continuă
        pass
    pg.wait_for_timeout(1500)
    asteapta_zona(pg)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                                    # 12 carduri (aserțiunea probei contractului)
    pg.set_viewport_size({"width": 603, "height": 590})
    ecran_banca(pg)                                    # reîncărcare la rezoluția nouă (firma() face goto), apoi Bancă
    pas("banca603")                                    # zona de derulare a ferestrei Bancă
    ecran_stocuri(pg)
    pas("stocuri603")                                  # zona de derulare a ferestrei Stocuri, octombrie 2026
    ecran_jurnal(pg)
    pas("jurnal603")                                   # zona de derulare a ferestrei Registru jurnal
