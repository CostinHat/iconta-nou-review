# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-C, cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026: pagina principală a cabinetului (pasul implicit),
Balanță de verificare și Salariați (Stat de plată) ale firmei F1 Comert Stoc, deschise din fereastra firmei FĂRĂ nicio apăsare „← luna”, apoi Emite factură cu o ciornă
salvată prin API cu data 15.06.2025. Ciorna se șterge la final. Nu compară nimic și nu scrie verdicte. Importă numai biblioteca standard și verifica_pas.
Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă: aserțiunile pasului judecă ce s-a desenat (pe commitul de bază aserțiunile lotului pică)."""
# data zilei = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026), nu data calendaristică a rulării
import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
ZONA = TOP + ".zona-derulare"
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
    except Exception:   # noqa: BLE001 — pasul se judecă pe ce s-a desenat (aserțiunile pică), parcursul continuă
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


JS_API = """async ([metoda, url, corp]) => { const {api} = await import('/static/js/api.js');
  if (metoda === 'get') return await api.get(url); if (metoda === 'put') return await api.put(url, corp || {}); return await api.del(url); }"""
CIORNA = {"v": 1, "salvat_la": "2025-07-01T10:00:00.000Z", "linii": [{"descriere": "Proba 17.5-C", "cantitate": 1, "pret_unitar": 10}], "moneda": "RON", "scadentaScrisa": False, "pleacaMarfa": None,
          "semnMarfa": None, "campuri": {"em-data": "2025-06-15", "em-scadenta": "2025-07-15"}, "stareCui": None}


def tenant_f1(pg):
    try:
        d = pg.evaluate(JS_API, ["get", "/tenants", None])
        lista = d.get("tenants", d) if isinstance(d, dict) else d
        return [t["id"] for t in lista if (t.get("denumire") or t.get("nume") or "").startswith(F1)][0]
    except Exception:   # noqa: BLE001 — fără tenant pașii emitere pică
        return None


def ecran_luna(pg, id_card, asteapta):
    """Ecranul lunar deschis din fereastra firmei, fără „← luna”: pasul judecă luna propusă la deschidere."""
    firma(pg, F1)
    intra(pg, id_card, asteapta)
    pg.wait_for_timeout(1500)


def ecran_emitere(pg, tid):
    """Ciorna cu data 15.06.2025 se scrie prin API (ruta ciornelor de formular), apoi Facturi › Emite factură."""
    try:
        pg.evaluate(JS_API, ["put", "/tenants/%d/ciorne-formular/factura" % tid, {"continut": CIORNA}])
    except Exception:   # noqa: BLE001
        pass
    firma(pg, F1)
    intra(pg, "fa-facturi", "#fac-emite")
    try:
        pg.click("#fac-emite", timeout=10000)
        pg.wait_for_selector("#em-cui", timeout=25000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)


def sterge_ciorna(pg, tid):
    try:
        pg.evaluate(JS_API, ["del", "/tenants/%d/ciorne-formular/factura" % tid, None])
    except Exception:   # noqa: BLE001
        pass


def ruleaza(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                                    # 12 carduri (aserțiunea probei contractului)
    ecran_luna(pg, "fa-balanta", TOP + "#b-intro")
    pas("balanta")                                     # Balanța pornește pe 10/2026
    ecran_luna(pg, "fa-salariati", TOP + "#sp-prev")
    pas("stat")                                        # Statul de plată pornește pe 10/2026
    tid = tenant_f1(pg)
    if tid is not None:
        ecran_emitere(pg, tid)
    pas("emitere")                                     # data de azi, cardul spune 15.06.2025
    if tid is not None:
        sterge_ciorna(pg, tid)
