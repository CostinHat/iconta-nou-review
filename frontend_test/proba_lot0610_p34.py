# -*- coding: utf-8 -*-
"""PROBA în browser — lotul 06.10, părțile 3 și 4 (comanda Costin 06.10.2026), pe baza de TEST (8011).

  P3 pct.11: mesajul propunerii notei de salarii pe o lună care soldează 421 (martie) și pe una care nu (octombrie, cu concediu
             medical) — forma veche spunea „coincide … în limita de toleranță” pe amândouă.
  P4 pct.14/15: pachetul și previzualizarea emailului — eticheta rezultatului și un text cu marcaje „**”.

Nu scrie nimic: propunerea notei (`POST …/salarii-contare/propunere`) doar calculează; fereastra poveștii se închide fără
„Salvează”/„Aprobă”/„Trimite”.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_lot0610_p34.py --asistent asistent@prisma-cont.test \
        --iesire /tmp/.../p34_dupa.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402

TEXT_CU_MARCAJE = "**Veniturile** lunii au fost bune.\n# Titlu\nRezultatul e *pozitiv*."


def _texte(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).map(e => e.innerText.trim()).filter(Boolean)")


def _desktop(pg, baza):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
    pg.wait_for_timeout(700)


def _propunere(pg, iesire, eticheta):
    with pg.expect_response(lambda x: "/salarii-contare/propunere" in x.url, timeout=60000) as rr:
        pg.click("#sp-contare")
    d = rr.value.json()
    pg.wait_for_timeout(700)
    zona = pg.eval_on_selector("#sp-contare-zona", "e => e.innerText")
    pg.screenshot(path="%s_stat_%s.png" % (iesire, eticheta), full_page=True)
    return {"luna_afisata": pg.eval_on_selector("#sp-luna, .sp-luna, .pf-titlu", "e => e.innerText") if pg.query_selector("#sp-luna, .sp-luna, .pf-titlu") else None,
            "net_fluturasi_server": d.get("net_fluturasi"), "divergente_server": d.get("divergente"),
            "mesaj": [t for t in _texte(pg, "#sp-contare-zona .caseta-info, #sp-contare-zona .caseta-atentie")],
            "zona": zona[:900], "axe": _axe(pg)}


def proba(pw, baza, asistent, firma, firma_pachet, luna_pachet, iesire):
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    # ---- P4: pachetul + previzualizarea emailului
    _desktop(pg, baza)
    pg.click(".asi-nod[data-nod='pachete']")
    pg.wait_for_selector("#pac-firma", timeout=15000)
    r["pachet_firme_vizibile"] = pg.eval_on_selector_all("#pac-firma option", "els => els.map(e => e.textContent)")
    val = pg.evaluate("(f) => { const o = [...document.querySelectorAll('#pac-firma option')].find(x => x.textContent.includes(f)); return o ? o.value : null; }", firma_pachet)
    if val is None:
        raise SystemExit("firma %r nu e în lista asistentului: %s" % (firma_pachet, r["pachet_firme_vizibile"]))
    pg.select_option("#pac-firma", value=val)
    pg.fill("#pac-an", "2026"); pg.dispatch_event("#pac-an", "change")
    pg.select_option("#pac-luna", value=str(luna_pachet))
    pg.click("#pac-continua")
    pg.wait_for_selector("#pac-deschide", timeout=20000)
    pg.wait_for_timeout(500)
    r["pachet_rezumat"] = _texte(pg, ".pac-rez-rand")
    pg.screenshot(path=iesire + "_pachet.png", full_page=True)
    r["pachet_axe"] = _axe(pg)
    pg.click("#pac-deschide")
    pg.wait_for_selector(".pacm", timeout=10000)
    pg.wait_for_timeout(700)
    pg.fill("#pacm-text", TEXT_CU_MARCAJE)
    pg.dispatch_event("#pacm-text", "input")
    pg.click("#pacm-vezi")
    pg.wait_for_function("() => !/Se încarcă/.test((document.querySelector('#pacm-preview')||{}).innerText||'x')", timeout=20000)
    pg.wait_for_timeout(500)
    txt = pg.eval_on_selector("#pacm-preview", "e => e.innerText")
    r["email"] = {"text": txt[:700], "are_marcaje": bool(re.search(r"\*\*|__|^#", txt, re.M)),
                  "eticheta_rezultat": [l for l in txt.splitlines() if l.startswith("Rezultat")]}
    pg.screenshot(path=iesire + "_email.png", full_page=True)
    r["email_axe"] = _axe(pg)
    pg.click("#pacm-x")
    pg.wait_for_timeout(300)
    # ---- P3: propunerea notei de salarii
    _desktop(pg, baza)
    pg.click(".asi-nod[data-nod='firme']")
    pg.wait_for_selector("#firme-lista .firme-rand, #firme-lista .firme-gol", timeout=15000)
    pg.wait_for_timeout(500)
    pg.locator("#firme-lista button.firme-rand", has_text=re.compile(firma)).first.click()
    pg.wait_for_selector("#fa-salariati", timeout=15000)
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-contare", timeout=20000)
    pg.wait_for_timeout(800)
    r["octombrie"] = _propunere(pg, iesire, "octombrie")
    for _ in range(7):
        pg.click("#sp-prev")
        pg.wait_for_selector("#sp-contare", timeout=20000)
        pg.wait_for_timeout(600)
    r["martie"] = _propunere(pg, iesire, "martie")
    r["cereri_scriere"] = cereri
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--firma-pachet", default="Coafor")
    ap.add_argument("--luna-pachet", type=int, default=8)
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, a.firma, a.firma_pachet, a.luna_pachet, a.iesire.replace(".json", ""))
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: r[k] for k in ("pachet_rezumat", "email")}, ensure_ascii=False)[:1500])
    for k in ("octombrie", "martie"):
        print(k, json.dumps({x: r[k][x] for x in ("net_fluturasi_server", "mesaj")}, ensure_ascii=False)[:900])


if __name__ == "__main__":
    main()
