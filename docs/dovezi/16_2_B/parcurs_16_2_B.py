# -*- coding: utf-8 -*-
"""Parcursul comenzii 16.2-B (scenariul F017, Casă › Dispoziție nouă › Încasare client, pe F1 Comert Stoc SRL): acțiunile pașilor a)–j), executate ca un contabil, apoi pagina vie se predă oracolului
(verifica_pas.verifica_pagina) după fiecare pas. Nu compară nimic și nu scrie verdicte. Importă numai playwright, biblioteca standard și verifica_pas (regula lansatorului).
PARCURS_PASI=a,b,... (variabilă de mediu) alege pașii rulați; implicit toți, în ordinea PASI. Pașii „c-ro”, „e-98” și „j-refuz” sunt momente ale aceluiași pas din scenariu (c: aceeași listă cu RO în fața CUI-ului;
e-98: firma F5 fără serie; j: refuzul plății), cu aserțiunile lor în pasi.json. După pasul e-98 fereastra lui F1 e refăcută (schimbarea firmei o închide)."""
import os

import verifica_pas as VP

PASI = ("a", "b", "c", "c-ro", "d", "e", "e-98", "f", "g", "h", "i", "i-tva", "j", "j-refuz")
BUT_TIP = ".alegere-butoane:has(+ #c-cat) button[data-valoare=\"%s\"]"


def _cabinet(pg):
    """Din cabinet: memoria ferestrei deschise (restaurare.js) se șterge întâi, ca pasul să înceapă din cabinet; dacă cabinetul nu răspunde la clic, pagina se reîncarcă și pasul se reia, de cel mult trei ori."""
    for incercare in range(3):
        try:
            pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
            pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
            pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
            pg.wait_for_timeout(800)
            pg.click("button.cab-card:has([data-cheie='firme'])", timeout=10000)
            break
        except Exception:   # noqa: BLE001 — se reia de la începutul cabinetului
            if incercare == 2:
                raise
            pg.reload(wait_until="domcontentloaded")
    pg.wait_for_timeout(600)
    if pg.query_selector("#opt-existente"):
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)


def _firma(pg, nume, buton):
    """Cabinet › Firme › firma `nume` › butonul ei (#fa-casa, #fa-facturi, #fa-jurnal)."""
    _cabinet(pg)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector(buton, timeout=20000)
    pg.click(buton)


def _casa(pg, nume="F1 Comert Stoc"):
    _firma(pg, nume, "#fa-casa")
    pg.wait_for_selector("#c-sold-inceput", timeout=20000)


def _dispozitie(pg):
    pg.click("#c-toggle")
    pg.wait_for_selector("#c-adauga", timeout=20000)


def _incasare(pg, cui):
    pg.click(BUT_TIP % "incasare_client")
    pg.fill("#c-cui", cui)
    pg.dispatch_event("#c-cui", "change")
    pg.wait_for_timeout(2000)


def _incasare_f1a18(pg):
    """F1 › Casă › Dispoziție nouă › Încasare client › 410001005 › bifa F1A18."""
    _casa(pg)
    _dispozitie(pg)
    _incasare(pg, "410001005")
    pg.locator("#c-facturi label:has-text('F1A nr. 18') input[data-cf]").check(timeout=10000)
    pg.wait_for_timeout(1200)


def _pas_a(pg, ctx):
    _casa(pg)


def _pas_b(pg, ctx):
    _dispozitie(pg)


def _pas_c(pg, ctx):
    _incasare(pg, "410001005")
    print("[format] lista pozițiilor: %r" % pg.evaluate("document.querySelector('#c-facturi') && document.querySelector('#c-facturi').innerText"))


def _pas_c_ro(pg, ctx):
    pg.fill("#c-cui", "RO410001005")
    pg.dispatch_event("#c-cui", "change")
    pg.wait_for_timeout(2000)


def _pas_d(pg, ctx):
    pg.fill("#c-cui", "410001005")
    pg.dispatch_event("#c-cui", "change")
    pg.wait_for_timeout(2000)
    pg.locator("#c-facturi label:has-text('F1A nr. 18') input[data-cf]").check(timeout=10000)
    pg.wait_for_timeout(1200)


def _pas_e(pg, ctx):
    pass   # starea butonului „Adaugă” după partener + poziție bifată, fără altă acțiune


def _pas_e98(pg, ctx):
    """F5 SRL Salariati (fără serie de chitanțe): Încasare client, CUI 410001005, „Avans, fără factură” bifat, suma 100, Adaugă."""
    _casa(pg, "F5 SRL Salariati")
    _dispozitie(pg)
    _incasare(pg, "410001005")
    pg.locator("#c-avans").check(timeout=10000)
    pg.fill("#c-suma", "100")
    pg.dispatch_event("#c-suma", "change")
    pg.wait_for_timeout(1500)
    pg.click("#c-adauga")
    pg.wait_for_timeout(2500)
    print("[format] mesajul de pe F5: %r" % pg.evaluate("document.querySelector('#c-mesaj') && document.querySelector('#c-mesaj').innerText"))


def _pas_f(pg, ctx):
    """Înapoi pe F1: aceeași încasare (F1A18 bifată), apoi Adaugă; Casa se redesenează cu rândul nou și confirmarea."""
    _incasare_f1a18(pg)
    pg.click("#c-adauga")
    pg.wait_for_selector("#c-confirmare", timeout=20000)
    pg.wait_for_timeout(800)
    print("[format] confirmarea: %r" % pg.evaluate("document.querySelector('#c-confirmare').innerText"))
    print("[format] rândurile Casei: %r" % pg.evaluate("Array.from(document.querySelectorAll('#c-tabel tbody.tn-nota .tn-rand')).map(r => r.innerText.replace(/\\s+/g, ' '))"))


def _pas_g(pg, ctx):
    """Chitanța nouă: rândul ei în Casă, detaliul, clic pe „PDF chitanță”; PDF-ul descărcat prin clic se salvează în directorul parcurgerii."""
    rand = "#c-tabel tbody.tn-nota:has-text('CHF1-2')"
    pg.locator(rand + " .tn-deschide").first.click()
    os.makedirs(ctx.director, exist_ok=True)
    with pg.expect_download(timeout=30000) as primit:
        pg.locator(rand + " [data-chpdf]").first.click()
    primit.value.save_as(os.path.join(ctx.director, "chitanta_CHF1_2.pdf"))
    for alta in pg.context.pages[1:]:   # fila goală deschisă de aplicație pentru PDF (în browserul fără ecran PDF-ul se descarcă)
        alta.close()


def _pas_h(pg, ctx):
    """Istoric facturi, luna 10/2026 (luna precedentă celei curente a ceasului fix)."""
    _firma(pg, "F1 Comert Stoc", "#fa-facturi")
    pg.click("#fac-istoric")
    pg.wait_for_selector("#fac-prev", timeout=20000)
    pg.click("#fac-prev")
    pg.wait_for_selector("button.fac-frand-btn", timeout=20000)


def _pas_i(pg, ctx):
    """Registru jurnal 11/2026, notele cu contul 4111 (câmpul de căutare al tabelului de note)."""
    _firma(pg, "F1 Comert Stoc", "#fa-jurnal")
    pg.wait_for_selector("#jn-cauta", timeout=20000)
    pg.fill("#jn-cauta", "4111")
    pg.dispatch_event("#jn-cauta", "input")
    pg.wait_for_timeout(1500)
    print("[format] notele lunii (poziție, număr, stare, linii): %r" % pg.evaluate("""async () => { const t = sessionStorage.getItem('iconta_token');
        const r = await fetch('/tenants/105779/jurnal?an=2026&luna=11', {headers: t ? {Authorization: 'Bearer ' + t} : {}}); const j = await r.json();
        return j.note.map((n, i) => [i, n.numar, n.status, n.linii.map(l => l.debit + '/' + l.credit + ':' + l.suma).join(';')]); }"""))


def _pas_i_tva(pg, ctx):
    """Același registru, notele cu contul 4427 (TVA colectată = exigibilă): nicio notă nouă de TVA exigibilă (F1 nu e în TVA la încasare)."""
    pg.fill("#jn-cauta", "4427")
    pg.dispatch_event("#jn-cauta", "input")
    pg.wait_for_timeout(1500)


def _pas_j(pg, ctx):
    """Încasare client, 410001005, a doua oară: pozițiile rămase."""
    _casa(pg)
    _dispozitie(pg)
    _incasare(pg, "410001005")


def _pas_j_refuz(pg, ctx):
    """Plată furnizor DANTE INTERNATIONAL SA (CUI 14399840), „Avans, fără factură”, destinația bunuri, suma 1779.46, Adaugă: refuzul „nu încape în casă”."""
    pg.click(BUT_TIP % "plata_furnizor")
    pg.fill("#c-cui", "14399840")
    pg.dispatch_event("#c-cui", "change")
    pg.wait_for_timeout(2000)
    pg.fill("#c-suma", "1779.46")
    pg.dispatch_event("#c-suma", "change")
    pg.wait_for_timeout(800)
    pg.locator("#c-avans").check(timeout=10000)
    pg.wait_for_timeout(1000)
    if pg.query_selector("#c-avans-dest"):
        pg.click("button[data-valoare=\"stocuri\"]", timeout=5000)
    pg.wait_for_timeout(1000)
    pg.click("#c-adauga")
    pg.wait_for_timeout(2500)
    print("[format] refuzul plății: %r" % pg.evaluate("Array.from(document.querySelectorAll('#c-mesaj, #c-previz-refuz')).map(e => e.innerText)"))


ACTIUNI = {"a": _pas_a, "b": _pas_b, "c": _pas_c, "c-ro": _pas_c_ro, "d": _pas_d, "e": _pas_e, "e-98": _pas_e98, "f": _pas_f, "g": _pas_g, "h": _pas_h, "i": _pas_i, "i-tva": _pas_i_tva,
           "j": _pas_j, "j-refuz": _pas_j_refuz}


def ruleaza(pagina, ctx):
    for pas in [p for p in os.environ.get("PARCURS_PASI", ",".join(PASI)).split(",") if p in ACTIUNI]:
        try:
            ACTIUNI[pas](pagina, ctx)
        except Exception as e:   # noqa: BLE001 — o acțiune care nu s-a putut face nu oprește parcursul: pagina vie, așa cum a rămas, merge oracolului
            print("[parcurs] pasul %s: acțiune neterminată (%s: %s)" % (pas, type(e).__name__, str(e)[:200]))
        rez, v = VP.verifica_pagina(pagina, ctx.lot, pas, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (pas, v, rez))
