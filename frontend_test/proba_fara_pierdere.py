# -*- coding: utf-8 -*-
"""PROBA în browser — „un contabil nu pierde niciodată ce a completat” (comanda Costin 05.10.2026, pct.1).

Trei situații, pe contul de asistent, pe factura de pe F1 (baza de TEST):
  a) sesiunea EXPIRĂ în mijlocul facturii (tokenul din tab e înlocuit cu unul expirat, apoi omul mai tastează);
  b) emiterea e refuzată (lipsește forma juridică) -> „Deschide Date firmă” -> Salvează -> Înapoi;
  c) o sesiune trecută de jumătatea duratei se REÎNNOIEȘTE singură la următoarea cerere.
Lanțul care o rulează pune o parolă temporară pe contul de asistent de test (pentru reautentificare) și restaurează hash-ul și
profilul firmei după. Nimic pe producție.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import auth_api, db  # noqa: E402
from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402

CLIENT = {"#em-cui": "14399840", "#em-nume": "ZT Client Proba Pierdere", "#em-adresa": "Str. Proba 1, București"}
LINIE = {"#em-l0-cantitate": "2", "#em-l0-pret_unitar": "150"}


def _token_cu_varsta(email, iat_in_urma, durata):
    import psycopg2.extras as E
    db.init_pool()
    with db.get_conn() as c, c.cursor(cursor_factory=E.RealDictCursor) as cur:
        cur.execute("SELECT * FROM public.users WHERE email=%s", (email,))
        u = dict(cur.fetchone())
        c.rollback()
    return auth_api.emite_token({"id": u["id"], "rol": u["rol"], "accounting_firm_id": u["accounting_firm_id"]},
                                durata=durata, acum=int(time.time()) - iat_in_urma)


def _deschide_emiterea(pg, baza, firma):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore", timeout=20000)
    pg.wait_for_timeout(500)
    pg.click(".asi-nod[data-nod='firme']")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=15000)
    pg.locator("#firme-lista button.firme-rand", has_text=firma).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=15000)
    pg.click("#fa-facturi")
    pg.wait_for_selector("#fac-emite", timeout=15000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-cui, #em-nu", timeout=20000)
    if pg.query_selector("#em-nu"):   # numerotare neconfigurată pe firma de test: „încep acum”, fără serie
        pg.click("#em-nu")
        pg.wait_for_selector("#em-salveaza-config2", timeout=10000)
        pg.click("#em-salveaza-config2")
        pg.wait_for_selector("#em-cui", timeout=20000)
    pg.wait_for_timeout(600)


def _completeaza(pg):
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", "Consultanță contabilă")
    for sel, v in LINIE.items():
        pg.fill(sel, v)
    try:   # cota TVA propusă (AI) — fără ea emiterea nu pleacă
        pg.wait_for_function("() => { const c = document.querySelector('#em-l0-cota'); return c && /%/.test(c.textContent); }", timeout=20000)
    except Exception:
        pass
    pg.wait_for_timeout(800)


def _stare_formular(pg):
    sel = list(CLIENT) + ["#em-l0-descriere"] + list(LINIE)
    return {s: (pg.eval_on_selector(s, "e => e.value") if pg.query_selector(s) else None) for s in sel}


def proba(pw, baza, asistent, parola, firma, iesire):
    r = {}
    # ── a) expirarea sesiunii în mijlocul facturii ──────────────────────────────────────────────────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _deschide_emiterea(pg, baza, firma)
    _completeaza(pg)
    r["a_inainte_de_expirare"] = _stare_formular(pg)
    expirat = _token_cu_varsta(asistent, 2 * 86400, 3600)
    pg.evaluate("(t) => sessionStorage.setItem('iconta_token', t)", expirat)
    pg.fill("#em-l0-descriere", "Consultanță contabilă lunară")   # declanșează /produse/potriveste -> 401
    pg.wait_for_timeout(2500)
    r["a_dupa_401"] = {"fereastra_reautentificare": bool(pg.query_selector(".reaut-overlay")),
                       "ecran_login": bool(pg.query_selector("#login-email, #pagina-acces-btn")),
                       "formular": _stare_formular(pg)}
    pg.screenshot(path=iesire + "_a_expirare.png", full_page=True)
    if r["a_dupa_401"]["fereastra_reautentificare"]:
        r["a_axe_fereastra"] = _axe(pg)
        pg.fill("#reaut-parola", parola)
        try:   # cererea refuzată cu 401 se RELUA după reautentificare — se așteaptă răspunsul ei
            with pg.expect_response(lambda x: "potriveste" in x.url and x.request.method == "POST", timeout=30000) as rr:
                pg.click("#reaut-continua")
            r["a_cererea_reluata"] = rr.value.status
        except Exception as e:  # noqa: BLE001
            r["a_cererea_reluata"] = "nereluata: %s" % type(e).__name__
        pg.wait_for_timeout(1500)
        r["a_dupa_reautentificare"] = {"fereastra_inchisa": not pg.query_selector(".reaut-overlay"),
                                       "formular": _stare_formular(pg),
                                       "token_nou": pg.evaluate("() => sessionStorage.getItem('iconta_token')") != expirat}
    r["a_cereri"] = [c for c in cereri if "auth" in c[1] or "potriveste" in c[1]]
    r["a_erori_consola"] = erori
    b.close()
    # ── b) refuzul emiterii -> Date firmă -> Salvează -> Înapoi ─────────────────────────────────────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _deschide_emiterea(pg, baza, firma)
    _completeaza(pg)
    pg.click("#em-emite")
    pg.wait_for_timeout(4000)
    if pg.query_selector("#em-poarta-nu"):   # poarta „Pleacă marfa acum?” (linie de stoc)
        pg.click("#em-poarta-nu"); pg.wait_for_timeout(3000)
    r["b_cereri_emite"] = [c for c in cereri if "emite" in c[1]]
    r["b_cota"] = pg.eval_on_selector("#em-l0-cota", "e => e.textContent") if pg.query_selector("#em-l0-cota") else None
    pg.screenshot(path=iesire + "_b_refuz.png", full_page=True)
    r["b_refuz"] = pg.eval_on_selector("#em-rezultat", "e => e.innerText")[:300] if pg.query_selector("#em-rezultat") else None
    r["b_buton_date_firma"] = bool(pg.query_selector("#em-deschide-date-firma"))
    if r["b_buton_date_firma"]:
        pg.click("#em-deschide-date-firma")
        pg.wait_for_selector("#df-forma_juridica", timeout=15000)
        pg.select_option("#df-forma_juridica", "SRL")
        pg.dispatch_event("#df-forma_juridica", "change")
        if pg.query_selector("#df-capital_subscris"):
            pg.fill("#df-capital_subscris", "200")
        pg.click("#df-salveaza")
        pg.wait_for_timeout(2500)
        r["b_date_firma_mesaj"] = pg.eval_on_selector_all("#df-msg, .msg-eroare", "e => e.map(x => x.innerText.trim()).filter(Boolean)")
        pg.click(".nav-sageata.nav-inapoi")
        pg.wait_for_timeout(1500)
        r["b_dupa_inapoi"] = _stare_formular(pg)
        pg.screenshot(path=iesire + "_b_dupa_inapoi.png", full_page=True)
        r["b_axe"] = _axe(pg)
    r["b_erori_consola"] = erori
    b.close()
    # ── c) reînnoirea unei sesiuni trecute de jumătate ─────────────────────────────────────────────────────────
    vechi = _token_cu_varsta(asistent, 13 * 3600, 24 * 3600)
    b, pg, cereri, erori = _pagina(pw, "sessionStorage.setItem('iconta_token'," + json.dumps(vechi) + ");"
                                   + _sesiune(asistent).split(";", 1)[1])
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore", timeout=20000)
    pg.wait_for_timeout(1500)
    pg.click(".asi-nod[data-nod='firme']")
    pg.wait_for_timeout(1500)
    nou = pg.evaluate("() => sessionStorage.getItem('iconta_token')")
    r["c_reinnoire"] = {"cereri_reinnoire": [c for c in cereri if "reinnoieste" in c[1]], "token_schimbat": nou != vechi,
                        "erori_consola": erori}
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    parola = os.environ["PROBA_PAROLA_TEMPORARA"]
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, parola, a.firma, a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire)
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(r, ensure_ascii=False, indent=1)[:5000])


if __name__ == "__main__":
    main()
