# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-X3 (continuarea lui 17.5-X2 și 17.5-X) (rezultatul auditului Pilot din 13.11.2026), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului (pasul implicit), apoi pe F1 Comert Stoc: Declarații pasul 1 (D300 și D394 pe 09/2026), Închidere lună (09/2026 deblocare, 10/2026), Stocuri, NIR nou,
Control fiscal, Verificări, Clienți și Furnizori (P7), Registru jurnal (10/2026 și nota nouă pe luna blocată 09/2026), Casă.
Pe fiecare pas se judecă texte, valori de câmp sau numărul elementelor numite. Parcursul este numai de citire: nu trimite motivul de deblocare, nu salvează NIR sau nota, nu validează, nu șterge, nu importă și nu contează nimic la Bancă, nu depune și nu adaugă nimic în coadă.
Elementul nou al lotului (selectorul «Luna comparată») este căutat opțional: pe commitul de bază lipsește, parcursul merge mai departe și aserțiunile a. pică; un clic pe un element care există pe bază și lipsește ridică eroarea și oprește parcursul.
Importă numai biblioteca standard și verifica_pas. Nerulat la redactare (nu s-a pornit nimic): selectorurile se validează pe baza lotului."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import re

import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc"


def card(cheie):
    return "button.cab-card:has([data-cheie='%s'])" % cheie


def acasa(pg):
    """Pagina principală proaspătă (goto): memoria ferestrei deschise se șterge întâi; se așteaptă cardurile și sintezele lor."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    try:
        pg.wait_for_function("() => ![...document.querySelectorAll('.cab-card-sinteza')].some((e) => e.textContent.includes('se încarcă'))", timeout=20000)
    except Exception:   # noqa: BLE001 — contoarele întârzie: pasul se judecă pe ce s-a desenat
        pass
    pg.wait_for_timeout(800)


def firma(pg, nume):
    """Pagina principală › Firme › Firme existente › firma `nume`, cu grupurile ferestrei ei deschise."""
    acasa(pg)
    pg.click(card("firme"), timeout=10000)
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(400)


def intra(pg, id_card, asteapta):
    """Clic pe cardul `id_card` din fereastra firmei și așteptarea ecranului (dacă nu apare, parcursul se oprește)."""
    pg.click(TOP + "#" + id_card, timeout=10000)
    pg.wait_for_selector(asteapta, state="attached", timeout=60000)
    pg.wait_for_timeout(600)


def la_luna(pg, pref, luna, an):
    """Navighează cu #<pref>-prev / #<pref>-next până când textul ferestrei spune «LL/AAAA» pentru luna cerută (cel mult 14 pași; dacă nu o găsește, pasul se judecă pe ce se vede)."""
    tinta = "%02d/%d" % (luna, an)
    for _ in range(14):
        text = pg.evaluate("() => (document.querySelector('.fereastra-overlay:not(.fundal) .fereastra') || document.body).innerText")
        m = re.search(r"(?:Luna\s+)?(\d{2})/(\d{4})", text)
        if not m or m.group(0).endswith(tinta):
            break
        actuala = (int(m.group(2)), int(m.group(1)))
        buton = "#%s-prev" % pref if actuala > (an, luna) else "#%s-next" % pref
        if not pg.locator(TOP + buton).count():
            break
        pg.click(TOP + buton, timeout=10000)
        pg.wait_for_timeout(900)


def rand_lista(pg, text):
    """Clic pe rândul din lista cu căutare al pasului 1 din Declarații care conține `text` (lista „Alte declarații” se deschide dacă rândul nu se vede)."""
    rand = pg.locator(TOP + ".ds-lista-rand", has_text=text).first
    if not rand.count() and pg.locator(TOP + "#dec-alte").count():
        if pg.get_attribute(TOP + "#dec-alte", "aria-expanded") != "true":
            pg.click(TOP + "#dec-alte", timeout=10000)
        pg.wait_for_timeout(500)
    rand.click(timeout=10000)
    pg.wait_for_timeout(600)
    # lista se redesenează de sus după clic: rândul marcat ca ales e adus în vedere, ca să intre în captură (descrieri verificate, 13.11)
    pg.evaluate("() => { const r = document.querySelector('.fereastra-overlay:not(.fundal) .ds-lista-ales-rand'); if (r) r.scrollIntoView({block: 'nearest'}); }")
    pg.wait_for_timeout(300)


def alege_luna_comparata(pg, luna):
    """Alege luna în selectorul «Luna comparată» (dacă există): măsurătorile din Control fiscal nu depind astfel de data serverului."""
    try:
        sel = pg.get_by_label("Luna comparată")
        if sel.count():
            sel.first.select_option(label=luna)
            pg.wait_for_timeout(2500)
    except Exception:   # noqa: BLE001 — pe bază selectorul lipsește
        pass


def deschide_declaratii(pg):
    firma(pg, F1)
    intra(pg, "fa-declaratii", TOP + "#dec-tip")


def asteapta_text(pg, text, ms=20000):
    try:
        pg.wait_for_function("(t) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return !!e && e.innerText.includes(t); }", arg=text, timeout=ms)
    except Exception:   # noqa: BLE001 — pasul se judecă pe ce s-a desenat
        pass


def optional_click(pg, selector, ms=3000):
    """Clic pe un element NOU al lotului: dacă nu există (commit de bază), nu se întâmplă nimic și pasul se judecă oricum."""
    try:
        if pg.locator(selector).count():
            pg.click(selector, timeout=ms)
            pg.wait_for_timeout(800)
            return True
    except Exception:   # noqa: BLE001
        pass
    return False


def vezi(pg, text):
    """Derulează ecranul până la primul text care conține `text` (pentru ca rândul judecat să intre în captură)."""
    pg.evaluate("""(t) => { const r = document.querySelector('.fereastra-overlay:not(.fundal)'); if (!r) return;
        const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT);
        while (w.nextNode()) { if (w.currentNode.textContent.includes(t)) { w.currentNode.parentElement.scrollIntoView({block: 'center'}); break; } } }""", text)
    pg.wait_for_timeout(400)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1

    # 727.2: Declarații pasul 1, clic pe rândul D300 din 09/2026 (nu pe primul)
    deschide_declaratii(pg)
    rand_lista(pg, "D300 · 09/2026")
    pas("decl_lista")               # f.2, a.1, a.2
    pg.click(TOP + "#dec-continua", timeout=10000)
    pg.wait_for_selector(TOP + "#dec-trimite, " + TOP + ".dec-eroare, " + TOP + "#dec-gol-da", state="attached", timeout=120000)   # a treia stare: perioada fără operațiuni (declaratii.js, #dec-gol-da)
    pg.wait_for_timeout(2500)
    pas("decl_pas2")                # a.3
    deschide_declaratii(pg)
    rand_lista(pg, "D394 · 09/2026")
    pas("decl_d394")                # a.4, a.5

    # 729.1 și 763: Închidere lună
    firma(pg, F1)
    intra(pg, "fa-inchidere", TOP + "#il-lock")
    la_luna(pg, "il", 9, 2026)
    if pg.locator(TOP + "#il-lock", has_text="Deblochează").count():
        pg.click(TOP + "#il-lock", timeout=10000)
        pg.wait_for_selector(TOP + "#bl-motiv", state="attached", timeout=20000)
    pas("inchidere")                # f.3, a.6 (motivul gol: confirmarea inactivă)
    firma(pg, F1)
    intra(pg, "fa-inchidere", TOP + "#il-lock")
    la_luna(pg, "il", 10, 2026)
    pg.wait_for_timeout(6000)       # controalele lunii se încarcă (763)
    pas("inchidere_10")             # f.4, a.7

    # F089 și 739: Stocuri, NIR nou
    firma(pg, F1)
    intra(pg, "fa-stocuri", TOP + "#sn-toggle")
    asteapta_text(pg, "Stoc validat")
    pas("stocuri")                  # f.5
    pg.click(TOP + "#sn-toggle", timeout=10000)
    pg.wait_for_selector(TOP + "#sn-numar", state="attached", timeout=20000)
    pg.wait_for_timeout(800)
    pas("nir")                      # f.6, a.8

    # 484: Control fiscal
    firma(pg, F1)
    intra(pg, "fa-control", TOP + "#cf-incrucisat")
    pg.wait_for_timeout(2500)
    alege_luna_comparata(pg, "10/2026")   # element nou al lotului: pe bază lipsește și se citește luna implicită
    vezi(pg, "De urmărit")
    pas("control_decl")             # f.7
    vezi(pg, "Nu se poate verifica")
    pas("control_decl2")            # a.9
    vezi(pg, "Perioada comparată")
    pas("control_incr")             # f.8, a.12
    pg.evaluate("""() => { const r = document.querySelector('.fereastra-overlay:not(.fundal) #cf-incrucisat'); if (!r) return;
        const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT);
        while (w.nextNode()) { if (w.currentNode.textContent.includes('4423')) { w.currentNode.parentElement.scrollIntoView({block: 'center'}); break; } } }""")
    pg.wait_for_timeout(400)
    pas("control_4423")             # a.10, a.11
    selector = pg.get_by_label("Luna comparată")
    if selector.count():            # element nou al lotului: lipsește pe bază
        try:
            selector.first.select_option(label="09/2026")
            pg.wait_for_timeout(2500)
        except Exception:   # noqa: BLE001
            pass
    vezi(pg, "Perioada comparată")
    pas("control_09")               # a.13

    # F089, 602.1: Verificări
    firma(pg, F1)
    intra(pg, "fa-verificari", TOP + ".vf-lista")
    la_luna(pg, "vf", 10, 2026)
    pg.wait_for_timeout(2500)
    vezi(pg, "Stocuri (contabil vs fișe CV)")
    pas("verificari")               # f.9, a.14–a.16

    # 640.1, 633.1: P7 e în ecranul care are deja adăugarea, ștergerea, căutarea și «Verifică la ANAF» (clienti_ecran.js): Clienți și Furnizori
    firma(pg, F1)
    intra(pg, "fa-clienti", TOP + "#cl-nou")
    pas("clienti")                  # f.10
    pg.click(TOP + "#cl-nou", timeout=10000)
    pg.wait_for_selector(TOP + "#cln-anaf", state="attached", timeout=20000)
    pg.wait_for_timeout(600)
    pas("clienti_nou")              # f.11 (formularul nu se salvează)
    firma(pg, F1)
    intra(pg, "fa-furnizori", TOP + "#fz-nou")
    pas("furnizori")                # f.12

    # 602.1, 781: Registru jurnal 10/2026 (stornare, notă validată), apoi nota nouă pe luna blocată 09/2026
    firma(pg, F1)
    intra(pg, "fa-jurnal", TOP + "#j-prev")
    la_luna(pg, "j", 10, 2026)
    pg.wait_for_timeout(1500)
    optional_click(pg, TOP + ".jn-lista :text('Stornare')")          # rândul stornării se desface (dacă are detalii)
    optional_click(pg, TOP + ".jn-lista :text('validată')")          # o notă validată se desface (dacă are detalii)
    pas("jurnal")                   # f.13, a.17
    firma(pg, F1)
    intra(pg, "fa-jurnal", TOP + "#j-prev")
    la_luna(pg, "j", 9, 2026)
    pg.click(TOP + "#j-nota-noua", timeout=10000)
    pg.wait_for_selector(TOP + "#je-data", state="attached", timeout=20000)
    pg.wait_for_timeout(800)
    pas("jurnal_nota")              # f.14, a.18, a.19 (nota nu se salvează)

    # F015: Casă
    firma(pg, F1)
    intra(pg, "fa-casa", TOP + "#c-tabel")
    la_luna(pg, "c", 10, 2026)
    pg.wait_for_timeout(1200)
    vezi(pg, "Casa rămâne pe minus")
    pas("casa")                     # f.15, a.20
