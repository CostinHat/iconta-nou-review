# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-G, cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026: pagina principală a cabinetului (pasul implicit),
fereastra De validat (cardul „De validat”), apoi fereastra Control fiscal (cardul „Control fiscal”). Răspunsurile serverului sunt cele reale (fără interceptări).
Nu salvează nimic și nu deschide niciun rând (coloana Conturi se judecă pe rândurile închise). Clicurile eșuate sunt înghițite (pe bază aserțiunile lotului pică)."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "


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


def deschide(pg, cheie, asteapta, timp=30000):
    """Pagina principală › cardul `cheie` și așteptarea ecranului (dacă nu apare, pasul se judecă pe ce s-a desenat)."""
    acasa(pg)
    try:
        pg.click(card(cheie), timeout=10000)
        pg.wait_for_selector(asteapta, state="attached", timeout=timp)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")
    deschide(pg, "validat", TOP + "#val-titlu")
    pas("validat")
    deschide(pg, "control", TOP + "#cf-lista tbody tr", timp=60000)
    pas("control")
