# -*- coding: utf-8 -*-
"""Parcursul lotului 17.1 (poziția X06, meniul firmei), cu contul administratorului (dovada.71507), 1366×768: fereastra firmei F1 (SRL, partidă dublă) în starea ei implicită, deschiderea și pliarea
grupului „Contabilitate”, redeschiderea ferestrei după reîncărcarea paginii, fereastra firmei F4 PFA Sistem Real (partidă simplă), meniul „Firme”, lista „Firme existente” și, la sfârșit, trei pași fără reîncărcare: aceeași firmă redeschisă după „←” (h), apoi după „✕” (k), intrare într-un card și „←” (i), altă firmă (j); apoi, cu pagina de 603 × 590 px (panoul observației arhitectului, 788 și 790), „Firme existente” (m) și fereastra firmei F1 (n). Nu salvează nimic.
După fiecare pas predă pagina oracolului (verifica_pas.verifica_pagina). Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas.
ATENȚIE: spre deosebire de parcurs_16_8.py, `firma()` NU deschide grupurile pliate: starea implicită (numai „Zi de zi” deschis) este chiar ce se măsoară. Așteptarea de după deschiderea ferestrei
folosește #fa-facturi (cardul din grupul deschis implicit), nu #fa-jurnal (grupul „Contabilitate” e pliat și deci nevizibil)."""
import verifica_pas as VP

BTN_CONTABILITATE = ".fereastra-overlay:not(.fundal) #fg-contabilitate .firme-grup-btn"


def _la_meniul_firme(pg):
    """Din parcurs_16_8.py (_cabinet): memoria ferestrei deschise se șterge întâi; dacă cabinetul nu răspunde la clic, pagina se reîncarcă, de cel mult trei ori. Se oprește în meniul „Firme”."""
    for incercare in range(3):
        try:
            pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
            pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
            pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
            pg.wait_for_timeout(800)
            pg.click("button.cab-card:has([data-cheie='firme'])", timeout=10000)
            break
        except Exception:   # noqa: BLE001
            if incercare == 2:
                raise
            pg.reload(wait_until="domcontentloaded")
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.wait_for_timeout(600)


def firma(pg, nume="F1 Comert Stoc"):
    """Fereastra firmei `nume`, pornită de la cabinet, în starea implicită a grupurilor; așteaptă cardul din grupul deschis implicit."""
    _la_meniul_firme(pg)
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.wait_for_timeout(500)


def _comuta(pg, asteapta):
    """Clic pe titlul „Contabilitate” și așteptarea stării noi. Pe commitul de bază titlul nu e un buton: clicul eșuează, parcursul continuă (pasii b, c, d pică pe bază, ca dovadă a defectului)."""
    try:
        pg.click(BTN_CONTABILITATE, timeout=3000)
        pg.wait_for_selector(asteapta, state="attached", timeout=3000)
    except Exception:   # noqa: BLE001
        pass


def _deschide_din_lista(pg, nume):
    """Din lista „Firme existente” (pagina rămâne aceeași, fără goto) deschide fereastra firmei `nume`."""
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.wait_for_timeout(500)


def _inapoi_la_lista(pg):
    """„←” de pe fereastra firmei (a treia fereastră: cabinet › Firme › Firme existente › firma; navigator.js _areInapoiReal, stiva.length > 1; e2e_lot15_e5.py:40–47 o măsoară 40 × 40): înapoi la lista „Firme existente”."""
    pg.click(".fereastra-overlay:not(.fundal) .nav-inapoi", timeout=10000)
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)


def _inchide_si_la_lista(pg):
    """„✕” (.nav-x, nav.acasa()) duce acasă, la cabinet; de acolo, fără goto, Firme › Firme existente (aceeași pagină, același modul firme.js)."""
    pg.click(".fereastra-overlay:not(.fundal) .nav-x", timeout=10000)
    pg.wait_for_selector("button.cab-card:has([data-cheie='firme'])", timeout=20000)
    pg.click("button.cab-card:has([data-cheie='firme'])", timeout=10000)
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)


def pastreaza_starea(pg, nume="F1 Comert Stoc"):
    """Pasul h: „Contabilitate” deschis, „←” de pe fereastra firmei la lista „Firme existente”, aceeași firmă redeschisă din rândul listei, fără reîncărcare. Pe commitul de bază clicul pe titlu eșuează (_comuta îl înghite) și pasul h pică."""
    _deschide_din_lista(pg, nume)
    _comuta(pg, ".fereastra-overlay:not(.fundal) #fgc-contabilitate:not([hidden])")
    _inapoi_la_lista(pg)
    _deschide_din_lista(pg, nume)


def intra_in_card_si_inapoi(pg):
    """Pasul i: din „Contabilitate” deschis, intrare în cardul Registru jurnal (fereastra firmei dispare din DOM) și „←”; fereastra firmei se redesenează."""
    pg.click(".fereastra-overlay:not(.fundal) #fa-jurnal", timeout=10000)
    pg.wait_for_selector("#fa-facturi", state="detached", timeout=20000)
    pg.wait_for_timeout(700)
    pg.click(".fereastra-overlay:not(.fundal) .nav-inapoi", timeout=10000)
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.wait_for_timeout(500)


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    firma(pg)
    pas("a")                                           # F1: 7 grupuri, 37 de carduri, deschis numai „Zi de zi”
    _comuta(pg, ".fereastra-overlay:not(.fundal) #fgc-contabilitate:not([hidden])")
    pas("b")                                           # „Contabilitate” deschis
    _comuta(pg, ".fereastra-overlay:not(.fundal) #fgc-contabilitate[hidden]")
    pas("c")                                           # „Contabilitate” pliat din nou
    _comuta(pg, ".fereastra-overlay:not(.fundal) #fgc-contabilitate:not([hidden])")   # îl las deschis și reîncarc (goto): starea se resetează
    firma(pg)
    pas("d")
    firma(pg, "F4 PFA Sistem Real")
    pas("e")                                           # F4: 7 grupuri, 27 de carduri
    _la_meniul_firme(pg)
    pas("f")                                           # meniul „Firme”: o singură intrare „Migrare cabinet”
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-adauga", timeout=20000)
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)   # lista a venit de la server (788: înălțimea ei se măsoară cu rândurile desenate)
    pg.wait_for_timeout(700)
    pas("g")                                           # „Firme existente”: fără „Import în masă (CSV)”
    pastreaza_starea(pg)
    pas("h")                                           # F1 redeschisă din listă după „←”, fără reîncărcare: „Contabilitate” a rămas deschis
    intra_in_card_si_inapoi(pg)
    pas("i")                                           # după intrarea într-un card și „←”: „Contabilitate” a rămas deschis
    _inchide_si_la_lista(pg)   # (k) „✕” + cabinet › Firme › Firme existente › aceeași firmă
    _deschide_din_lista(pg, "F1 Comert Stoc")
    pas("k")                                           # după „✕” și redeschidere, aceeași firmă: „Contabilitate” a rămas deschis
    _inapoi_la_lista(pg)
    _deschide_din_lista(pg, "F4 PFA Sistem Real")
    pas("j")                                           # altă firmă (după „←”), fără reîncărcare: numai „Zi de zi” deschis
    # 788 și 790: aceleași ferestre în pagina de 603 × 590 px (innerWidth × innerHeight măsurate de arhitect pe iconta.eu)
    try:
        pg.set_viewport_size({"width": 603, "height": 590})
        _la_meniul_firme(pg)
        pg.click("#opt-existente")
        pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
        pg.wait_for_timeout(700)
        pas("m")                                       # „Firme existente” în pagina de 603 × 590 px: lista singurul loc de derulare; „←” și „✕” de aceeași lățime
        _deschide_din_lista(pg, "F1 Comert Stoc")
        pas("n")                                       # fereastra firmei F1 în pagina de 603 px: „←” și „✕” de aceeași lățime
    finally:
        pg.set_viewport_size({"width": 1366, "height": 768})
