# -*- coding: utf-8 -*-
"""Parcursul lotului 17.2 (poziția X07), cu contul administratorului (dovada.71507), 1366×768: pagina principală a cabinetului în starea ei implicită (secțiunea „Pentru șeful de cabinet” pliată), deschiderea și pliarea
secțiunii, lista Asistenților (nume-buton, „Editează”, fișa), „✕” acasă (secțiunea rămâne deschisă), reîncărcarea paginii (secțiunea revine pliată), Setări cont, Sinteza zilei și fișa primului salariat din F5 SRL Salariati SRL
(„+ Beneficiu”, „+ masă”, „←”). Nu salvează nimic. După fiecare pas predă pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas.
ATENȚIE: spre deosebire de e2e conftest.Ecran.acasa(), parcursul NU deschide secțiunea pliată și grupurile ferestrei firmei decât unde pasul o cere: starea implicită este chiar ce se măsoară. Pe commitul de bază
secțiunea și butoanele noi lipsesc: clicurile pe ele eșuează (înghițite), parcursul continuă, iar aserțiunile care le cer pică."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
BTN_SEF = ".cab-grila > section.firme-grup h3 > button.firme-grup-btn"
SEF_DESCHIS = "#fgc-sef:not([hidden])"
SEF_PLIAT = "#fgc-sef[hidden]"
NUME_FIRMA = "F5 SRL Salariati"


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


def x_acasa(pg):
    """„✕” (.nav-x, nav.acasa()) din fereastra de sus: pagina principală se redesenează (aceeași pagină, fără goto)."""
    pg.click(TOP + ".nav-x", timeout=10000)
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=20000)
    pg.wait_for_timeout(800)


def comuta_sef(pg, asteapta):
    """Clic pe titlul „Pentru șeful de cabinet” și așteptarea stării noi. Pe commitul de bază titlul nu există: clicul eșuează, parcursul continuă."""
    try:
        pg.click(BTN_SEF, timeout=3000)
        pg.wait_for_selector(asteapta, state="attached", timeout=3000)
    except Exception:   # noqa: BLE001
        pass


def deschide_card(pg, cheie, asteapta):
    pg.click(card(cheie), timeout=10000)
    pg.wait_for_selector(asteapta, timeout=20000)
    pg.wait_for_timeout(500)


def lista_asistenti(pg):
    """Din pagina principală: secțiunea deschisă (dacă există) și cardul Asistenți (în secțiune pe candidat, în grilă pe bază)."""
    comuta_sef(pg, SEF_DESCHIS)
    deschide_card(pg, "asistenti", "#asi-lista")
    pg.wait_for_selector(TOP + "#asi-lista > .val-card", timeout=20000)


def fisa_primului_asistent(pg):
    """Clic pe numele primului asistent activ ([data-act='vezi']: butonul-nume pe candidat, „Vizualizează” pe bază) și așteptarea fișei."""
    pg.locator(TOP + "#asi-lista > .val-card [data-act='vezi']").first.click(timeout=10000)
    pg.wait_for_selector(TOP + ".asi-nivel-badge", timeout=20000)
    pg.wait_for_timeout(500)


def editare_primului_asistent(pg):
    """„←” la listă, apoi „Editează” de pe rândul primului asistent activ."""
    pg.click(TOP + ".nav-inapoi", timeout=10000)
    pg.wait_for_selector(TOP + "#asi-lista > .val-card", timeout=20000)
    pg.locator(TOP + "#asi-lista > .val-card [data-act='edit']").first.click(timeout=10000)
    pg.wait_for_selector(TOP + "#asi-salveaza", timeout=20000)
    pg.wait_for_timeout(500)


def fisa_salariat(pg):
    """Pagina principală › Firme › Firme existente › F5 › (grupul „Personal și stocuri”, pliat implicit după 17.1) › Salariați › primul salariat din stat. Dacă luna curentă nu are rânduri, înapoi cu #sp-prev (cel mult 3 ori)."""
    pg.click(card("firme"), timeout=10000)
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
    pg.locator("#firme-lista button.firme-rand", has_text=NUME_FIRMA).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.evaluate("() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #fg-personal .firme-grup-btn[aria-expanded=\"false\"]'); if (b) b.click(); }")
    pg.wait_for_selector(TOP + "#fa-salariati", state="visible", timeout=20000)
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
    pg.wait_for_timeout(500)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                                    # 12 carduri, 6 sus + 6 în secțiunea pliată
    comuta_sef(pg, SEF_DESCHIS)
    pas("deschis")                                     # secțiunea deschisă
    comuta_sef(pg, SEF_PLIAT)
    pas("pliat")                                       # pliată din nou
    lista_asistenti(pg)                                # secțiunea rămâne deschisă (starea în memorie)
    pas("asistenti")                                   # lista Asistenților: fără „Vizualizează”, nume-buton, „Editează”
    fisa_primului_asistent(pg)
    pas("fisa_asi")
    editare_primului_asistent(pg)
    pas("editare")
    x_acasa(pg)
    pas("dupa_x")                                      # după „✕”: secțiunea a rămas deschisă
    acasa(pg)
    pas("dupa_goto")                                   # după reîncărcare: pliată
    deschide_card(pg, "setari", ".set-meniu")
    pas("setari")
    x_acasa(pg)
    deschide_card(pg, "brief", TOP + ".sa-cifra")
    pas("sinteza")
    x_acasa(pg)
    fisa_salariat(pg)
    pas("salariat")                                    # fișa: 13 copii directe, 19 butoane, meniurile pliate
    try:
        pg.click(TOP + "#ss-benef > summary", timeout=3000)
        pg.wait_for_selector(TOP + "#ss-benef[open]", state="attached", timeout=3000)
    except Exception:   # noqa: BLE001 — pe bază meniul nu există
        pass
    pas("benef")
    try:
        pg.click(TOP + "#ss-butoane [data-masa]", timeout=3000)
        pg.wait_for_selector(TOP + "#masa-input", timeout=20000)
    except Exception:   # noqa: BLE001 — pe bază butonul e vizibil direct; dacă și acolo eșuează, pasul pică
        pass
    pas("masa")
    try:
        pg.click(TOP + ".nav-inapoi", timeout=10000)
        pg.wait_for_selector(TOP + "#ss-butoane", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pas("inapoi")
