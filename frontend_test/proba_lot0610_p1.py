# -*- coding: utf-8 -*-
"""PROBA în browser — partea 1 a comenzii Costin 06.10.2026 (§6 din raportul F1), contul de asistent, baza de TEST.
  §6.1 factura pe o firmă fără serie: refuzul cere seria pe loc; după setare, emiterea continuă, cu factura păstrată
  §6.3/§6.4 Date firmă: metoda de stoc se alege; salvarea apare în „Istoricul modificărilor” (cine, câmp, vechi -> nou)
Lanțul restaurează profilul firmei și șterge factura emisă.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402
from proba_fara_pierdere import _deschide_emiterea  # noqa: E402
from proba_flux_c import _deschide_firma, _text  # noqa: E402


def proba(pw, baza, asistent, firma, iesire):
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _deschide_emiterea(pg, baza, firma)
    r["serie_la_deschidere"] = _text(pg, "#em-serie-nr")
    pg.fill("#em-cui", "14399840"); pg.fill("#em-nume", "DANTE INTERNATIONAL SA"); pg.fill("#em-adresa", "Șos. Virtuții 148, București")
    pg.fill("#em-l0-descriere", "Consultanță contabilă lunară")
    pg.fill("#em-l0-cantitate", "1"); pg.fill("#em-l0-pret_unitar", "500")
    pg.wait_for_timeout(3000)
    with pg.expect_response(lambda x: x.url.endswith("/facturi/emite"), timeout=60000) as rr0:
        pg.click("#em-emite")
    try:
        _det = rr0.value.json().get("detail")
    except Exception:
        _det = None
    pg.wait_for_timeout(1500)
    r["1_refuz"] = {"status": rr0.value.status, "cod": (_det or {}).get("cod") if isinstance(_det, dict) else None,
                    "numar_emis": (rr0.value.json() or {}).get("numar") if rr0.value.status == 200 else None,
                    "mesaj": _text(pg, "#em-rezultat .em-curs-titlu"),
                    "camp_serie": bool(pg.query_selector("#em-serie-noua")),
                    "factura_pastrata": pg.eval_on_selector("#em-nume", "e => e.value") if pg.query_selector("#em-nume") else None}
    pg.screenshot(path=iesire + "_1_refuz_serie.png", full_page=True)
    r["1_axe"] = _axe(pg)
    if pg.query_selector("#em-serie-noua"):
        pg.fill("#em-serie-noua", "ZT")
        with pg.expect_response(lambda x: x.url.endswith("/facturi/emite"), timeout=60000) as rr:
            pg.click("#em-serie-si-emite")
        corp = rr.value.json() if rr.value.status == 200 else {}
        r["1_dupa_serie"] = {"status": rr.value.status, "numar": corp.get("numar"), "factura_id": corp.get("factura_id"),
                             "serie_afisata": _text(pg, "#em-serie-nr")}
        pg.wait_for_timeout(1500)
        pg.screenshot(path=iesire + "_1_emisa.png", full_page=True)
    else:
        r["1_dupa_serie"] = None
    # §6.3 / §6.4 Date firmă
    _deschide_firma(pg, baza, firma)
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-salveaza", timeout=15000)
    pg.wait_for_timeout(1000)
    r["2_metoda_inainte"] = pg.eval_on_selector("#df-metoda_stoc", "e => e.value") if pg.query_selector("#df-metoda_stoc") else None
    if pg.query_selector("#df-metoda_stoc"):
        pg.select_option("#df-metoda_stoc", "cantitativ_valoric")
        for cid, v in (("df-reg_com", "J40/1234/2015"), ("df-adresa", "Str. Proba 1"), ("df-banca", "Banca Proba"),
                       ("df-iban", "RO49AAAA1B31007593840000"), ("df-telefon", "0712345678")):
            el = pg.query_selector("#" + cid)
            if el and not el.input_value():
                el.fill(v)
        pg.click("#df-salveaza")
        pg.wait_for_timeout(2500)
        pg.click(".nav-sageata.nav-inapoi")
        pg.wait_for_timeout(800)
        pg.click("#fa-datefirma")
        pg.wait_for_selector("#df-salveaza", timeout=15000)
        pg.wait_for_timeout(1000)
    r["2_jurnal"] = pg.eval_on_selector_all("#df-jurnal tbody tr", "e => e.map(r => [...r.cells].map(c => c.innerText.trim()).slice(1))")[:6]
    r["2_metoda_dupa"] = pg.eval_on_selector("#df-metoda_stoc", "e => e.value") if pg.query_selector("#df-metoda_stoc") else None
    pg.screenshot(path=iesire + "_2_date_firma.png", full_page=True)
    r["2_axe"] = _axe(pg)
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
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str)[:5000])


if __name__ == "__main__":
    main()
