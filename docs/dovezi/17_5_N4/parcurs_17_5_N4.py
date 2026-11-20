# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-N4 (ferestrele firmei F1 cu contoare, formate și acțiuni care spun adevărul), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului (pasul implicit), apoi pe F1 Comert Stoc: Scadențar (rândul de pastile din partea de sus), Verificări (rândul de sus «Luna …» și rândurile Stocuri și Intrastat, luna propusă la deschidere),
Cartea mare (contul 371 ales în lista de conturi) și e-Transport (bara de jos cu cele două butoane, cu starea SPV a firmei citită la deschidere).
Pe fiecare pas se judecă texte sau valori de câmp: textul / valoarea nouă există, textul vechi lipsește. Nu salvează nimic, nu alege niciun fișier; singurul câmp atins este lista de conturi din Cartea mare (#fc-cont, contul 371).
Import salariați (F5) nu are pas aici: oracolul nu poate alege un fișier (limita de la pct.6 al comenzii); AC117 și AC118 se dovedesc în e2e_ferestre_firma_17_5_N.py.
Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import re

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


def sus(pg):
    """Corpul ferestrei de sus derulat la început."""
    try:
        pg.evaluate("() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); if (c) c.scrollTop = 0; "
                    "const z = document.querySelector('.fereastra-overlay:not(.fundal) .zona-derulare'); if (z) z.scrollTop = 0; }")
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(500)


def intrastat_simulat(pg, pas):
    """Fixează valorile brute ale expedierilor. Aplicația formatează textul capturii."""
    ruta_praguri = re.compile(r"/tenants/\d+/intrastat-praguri(?:\?[^#]*)?$")

    def fixeaza_expedieri(ruta):
        if ruta.request.method != "GET":
            ruta.continue_()
            return
        raspuns = ruta.fetch()
        if raspuns.status != 200:
            ruta.fulfill(response=raspuns)
            return
        corp = raspuns.json()
        expedieri = corp.get("expedieri") if isinstance(corp, dict) else None
        if isinstance(expedieri, dict):
            expedieri.update(cumulat=12345.67, procent=1.2, status="sub_prag")
        ruta.fulfill(status=200, json=corp)

    pg.route(ruta_praguri, fixeaza_expedieri)
    try:
        with pg.expect_response(lambda r: r.request.method == "GET" and ruta_praguri.search(r.url), timeout=60000) as primit:
            ecran(pg, F1, "fa-verificari", TOP + "#vf-prev")
        if primit.value.status != 200:
            raise RuntimeError("a.4: răspuns Intrastat HTTP %s" % primit.value.status)
        exp = primit.value.json().get("expedieri") or {}
        if (exp.get("cumulat"), exp.get("procent"), exp.get("status")) != (12345.67, 1.2, "sub_prag"):
            raise RuntimeError("a.4: datele de probă lipsesc din răspunsul primit de pagină")
        # Așteaptă eticheta prezentă atât înainte, cât și după schimbarea formatului.
        rand = pg.locator(TOP + ".fereastra").get_by_text("Expedieri:", exact=False).last
        rand.scroll_into_view_if_needed(timeout=20000)
        pas("intrastat_simulat")
    finally:
        pg.unroute(ruta_praguri, fixeaza_expedieri)


def stocuri_simulate(pg, pas):
    """O singură navigare de probă. Celelalte rute ale ferestrei folosesc baza reală."""
    model = re.compile(r"/tenants/\d+/verificare-stocuri$")
    corp = {
        "conturi": [
            {"cont": "371", "sold_contabil": "1000.50", "valoare_fise_cv": "1000.50", "diferenta": "0.00", "ok": True},
            {"cont": "301", "sold_contabil": "20.00", "valoare_fise_cv": "1520.25", "diferenta": "-1500.25", "ok": False},
        ],
        "ok": False,
        "nota": "Diferențele pot veni din note ciornă nevalidate sau din operațiuni în afara fișelor de magazie.",
    }

    def raspunde(ruta):
        ruta.fulfill(status=200, json=corp)

    pg.route(model, raspunde)
    try:
        with pg.expect_response(lambda r: r.request.method == "GET" and model.search(r.url), timeout=60000) as rezultat:
            ecran(pg, F1, "fa-verificari", TOP + "#vf-prev")
        if rezultat.value.status != 200 or rezultat.value.json() != corp:
            raise RuntimeError("a.5: răspunsul simulat nu a ajuns în fereastra Verificări")
        titlu = pg.locator(TOP + ".fereastra").get_by_text("Stocuri (contabil vs fișe CV)", exact=False)
        titlu.last.scroll_into_view_if_needed(timeout=20000)
        pas("stocuri_simulate")
    finally:
        pg.unroute(model, raspunde)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal» (aserțiunea probei contractului)

    # AC077: F1, Scadențar (Facturi › Scadențar): rândul de pastile (.cf-sumar) cu a patra pastilă «2 fără scadență în sistem»
    ecran(pg, F1, "fa-facturi", TOP + "#fac-scadentar")
    apasa(pg, "#fac-scadentar", ".cf-sumar", 2500)
    sus(pg)
    pas("scadentar")                # a.1 («fără scadență în sistem»), f.2 («în termen»)

    # AC058 + AC061 + AC060: F1, Verificări, luna propusă la deschidere: rândul de sus, rândul Stocuri, rândul Intrastat (captura e a ferestrei de sus; aserțiunile se măsoară pe textul ferestrei)
    ecran(pg, F1, "fa-verificari", TOP + "#vf-prev")
    try:
        pg.wait_for_function("() => !((document.querySelector('.fereastra-overlay:not(.fundal) .fereastra') || {textContent: ''}).textContent.includes('Se verifică'))", timeout=25000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)
    sus(pg)
    pas("verificari")               # a.2 și a.3 pe răspunsuri reale
    intrastat_simulat(pg, pas)      # a.4, AC061
    stocuri_simulate(pg, pas)       # a.5, AC060

    # AC050: F1, Cartea mare, contul 371 ales în lista de conturi
    ecran(pg, F1, "fa-fisacont", TOP + "#fc-cont")
    try:
        pg.select_option(TOP + "#fc-cont", "371", timeout=10000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2500)
    sus(pg)
    pas("cartea_mare")              # a.6: opțiunea aleasă = «371 · Mărfuri»

    # AC041: F1, e-Transport, starea SPV citită la deschidere (acoperire «neconectat»)
    ecran(pg, F1, "fa-etransport", TOP + "#et-trimite")
    pg.wait_for_timeout(2500)
    pas("etransport")               # a.7: «Firma nu are drept SPV …»
