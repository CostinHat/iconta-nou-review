# -*- coding: utf-8 -*-
"""PROBA în browser — pasul C al comenzii Costin 05.10.2026 („fluxul de factură pe F1”, pct.6–9), pe contul de asistent, baza de TEST.

Lanțul care o rulează pune datele (articol cu stoc, produs în nomenclator, formă + capital) și le șterge după.
  9) linia facturii: prețul și UM din nomenclator; linia fără articol spune că marfa nu se descarcă; stocul fără zecimale
  6) nota 607=371 de la emitere poartă factura ca document; descrierea are cantitatea cu UM
  7) detaliul facturii: „notă propusă, de validat” (nu „contabilizată”) + legătura spre notă
  6) Registrul jurnal: nota fără document e marcată; „Validează” pe ea cere confirmare
  8) banca: mesajul de import numără potrivite/fără potrivire; contarea comisionului spune nota creată (627=5121)
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

EXTRAS = "Data;Detalii;Suma\n05.10.2026;Comision administrare cont;-12,50\n05.10.2026;Incasare client necunoscut;500,00\n"


def _text(pg, sel):
    return pg.eval_on_selector_all(sel, "e => e.filter(x => x.offsetParent !== null).map(x => x.innerText.trim())")


def _deschide_firma(pg, baza, firma):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore", timeout=20000)
    pg.wait_for_timeout(500)
    pg.click(".asi-nod[data-nod='firme']")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=15000)
    pg.locator("#firme-lista button.firme-rand", has_text=firma).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=15000)


def proba(pw, baza, asistent, firma, tid, iesire):
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    # ── 9) linia facturii ──
    _deschide_emiterea(pg, baza, firma)
    pg.fill("#em-cui", "14399840"); pg.fill("#em-nume", "DANTE INTERNATIONAL SA"); pg.fill("#em-adresa", "Șos. Virtuții 148, București")
    pg.fill("#em-l0-descriere", "Pâine albă feliată")
    pg.wait_for_timeout(2500)
    r["9_optiune_articol"] = pg.eval_on_selector_all("#em-l0-articol option", "e => e.map(x => x.textContent)")
    r["9_dupa_denumire"] = {
        "pret": pg.eval_on_selector("#em-l0-pret_unitar", "e => e.value"),
        "um": pg.eval_on_selector("#em-l0-um", "e => e.value") if pg.query_selector("#em-l0-um") else None,
        "semn_fara_articol": _text(pg, "#em-l0-fara-articol"),
    }
    pg.screenshot(path=iesire + "_9_linie.png", full_page=True)
    opt = pg.eval_on_selector_all("#em-l0-articol option", "e => e.map(x => x.value).filter(Boolean)")
    if opt:
        pg.select_option("#em-l0-articol", opt[0])
        pg.wait_for_timeout(2500)
    r["9_dupa_articol"] = {"semn_fara_articol": _text(pg, "#em-l0-fara-articol"),
                           "um": pg.eval_on_selector("#em-l0-um", "e => e.value") if pg.query_selector("#em-l0-um") else None}
    pg.fill("#em-l0-cantitate", "2")
    if not pg.eval_on_selector("#em-l0-pret_unitar", "e => e.value"):
        pg.fill("#em-l0-pret_unitar", "5")
    pg.wait_for_timeout(500)
    r["9_axe"] = _axe(pg)
    with pg.expect_response(lambda x: x.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
        pg.wait_for_selector("#em-poarta-da", timeout=10000)
        pg.click("#em-poarta-da")
    fid = (rr.value.json() or {}).get("factura_id")
    r["emitere"] = {"status": rr.value.status, "factura_id": fid}
    pg.wait_for_timeout(1500)
    # ── 7) detaliul facturii ──
    if fid:
        d = pg.evaluate("""async ([tid, fid]) => {
            const t = sessionStorage.getItem('iconta_token');
            const x = await fetch('/tenants/' + tid + '/facturi/' + fid, {headers: {Authorization: 'Bearer ' + t}});
            return await x.json(); }""", [tid, fid])
        r["7_api"] = {"contabilizata": d.get("contabilizata"), "nota_contare": d.get("nota_contare")}
        _deschide_firma(pg, baza, firma)
        pg.click("#fa-facturi")
        pg.wait_for_selector("#fac-istoric", timeout=15000)
        pg.click("#fac-istoric")
        pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=15000)
        r["7_lista_conteaza"] = bool(pg.query_selector(".fac-frand-btn[data-id='%s'] .fac-cont" % fid))
        pg.click(".fac-frand-btn[data-id='%s']" % fid)
        pg.wait_for_selector(".fd-antet", timeout=15000)
        pg.wait_for_timeout(800)
        r["7_detaliu"] = {"stare": _text(pg, ".fd-antet .fd-stare"), "buton_nota": _text(pg, "#fd-vezi-nota")}
        pg.screenshot(path=iesire + "_7_detaliu.png", full_page=True)
        r["7_axe"] = _axe(pg)
        if pg.query_selector("#fd-vezi-nota"):
            pg.click("#fd-vezi-nota")
            pg.wait_for_selector("#j-prev", timeout=15000)
            pg.wait_for_timeout(1000)
            r["7_jurnal_deschis"] = _text(pg, ".pf-intro")[:1]
    # ── 6) Registrul jurnal ──
    _deschide_firma(pg, baza, firma)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-prev", timeout=15000)
    pg.wait_for_timeout(1200)
    randuri = pg.eval_on_selector_all(".pf-lista .pf-frand", "e => e.map(x => x.innerText.replace(/\\s+/g, ' ').trim())")
    r["6_jurnal_randuri"] = [x for x in randuri if "607" in x or "Comision" in x or "Fara doc" in x or "Manual" in x][:6]
    r["6_marcaje_fara_document"] = len(_text(pg, ".jn-fara-doc"))
    pg.screenshot(path=iesire + "_6_jurnal.png", full_page=True)
    r["6_axe"] = _axe(pg)
    # validarea notei manuale fără document (pusă de lanț, descrierea „Manual fara document”)
    btn = pg.evaluate("""() => { const r = [...document.querySelectorAll('.pf-frand')].find(x => x.innerText.includes('Manual fara document'));
                                  const b = r && r.querySelector('[data-val]'); return b ? b.dataset.val : null; }""")
    if btn:
        cereri_val = []
        pg.on("request", lambda q: cereri_val.append(q.url) if q.url.endswith("/valideaza") else None)
        pg.click("[data-val='%s']" % btn)
        pg.wait_for_timeout(1200)
        r["6_validare"] = {"confirmare": _text(pg, "#caseta-atentie-activa .ca-mesaj"), "cereri_inainte_de_confirmare": len(cereri_val)}
        pg.screenshot(path=iesire + "_6_confirmare.png", full_page=True)
    # ── 8) banca ──
    _deschide_firma(pg, baza, firma)
    pg.click("#fa-banca")
    pg.wait_for_selector("#bk-fisier", timeout=15000)
    cale = iesire + "_extras.csv"
    open(cale, "w", encoding="utf-8").write(EXTRAS)
    pg.set_input_files("#bk-fisier", cale)
    pg.wait_for_timeout(3000)
    r["8_mesaj_import"] = _text(pg, "#bk-mesaj")
    r["8_ordine"] = pg.eval_on_selector_all("#bk-lista .pf-frand .pf-frand-sub", "e => e.map(x => x.innerText.slice(0, 40))")[:4]
    btn = pg.evaluate("""() => { const b = [...document.querySelectorAll('#bk-lista [data-cont]')].find(x => /627/.test(x.textContent));
                                  return b ? b.dataset.cont : null; }""")
    if btn:
        pg.click("#bk-lista [data-cont='%s']" % btn)
        pg.wait_for_timeout(2500)
        r["8_mesaj_contare"] = _text(pg, "#bk-mesaj")
    pg.screenshot(path=iesire + "_8_banca.png", full_page=True)
    r["8_axe"] = _axe(pg)
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--tid", type=int, default=4784)
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, a.firma, a.tid, a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire)
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
