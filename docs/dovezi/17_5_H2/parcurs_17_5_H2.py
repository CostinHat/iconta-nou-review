# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-H2, cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026: pagina principală a cabinetului (pasul implicit), apoi pe F1 Comert Stoc
Istoric facturi (luna ceasului, fără facturi), Contracte (fără șabloane), Import date (meniul), Detaliu factură F1A19 (Istoric › «← luna» › rândul F1A19), pe F5 SRL Salariati
Fișa salariatului (Ionescu Vasile) și Prime, sporuri, ore suplimentare (formular gol), apoi pe F1 Casă — dispoziție nouă și Registru jurnal — notă nouă (formulare goale); la sfârșit,
după schimbarea rezoluției la 603×590 și reîncărcarea paginii, din nou Casă — dispoziție nouă, apoi Fișa salariatului (Ionescu Vasile). Pe fiecare pas se judecă piesele cadrului: lista goală, contorul, butonul principal și motivul lui.
Nu salvează nimic, nu alege niciun fișier, nu completează niciun câmp. Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile lotului pică).
Importă numai biblioteca standard și verifica_pas."""
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


def apasa(pg, selector, asteapta=None, timp=1500):
    """Clic pe `selector` în fereastra de sus, apoi așteptarea lui `asteapta` (înghițit dacă lipsește)."""
    try:
        pg.click(TOP + selector, timeout=10000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def ecran(pg, nume_firma, id_card, asteapta):
    firma(pg, nume_firma)
    intra(pg, id_card, asteapta)
    pg.wait_for_timeout(1500)


def istoric(pg):
    """Facturi › Istoric facturi, pe luna ceasului înghețat (11/2026): F1 nu are facturi în luna aceasta."""
    ecran(pg, F1, "fa-facturi", TOP + "#fac-istoric")
    apasa(pg, "#fac-istoric", "#fac-prev", 2000)


def detaliu(pg):
    """Istoric facturi › «← luna» (10/2026) › rândul facturii F1A19 › Detaliu factură."""
    istoric(pg)
    apasa(pg, "#fac-prev", "button.fac-frand-btn", 1500)
    apasa(pg, "button.fac-frand-btn[data-doc='F1A19']", ".fd-tabel", 2000)


def fisa(pg):
    """F5 › Salariați (statul de plată; dacă luna ceasului nu are rânduri, «← luna» de cel mult 3 ori, ca docs/dovezi/17_2/parcurs_17_2.py) › primul salariat › fișa."""
    ecran(pg, F5, "fa-salariati", TOP + "#sp-contare")
    for incercare in range(4):
        try:
            pg.wait_for_selector(TOP + "#sp-tabel tbody tr.sp-rand", timeout=12000)
            break
        except Exception:   # noqa: BLE001
            if incercare == 3:
                break
            try:
                pg.click(TOP + "#sp-prev", timeout=5000)
            except Exception:   # noqa: BLE001
                break
            pg.wait_for_timeout(1500)
    try:
        pg.locator(TOP + "#sp-tabel tbody tr.sp-rand").first.locator(".sp-deschide").click(timeout=10000)
        pg.wait_for_selector(TOP + "#ss-butoane", timeout=30000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)


def elemente(pg):
    """Fișa salariatului › «Prime, sporuri, ore supl.» (formularul elementelor variabile, gol)."""
    fisa(pg)
    try:
        pg.locator(TOP + "button", has_text="Prime, sporuri").first.click(timeout=10000)
        pg.wait_for_selector(TOP + "#el-adauga", state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)


def casa(pg):
    """Casă › «+ Dispoziție nouă» (formular gol)."""
    ecran(pg, F1, "fa-casa", TOP + "#c-toggle")
    apasa(pg, "#c-toggle", "#c-adauga", 1500)


def nota(pg):
    """Registru jurnal › «+ Notă nouă» (formular gol)."""
    ecran(pg, F1, "fa-jurnal", TOP + "#j-nota-noua")
    apasa(pg, "#j-nota-noua", "#je-salveaza", 1500)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal» (aserțiunea probei contractului)
    istoric(pg)
    pas("istoric")                  # a.1–a.3, h.1: lista goală fără tabel, fără contor, fără PDF de rezervă
    ecran(pg, F1, "fa-contracte", TOP + "#c-nou")
    pas("contracte")                # a.4, f.2
    ecran(pg, F1, "fa-import", TOP + "#mig-pasi")
    pas("import")                   # a.5, a.6, f.4: meniul fără contor și fără buton principal; f.4 «Audit de preluare» = fereastra s-a deschis
    detaliu(pg)
    pas("detaliu")                  # h.2: capul tabelului nu acoperă rândul «Marfa A»
    fisa(pg)
    pas("fisa")                     # h.3: capetele tabelelor din «Compoziția netului»
    elemente(pg)
    pas("elemente")                 # a.7, f.3: «Adaugă» inactiv cu motiv
    casa(pg)
    pas("casa")                     # a.8, a.9: «Adaugă» + motivul în fj-motiv
    nota(pg)
    pas("nota")                     # a.10, a.11: «Salvează» + motivul în fj-motiv
    pg.set_viewport_size({"width": 603, "height": 590})
    casa(pg)                        # reîncărcare la rezoluția nouă (firma() face goto), apoi Casă — dispoziție nouă
    pas("casa603")                  # a.12, h.4
    fisa(pg)                        # aceeași rezoluție (603×590): firma() face goto, apoi Statul de plată › primul salariat › fișa
    pas("fisa603")                  # h.5: capetele tabelelor din «Compoziția netului» la 603×590
