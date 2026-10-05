# -*- coding: utf-8 -*-
"""PROBA în browser — pasul D al comenzii Costin 05.10.2026 („fluxul de factură pe F1”, pct.10–11), contul de asistent, baza de TEST.
  11) fereastra firmei: titlurile de grup și câte carduri are fiecare; niciun card în afara grupurilor; Solicitări în fereastră
  10) Stocuri: situația stocului întâi (rândurile tabelului), formularele închise, Rețete numai la HoReCa
Lanțul pune articolul de probă și îl șterge după.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402
from proba_flux_c import _deschide_firma, _text  # noqa: E402


def proba(pw, baza, asistent, firma, iesire, lat=1280):
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent), lat=lat, inalt=900)
    _deschide_firma(pg, baza, firma)
    pg.wait_for_timeout(800)
    r["11_grupuri"] = pg.evaluate("""() => {
      const g = [...document.querySelectorAll('.firme-grup')];
      return { titluri: g.map((x) => [x.querySelector('h3').innerText.trim(), x.querySelectorAll('.firme-optiune').length]),
               carduri_total: document.querySelectorAll('.firme-optiune').length,
               in_afara_grupurilor: [...document.querySelectorAll('.firme-optiune')].filter((b) => !b.closest('.firme-grup')).length };
    }""")
    pg.screenshot(path=iesire + "_11_fereastra.png", full_page=True)
    r["11_axe"] = _axe(pg)
    # Solicitări: fereastră peste meniul firmei, nu înlocuire inline
    pg.click("#fa-solicitari")
    pg.wait_for_timeout(1500)
    # fereastră nouă = o verigă în plus în firul navigatorului; inline = firul rămâne la firmă
    r["11_fir_dupa_solicitari"] = pg.eval_on_selector_all(".fir-veriga", "e => e.map(x => x.innerText.trim())")
    _deschide_firma(pg, baza, firma)
    pg.click("#fa-stocuri")
    pg.wait_for_selector("#s-prev", timeout=15000)
    pg.wait_for_timeout(2000)
    r["10_situatie"] = pg.eval_on_selector_all("#s-situatie-tabel tbody tr", "e => e.map(r => [...r.cells].map(c => c.innerText.trim()))") \
        if pg.query_selector("#s-situatie-tabel") else _text(pg, "#s-situatie")
    r["10_total"] = _text(pg, "#s-situatie-tabel tfoot")
    r["10_formulare_inchise"] = pg.evaluate("() => { const z = document.querySelector('#cv-zona'); return z ? z.hidden : null; }")
    r["10_primul_element"] = pg.evaluate("""() => { const c = document.querySelector('#s-prev').closest('.fereastra-corp') || document.body;
        const t = c.querySelector('#s-situatie, #s-prev'); return t ? t.id : null; }""")
    pg.screenshot(path=iesire + "_10_stocuri.png", full_page=True)
    r["10_axe"] = _axe(pg)
    if pg.query_selector("#cv-toggle"):
        pg.click("#cv-toggle")
        pg.wait_for_timeout(500)
    r["10_retete_vizibile"] = bool(pg.query_selector("#rt-lista"))
    pg.screenshot(path=iesire + "_10_formulare.png", full_page=True)
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, a.firma, a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire)
        r["mobil"] = proba(pw, a.baza, a.asistent, a.firma, (a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire) + "_mobil", lat=393)["11_grupuri"]
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str)[:5000])


if __name__ == "__main__":
    main()
