# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-J (declarațiile pasul 2 și Certificatul CM cu datele din aplicație), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului (pasul implicit), apoi Registrul de evidență fiscală pe F6 Migrare Test (anul 2025 propus, cardul de eroare) și pe F1 Comert Stoc (regim micro),
Declarații pasul 1 pe F1 (lista «Tip declarație»: rândul D177 atins; rândul «D300 · 10/2026»; D398), Declarații deschise din căutarea globală («D104»), pasul 2 al D114 și al D104 pe F1,
pasul 2 al D301 pe F3 Intracomunitar (perioada 06/2026) și Certificat nou pe F5 SRL Salariati (fișa lui Ionescu Vasile › Concediu medical › «+ Certificat nou», Data început 19.10.2026).
Pe fiecare pas se judecă texte sau valori de câmp: textul / valoarea nouă există, textul vechi lipsește. Nu salvează nimic, nu alege niciun fișier; singurele câmpuri completate sunt cele numite mai jos
(căsuța de căutare, anul și luna perioadei D301, Data început a certificatului), iar la certificat ciorna formularului poate fi păstrată pe server (mecanismul formularelor lungi), fără a se salva certificatul.
Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc"
F3 = "F3 Intracomunitar"
F5 = "F5 SRL Salariati"
F6 = "F6 Migrare Test"


def card(cheie):
    return "button.cab-card:has([data-cheie='%s'])" % cheie


def acasa(pg):
    """Pagina principală proaspătă (goto): memoria ferestrei deschise se șterge întâi; se așteaptă cardurile și sintezele lor (nimic „se încarcă”)."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    try:
        pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    except Exception:   # noqa: BLE001 — [17.11.2026, arhitect] Chromium headless: net::ERR_INSUFFICIENT_RESOURCES la încărcarea modulelor
        # JS imediat după o navigare (intermitent, 4 din 8 rulări pe main aabc1f31, pagina rămâne goală); o singură reîncărcare, apoi aceeași așteptare
        print("[parcurs] pagina principală goală după navigare: o reîncărcare")
        pg.wait_for_timeout(2000)
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


def rand_lista(pg, text, timp=1000):
    """Clic pe primul rând al listei «Tip declarație» (li.ds-lista-rand) al cărui text conține `text` (un rând inactiv își deschide motivul; unul activ se alege)."""
    try:
        pg.locator(TOP + "li.ds-lista-rand", has_text=text).first.click(timeout=10000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def la_pasul_2(pg, asteapta, timp=1800):
    """«Continuă →» din pasul 1 al Declarațiilor, apoi așteptarea unui element al pasului 2."""
    try:
        pg.click(TOP + "#dec-continua", timeout=10000)
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def centreaza(pg, selector):
    """Aduce elementul în mijlocul zonei vizibile (captura de 1366×768 îl arată); înghițit dacă lipsește."""
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


def text_ferestrei(pg):
    try:
        return pg.evaluate("() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return f ? (f.textContent || '') : ''; }")
    except Exception:   # noqa: BLE001
        return ""


def fisa(pg):
    """F5 › Salariați (dacă luna ceasului nu are rânduri, «← luna» de cel mult 3 ori, ca docs/dovezi/17_1/parcurs_17_1.py) › rândul lui Ionescu (altfel primul rând) › fișa."""
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
        randuri = pg.locator(TOP + "#sp-tabel tbody tr.sp-rand")
        rand = randuri.filter(has_text="Ionescu")
        (rand if rand.count() else randuri).first.locator(".sp-deschide").click(timeout=10000)
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

    # AC052: F6 (profit), registrul pe 2025 — cauza refuzului și butonul «Deschide Import date»
    ecran(pg, F6, "fa-regfiscal", TOP + "#rf-an")
    pg.wait_for_timeout(2500)
    if "Deschide Import date" not in text_ferestrei(pg):   # butonul poate sta în cardul de eroare deschis (fereastra lui), nu pe fereastra registrului
        apasa(pg, "#rf-carduri button[data-card='eroare']", ".fereastra-corp", 2500)
    pas("registru_import")          # a.1: «Deschide Import date»

    # AC053: F1 (micro), registrul pe varianta pornită: nota regimului
    ecran(pg, F1, "fa-regfiscal", TOP + "#rf-an")
    pg.wait_for_timeout(2500)
    sus(pg)
    pas("registru_micro")           # a.2: nota «Firma e pe impozitul pe veniturile microîntreprinderilor …»

    # AC135 + f.2: F1, Declarații pasul 1, rândul D177 atins (inactiv: își deschide motivul)
    ecran(pg, F1, "fa-declaratii", TOP + "#dec-continua")
    rand_lista(pg, "D177", 1200)
    centreaza(pg, ".ds-lista-detalii:not([hidden])")
    pas("lista_tip")                # a.3 (textul D177), f.2 («Continuă →»)

    # AC103: F1, rândul «D300 · 10/2026»: luna perioadei = luna rândului
    ecran(pg, F1, "fa-declaratii", TOP + "#dec-continua")
    rand_lista(pg, "D300 · 10/2026", 1200)
    centreaza(pg, "#dec-luna")
    pas("perioada_d300")            # f.3: «octombrie»

    # AC129: F1, căutarea globală «D104» (căsuța din bara ferestrei firmei) → Declarații cu D104; trimestrul propus
    firma(pg, F1)
    try:
        pg.fill(TOP + "#cautare-fereastra", "D104", timeout=10000)
        pg.wait_for_selector(TOP + "#cautare-fereastra-rez .cautare-item", timeout=15000)
        pg.locator(TOP + "#cautare-fereastra-rez .cautare-item", has_text="D104 —").first.click(timeout=10000)
        pg.wait_for_selector(TOP + "#dec-trim", state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)
    centreaza(pg, "#dec-trim")
    pas("cautare_d104")             # a.5: «T3 (iul-sep)»

    # AC134: F1, D114 pasul 2: CIF declarant precompletat
    ecran(pg, F1, "fa-declaratii", TOP + "#dec-continua")
    rand_lista(pg, "D114", 1000)
    la_pasul_2(pg, "#d114-cif")
    centreaza(pg, "#d114-cif")
    pas("d114")                     # a.6: #d114-cif = 401002001

    # AC137: F1, D398 aleasă (de lămurit): butonul «Deschide Date firmă»
    ecran(pg, F1, "fa-declaratii", TOP + "#dec-continua")
    rand_lista(pg, "D398", 1200)
    pas("d398")                     # a.7: «Deschide Date firmă»

    # AC130: F1, D104 pasul 2: nota asociatului desemnat
    ecran(pg, F1, "fa-declaratii", TOP + "#dec-continua")
    rand_lista(pg, "D104", 1000)
    la_pasul_2(pg, "#d104-dnume")
    sus(pg)
    pas("d104")                     # a.8: nota «D104 se depune de asociatul desemnat …»

    # AC139 + AC141: F3, D301 pasul 2 pe 06/2026 (rândul «D301 · 06/2026»; anul și luna se pun apoi explicit: pe bază alegerea rândului duce la prima perioadă D301)
    ecran(pg, F3, "fa-declaratii", TOP + "#dec-continua")
    rand_lista(pg, "D301", 1000)
    try:
        pg.fill(TOP + "#dec-an", "2026", timeout=10000)
        pg.dispatch_event(TOP + "#dec-an", "change")
        pg.select_option(TOP + "#dec-luna", "6", timeout=10000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(600)
    la_pasul_2(pg, "#d301-regen", 2500)
    sus(pg)
    # [16.11.2026, arhitect] a.8: zona mesajelor pasului 2 în cadru, ca avertismentul (dacă există) să fie în captură
    pg.evaluate("""() => { const r = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!r) return;
        const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); let tinta = null, rez = null;
        while (w.nextNode()) { const x = w.currentNode.textContent;
            if (!tinta && x.includes('din facturi')) tinta = w.currentNode.parentElement;
            if (!rez && x.trim() === 'Rezumat') rez = w.currentNode.parentElement; }
        const e = tinta || rez; if (e) e.scrollIntoView({block: 'center'}); }""")
    pg.wait_for_timeout(400)
    pas("d301_avert")               # a.8: lipsește «nu automat din facturi»
    sus(pg)                         # [16.11.2026, arhitect] înapoi sus după a.8, ca rândul «Adaugă operațiune» să fie în cadru
    centreaza(pg, "#d301-valuta")
    pas("d301_valuta")              # a.9: Valută = EUR

    # AC109: F5, fișa lui Ionescu › Concediu medical › «+ Certificat nou», Data început 19.10.2026
    fisa(pg)
    apasa_text(pg, "Concediu medical", "#cm-nou", 2000)
    apasa(pg, "#cm-nou", "#cm-calc", 2500)
    try:
        pg.fill(TOP + "#cm-inceput", "2026-10-19", timeout=10000)
        pg.dispatch_event(TOP + "#cm-inceput", "change")
        pg.wait_for_function("() => (document.querySelector('.fereastra-overlay:not(.fundal) .fereastra') || {textContent: ''}).textContent.includes('Propus din statele de plată')", timeout=12000)
    except Exception:   # noqa: BLE001 — pe baza lotului propunerea nu apare
        pass
    pg.wait_for_timeout(1500)
    centreaza(pg, "#cm-zile6")
    pas("cm")                       # a.10 (propoziția), a.11 (#cm-zile6 = 127)
