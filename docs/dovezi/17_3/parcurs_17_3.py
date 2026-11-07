# -*- coding: utf-8 -*-
"""Parcursul lotului 17.3 (text tăiat în tabelele DS, „Renunță” din bara de jos, antetul la 603 px), cu contul administratorului (dovada.71507): pagina principală la 1366×768, fereastra Control fiscal (tabelul firmelor),
fereastra Setări cont › Schimbă parola (fereastră cu formular și „←” activ), apoi, după schimbarea rezoluției la 603×590 și reîncărcarea paginii, Control fiscal și Firme existente. Nu salvează nimic (în „Schimbă parola” nu se
scrie nimic și nu se apasă butonul). După fiecare pas predă pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas.
ATENȚIE: rezoluția se schimbă ÎNAINTE de reîncărcarea paginii, iar fereastra se deschide după reîncărcare: indiciul căutării („Caută” sub 700 px) se pune la crearea ferestrei. Pe commitul de bază aserțiunile lotului pică, parcursul continuă."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
TABEL_CONTROL = TOP + "#cf-lista .ds-tabel tbody tr"


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


def deschide_card(pg, cheie, asteapta):
    pg.click(card(cheie), timeout=10000)
    try:
        pg.wait_for_selector(asteapta, timeout=30000)
    except Exception:   # noqa: BLE001 — ecranul n-a desenat ce se aștepta: pasul se judecă pe ce s-a desenat (aserțiunile pică, parcursul continuă)
        pass
    pg.wait_for_timeout(500)


def control_fiscal(pg):
    """Din pagina principală: cardul Control fiscal și așteptarea tabelului firmelor."""
    deschide_card(pg, "control", TABEL_CONTROL)


def setari_parola(pg):
    """Din pagina principală: cardul Setări cont, apoi intrarea „Schimbă parola” (câmpurile rămân goale)."""
    deschide_card(pg, "setari", ".set-meniu")
    pg.locator(TOP + ".set-meniu button", has_text="Schimbă parola").first.click(timeout=10000)
    pg.wait_for_selector(TOP + "#set-pv", timeout=20000)
    pg.wait_for_timeout(500)


def firme_existente(pg):
    """Din pagina principală: cardul Firme › Firme existente și așteptarea rândurilor listei."""
    pg.click(card("firme"), timeout=10000)
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    try:
        pg.wait_for_selector(TOP + "#firme-lista button.firme-rand", timeout=30000)
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
    pas("implicit")                                    # 12 carduri (aserțiunea probei contractului)
    control_fiscal(pg)
    pas("control")                                     # tabelul DS la 1366×768: text rupt pe linii, nu tăiat cu „…”
    acasa(pg)
    setari_parola(pg)
    pas("parola")                                      # fereastră cu formular și „←” activ: bara de jos fără „Renunță”
    pg.set_viewport_size({"width": 603, "height": 590})
    acasa(pg)                                          # reîncărcare la rezoluția nouă: antetul și căutarea se desenează la 603 px
    control_fiscal(pg)
    pas("control603")                                  # tabel, cale și căutare în antet
    acasa(pg)
    firme_existente(pg)
    pas("firme603")                                    # Firme existente: rânduri care urmează conținutul
