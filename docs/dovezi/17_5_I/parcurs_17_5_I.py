# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-I (texte), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026: pagina principală a cabinetului
(pasul implicit), ferestrele cabinetului (Sinteza zilei, Termene, Consolidare, Asistenți, Capacitate, meniul Activitate, Activitatea echipei, Tipare de erori),
apoi pe F1 Comert Stoc: Solicitări client, e-Transport, Registrul-inventar, Rapoarte comerciale, Produse, Istoric facturi (luna 10/2026, după «← luna»), Model factură, NIR nou,
Import date (meniul) și pasul Solduri inițiale, Bilanț anual, Declarații pasul 1, Leasing (tipul «Primire bun (financiar)» ales; apoi «Cod din catalog» = 2.3.2.1.1),
apoi pe F5 SRL Salariati: Salariați și Certificat nou (din fișa primului salariat › Concediu medical › «+ Certificat nou»). Pe fiecare pas se judecă texte: textul nou
există, textul vechi lipsește. Nu salvează nimic, nu alege niciun fișier; singurul câmp completat e «Cod din catalog» (cere serverului numai o citire, GET).
Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
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


def comuta_sef(pg):
    """Deschide secțiunea «Pentru șeful de cabinet» (cardurile Consolidare, Asistenți, Capacitate, Activitate stau în ea, pliată implicit); idempotent."""
    try:
        pg.evaluate("() => { const b = document.querySelector('.cab-grila > section.firme-grup .firme-grup-btn[aria-expanded=\"false\"]'); if (b) b.click(); }")
        pg.wait_for_selector("#fgc-sef:not([hidden])", state="attached", timeout=3000)
    except Exception:   # noqa: BLE001
        pass


def fereastra_cabinet(pg, cheie, asteapta=None, timp=2500):
    """Pagina principală › cardul `cheie` al cabinetului; se așteaptă fereastra (și, dacă e dat, selectorul `asteapta`)."""
    acasa(pg)
    comuta_sef(pg)
    try:
        pg.click(card(cheie), timeout=10000)
        pg.wait_for_selector(TOP + ".fereastra-corp", timeout=20000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
        pg.wait_for_function("() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); return f && !/se încarcă|Se încarcă/.test(f.innerText); }", timeout=20000)
    except Exception:   # noqa: BLE001 — pasul se judecă pe ce s-a desenat
        pass
    pg.wait_for_timeout(timp)


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


def apasa_text(pg, text, asteapta=None, timp=1500):
    """Clic pe primul buton al ferestrei de sus al cărui text conține `text`."""
    try:
        pg.locator(TOP + "button", has_text=text).first.click(timeout=10000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def ecran(pg, nume_firma, id_card, asteapta):
    firma(pg, nume_firma)
    intra(pg, id_card, asteapta)
    pg.wait_for_timeout(1500)


def fisa(pg):
    """F5 › Salariați (dacă luna ceasului nu are rânduri, «← luna» de cel mult 3 ori, ca docs/dovezi/17_1/parcurs_17_1.py) › primul salariat › fișa."""
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


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal» (aserțiunea probei contractului)
    fereastra_cabinet(pg, "brief", ".sa-cifra")
    pas("brief")                    # a.1, a.2: «1 sesizare nouă»
    fereastra_cabinet(pg, "termene", ".mig-intro")
    pas("termene")                  # a.3, f.2: introducerea Termene
    fereastra_cabinet(pg, "consolidare", ".pf-intro")
    pas("consolidare")              # a.4: «inclusiv (luna în curs»
    fereastra_cabinet(pg, "asistenti", ".asi-perm")
    pas("asistenti")                # a.5, a.6, f.3: drepturile în cuvinte
    fereastra_cabinet(pg, "capacitate", ".stare-goala")
    pas("capacitate")               # a.7, a.8: «Deschide Asistenți»
    fereastra_cabinet(pg, "activitate", "#opt-tipare")
    pas("activitate")               # f.4: meniul Activitate
    apasa(pg, "#opt-jurnal", ".fereastra-corp", 2500)
    pas("jurnal")                   # a.9: numele ferestrei «Activitatea echipei»
    fereastra_cabinet(pg, "activitate", "#opt-tipare")
    apasa(pg, "#opt-tipare", ".fereastra-corp", 2500)
    pas("tipare")                   # a.10: numele ferestrei «Tipare de erori»
    ecran(pg, F1, "fa-solicitari", TOP + "#sol-input")
    pas("solicitari")               # a.11, f.5
    ecran(pg, F1, "fa-etransport", TOP + "#et-tip")
    pas("etransport")               # a.12, a.13
    ecran(pg, F1, "fa-reginventar", TOP + "#ri-adauga")
    pas("reginventar")              # a.14, a.15, f.6
    ecran(pg, F1, "fa-rapoarte", TOP + "#r-carduri")
    pas("rapoarte")                 # a.16, a.17
    ecran(pg, F1, "fa-produse", TOP + ".pr-rand")
    pas("produse")                  # a.18, f.7
    ecran(pg, F1, "fa-facturi", TOP + "#fac-istoric")
    apasa(pg, "#fac-istoric", "#fac-prev", 2000)
    apasa(pg, "#fac-prev", ".fac-frand-btn", 2000)   # luna ceasului (11/2026) n-are facturi: «← luna» duce la 10/2026 (25 de facturi)
    pas("istoric")                  # a.19, a.20: «Arată încă 10 facturi ale lunii» (10/2026)
    ecran(pg, F1, "fa-facturi", TOP + "#fac-model")
    apasa(pg, "#fac-model", "#mf-preview", 2000)
    pas("model")                    # a.21, a.22: previzualizare
    ecran(pg, F1, "fa-stocuri", TOP + "#sn-toggle")
    apasa(pg, "#sn-toggle", "#sn-transport-cota", 2000)
    pas("nir")                      # a.23–a.25: cost accesoriu, TVA transport 0%
    ecran(pg, F1, "fa-import", TOP + "#mig-pasi")
    pas("import")                   # a.26, a.27: rândul «Solduri inițiale» al meniului
    apasa(pg, "#mig-pasi button.mig-frand[data-strat='solduri']", ".mig-intro", 2000)
    pas("solduri")                  # a.28, a.29: numele firmei și textul, pe un rând
    ecran(pg, F1, "fa-bilant", TOP + "#bl-tip")
    pas("bilant")                   # a.30: numele ferestrei «Bilanț anual»
    ecran(pg, F1, "fa-declaratii", TOP + "#dec-continua")
    pas("declaratii")               # a.31: «Completează: Tip declarație»
    ecran(pg, F1, "fa-operatiuni", TOP + "button[data-op='leasing']")
    apasa(pg, "button[data-op='leasing']", "#op-tip", 2000)
    apasa_text(pg, "Primire bun (financiar)", "#op-cod_catalog", 2000)
    pas("leasing")                  # a.32: «… și încă N câmpuri»
    try:
        pg.fill(TOP + "#op-cod_catalog", "2.3.2.1.1", timeout=10000)
        pg.dispatch_event(TOP + "#op-cod_catalog", "change")
        pg.wait_for_function("() => { const s = document.querySelector('.fereastra-overlay:not(.fundal) #op-cod_catalog-stare'); return s && s.textContent.trim().length > 0; }", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)
    pas("leasing_catalog")          # a.33, a.34: denumirea din catalog fără «în afară de» tăiat
    ecran(pg, F5, "fa-salariati", TOP + "#sp-contare")
    pas("salariati")                # a.35, a.36: h2 «Salariați»
    fisa(pg)
    apasa_text(pg, "Concediu medical", "#cm-nou", 2000)
    apasa(pg, "#cm-nou", "#cm-calc", 2500)
    pas("certificat")               # a.37, a.38: «Datele certificatului»
