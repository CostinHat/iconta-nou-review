# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5, cu contul administratorului (dovada.71507), 1366×768: acțiunile din rândurile ecranelor martor (Plan de conturi, Clienți, Casă, Produse), bara de jos la Tipare de erori și la Fișa salariatului, eticheta câmpului de profit din D104 și acțiunea principală din Setări › Schimbă parola. Nu salvează nimic. După fiecare ecran predă pagina oracolului
(verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas.
ATENȚIE: fiecare ecran se deschide de la zero (pagina principală reîncărcată, apoi drumul contabilului până la ecran), ca un ecran care nu se deschide să nu strice pașii următori. Un clic care eșuează e înghițit,
iar parcursul continuă: aserțiunile pasului judecă ce s-a desenat (pe commitul de bază meniul „Acțiuni” lipsește la Plan de conturi, Casă și Produse, deci aserțiunile lor pică)."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
BTN_SEF = ".cab-grila > section.firme-grup h3 > button.firme-grup-btn"
SEF_DESCHIS = "#fgc-sef:not([hidden])"
PRINCIPAL = TOP + ".fereastra-jos [data-actiune-principala]"
F1, F5 = "F1 Comert Stoc", "F5 SRL Salariati"


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
    """Pagina principală › Firme › Firme existente › firma `nume`, cu toate grupurile ferestrei ei deschise (grupurile sunt pliate implicit)."""
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
    """Clic pe cardul `id_card` din fereastra firmei și așteptarea ecranului."""
    pg.click(TOP + "#" + id_card, timeout=10000)
    pg.wait_for_selector(asteapta, state="attached", timeout=30000)
    pg.wait_for_timeout(600)


def asteapta_principal(pg):
    """Bara de jos și-a pus acțiunea principală (pe bază sau pe candidat); dacă nu apare, pasul se judecă pe ce există."""
    try:
        pg.wait_for_selector(PRINCIPAL, state="attached", timeout=8000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(500)


def comuta_sef(pg):
    """Deschide secțiunea „Pentru șeful de cabinet” (cardul Activitate stă în ea); idempotent."""
    try:
        pg.evaluate("() => { const b = document.querySelector('.cab-grila > section.firme-grup .firme-grup-btn[aria-expanded=\"false\"]'); if (b) b.click(); }")
        pg.wait_for_selector(SEF_DESCHIS, state="attached", timeout=3000)
    except Exception:   # noqa: BLE001
        pass


def ecran_plan(pg):
    firma(pg, F1)
    intra(pg, "fa-planconturi", TOP + "#pcf-lista .pf-frand")


def ecran_clienti(pg):
    firma(pg, F1)
    intra(pg, "fa-clienti", TOP + "#cl-tabel")


def ecran_casa(pg):
    """Casă se deschide pe luna ceasului înghețat (noiembrie 2026, fără operațiuni); operațiunile de test sunt din octombrie: „← luna” până apare tabelul (cel mult de 3 ori)."""
    firma(pg, F1)
    intra(pg, "fa-casa", TOP + "#c-prev")
    for _ in range(3):
        if pg.query_selector(TOP + "#c-tabel"):
            break
        pg.click(TOP + "#c-prev", timeout=5000)
        pg.wait_for_timeout(1500)
    pg.wait_for_selector(TOP + "#c-tabel", state="attached", timeout=15000)


def ecran_produse(pg):
    firma(pg, F1)
    intra(pg, "fa-produse", TOP + "#pr-lista .pr-rand")


def ecran_tipare(pg):
    acasa(pg)
    comuta_sef(pg)
    pg.click(card("activitate"), timeout=10000)
    pg.wait_for_selector("#opt-tipare", timeout=20000)
    pg.click("#opt-tipare")
    pg.wait_for_selector(TOP + ".tip-ecran", state="attached", timeout=30000)
    asteapta_principal(pg)


def ecran_salariat(pg):
    """F5 › Salariați › primul salariat din stat. Dacă luna curentă nu are rânduri, înapoi cu #sp-prev (cel mult 3 ori)."""
    firma(pg, F5)
    pg.click(TOP + "#fa-salariati", timeout=10000)
    pg.wait_for_selector(TOP + "#sp-contare", timeout=30000)
    for incercare in range(4):
        try:
            pg.wait_for_selector(TOP + "#sp-tabel tbody tr.sp-rand", timeout=12000)
            break
        except Exception:   # noqa: BLE001
            if incercare == 3:
                raise
            pg.click(TOP + "#sp-prev", timeout=5000)
            pg.wait_for_timeout(1500)
    pg.locator(TOP + "#sp-tabel tbody tr.sp-rand").first.locator(".sp-deschide").click()
    pg.wait_for_selector(TOP + "#ss-butoane", timeout=30000)
    asteapta_principal(pg)


def ecran_d104(pg):
    """F1 › Declarații › D104 › „Continuă” (pasul 2, unde stă câmpul de profit sau pierdere)."""
    firma(pg, F1)
    intra(pg, "fa-declaratii", TOP + "li.ds-lista-rand")
    pg.locator(TOP + "li.ds-lista-rand", has_text="D104").first.click(timeout=10000)
    pg.wait_for_selector(TOP + "#dec-continua", timeout=20000)
    pg.click(TOP + "#dec-continua", timeout=10000)
    pg.wait_for_selector(TOP + "#d104-profit", state="attached", timeout=20000)
    pg.wait_for_timeout(500)


def ecran_parola(pg):
    acasa(pg)
    pg.click(card("setari"), timeout=10000)
    pg.wait_for_selector(".set-meniu", timeout=20000)
    pg.locator(TOP + "button.meniu-card", has_text="Schimbă parola").first.click(timeout=10000)
    pg.wait_for_selector(TOP + "#set-pv", state="attached", timeout=20000)
    asteapta_principal(pg)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume, deschide):
        try:
            deschide(pg)
        except Exception as e:   # noqa: BLE001 — ecranul nu s-a deschis: aserțiunile pasului se judecă pe ce e în pagină (neexecutat sau pică, cu motiv)
            print("[parcurs] ecranul %s nu s-a deschis complet: %s: %s" % (nume, type(e).__name__, str(e).splitlines()[0][:200]))
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    pas("plan", ecran_plan)            # Plan de conturi: o acțiune vizibilă + meniul „Acțiuni”, Șterge în meniu
    pas("clienti", ecran_clienti)      # Clienți: meniul „Acțiuni” (există deja)
    pas("casa", ecran_casa)            # Casă: Șterge în meniu
    pas("produse", ecran_produse)      # Produse: „×” de ștergere în meniu
    pas("tipare", ecran_tipare)        # Tipare de erori: exact o acțiune principală în bară
    pas("salariat", ecran_salariat)    # Fișa salariatului: principalul nu e „Descarcă PDF”
    pas("d104", ecran_d104)            # D104: eticheta „Profit(+)/pierdere(-)”
    pas("parola", ecran_parola)        # Setări › Schimbă parola: acțiunea principală în bară
