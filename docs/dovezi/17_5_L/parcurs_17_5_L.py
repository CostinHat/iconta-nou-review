# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-L (portalul clientului), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală a cabinetului, apoi Firme › Firme existente › F1 Comert Stoc › Acces client › «Previzualizează portalul» (tab NOU al portalului clientului firmei F1: token emis de
POST /tenants/{id}/acces-portal, main.py:2133 și core/uc_tenants.py:146; butonul #ac-btn-preview, static/js/ecrane/firme.js: ecranAccesClient, `window.open`). Pașii se judecă pe TABUL de previzualizare
(pagina lui e cea predată oracolului, nu cea a cabinetului):
  start_portal    ecranul de start al portalului (cardurile): f.1 «Acces cont», a.3 «Fotografiază bon sau chitanță», a.4 «Mesaje către contabil», f.2 «Declarații depuse»;
  istoric_portal  Facturi › Istoric facturi, în același tab: a.5 și a.6 («Export SAGA lună» și «Export WinMentor lună» lipsesc).
Nu salvează nimic, nu alege niciun fișier; previzualizarea refuză orice mutație (main.py:720–733). Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile a. pică).
Dacă tabul de previzualizare nu se deschide, f.1 se judecă pe pagina cabinetului și PICĂ (nu trece pe nimic); dacă fereastra «Istoric facturi» nu se deschide, pasul istoric_portal NU se predă oracolului
(un «lipsește» pe un ecran neatins ar trece fără sens). Importă numai biblioteca standard și verifica_pas."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc"
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
JS_STATUS_GATA = "() => { const s = document.querySelector('#pa-status'); return !!s && !s.textContent.includes('Se verifică'); }"
JS_PREVIZ_GATA = ("() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #ac-btn-preview'); const l = document.querySelector('.fereastra-overlay:not(.fundal) #ac-lista');"
                  " return !!b && !b.disabled && !!l && !l.textContent.includes('Se încarcă'); }")


def acasa(pg):
    """Pagina principală a cabinetului, proaspătă (goto): memoria ferestrei deschise se șterge întâi; se așteaptă cardurile și sintezele lor."""
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
        pg.click("button.cab-card:has([data-cheie='firme'])", timeout=10000)
        pg.wait_for_selector("#opt-existente", timeout=20000)
        pg.click("#opt-existente")
        pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
        pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
        pg.wait_for_selector("#fa-facturi", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(400)


def previzualizare(pg):
    """Firma F1 › Acces client › «Previzualizează portalul»: tabul NOU (`context.expect_page`) al portalului clientului, așteptat până la cardurile ecranului de start. -> pagina tabului sau None (două încercări)."""
    for _incercare in range(2):
        firma(pg, F1)
        try:
            pg.evaluate(JS_DESCHIDE_CARD, "#fa-acces")
            pg.click(TOP + "#fa-acces", timeout=10000)
            pg.wait_for_selector(TOP + "#ac-btn-preview", timeout=20000)
            pg.wait_for_function(JS_PREVIZ_GATA, timeout=20000)
            with pg.context.expect_page(timeout=30000) as fila:
                pg.click(TOP + "#ac-btn-preview", timeout=10000)
            tab = fila.value
            tab.wait_for_load_state("domcontentloaded", timeout=30000)
            tab.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
            try:
                tab.wait_for_function(JS_STATUS_GATA, timeout=20000)
            except Exception:   # noqa: BLE001 — situația ANAF întârzie: pasul se judecă pe cardurile desenate
                pass
            tab.wait_for_timeout(800)
            return tab
        except Exception:   # noqa: BLE001
            continue
    return None


def istoric_facturi(tab):
    """În tabul de previzualizare: cardul «Facturi» › «Istoric facturi» (#fac-istoric); fereastra e atinsă numai dacă apare #fac-prev (antetul lunii). -> True/False."""
    try:
        tab.locator(".cab-card-titlu", has_text="Facturi").first.click(timeout=10000)
        tab.wait_for_selector(TOP + "#fac-istoric", timeout=20000)
        tab.click(TOP + "#fac-istoric", timeout=10000)
        tab.wait_for_selector(TOP + "#fac-prev", state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        return False
    tab.wait_for_timeout(2000)   # a doua cerere a listei (luna cu facturi) se așază înainte de captură
    return True


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(unde, nume):
        unde.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(unde, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    tab = previzualizare(pg)
    try:
        if tab is None:
            raise AssertionError("Previzualizarea portalului F1 nu s-a deschis")
        pas(tab, "start_portal")            # f.1 (aserțiunea probei contractului), a.3, a.4, f.2: textul ecranului de start al portalului
        if tab is not None and istoric_facturi(tab):
            pas(tab, "istoric_portal")            # a.5, a.6: lipsesc «Export SAGA lună» și «Export WinMentor lună»
        else:
            raise AssertionError("Istoric facturi nu s-a deschis; absențele nu pot fi evaluate")
    finally:
        if tab is not None:
            try:
                tab.close()
            except Exception:   # noqa: BLE001
                pass
