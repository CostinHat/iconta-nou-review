# -*- coding: utf-8 -*-
"""PROBA UI D212 Etapa 4: excepția de la baza minimă CASS pe formularul Declarației unice -> oblig_realizat în XML.

Firma implicită a contului de probă -> D212 -> identitate + o activitate pe normă de 20.000 lei (sub 6 sm) -> Regenerează:
XML-ul are <oblig_realizat> cu CASS 2.430 (baza minimă, CF art.174 alin.(6)); apoi excepția „salarii” -> CASS 2.000
(alin.(7) lit.a). Plus axe desktop + telefon. Rulează cu app viu pe PROBA_BAZA (8011). Nu scrie nimic în bază.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "vizual"))
sys.path.insert(0, os.path.dirname(HERE))

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
from vizual import axe_scan  # noqa: E402

IESIRE = os.path.join(HERE, "proba_d212_contributii_ui.json")
CNP = "1800101221144"   # cifra de control verificată


def _formular(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000)
    pg.select_option("#dec-tip", "d212")
    pg.wait_for_timeout(500)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_selector("#d212-exccass", timeout=20000)


def _xml(pg):
    pg.click("#d212-regen")
    pg.wait_for_timeout(9000)
    x = pg.evaluate("""() => [...document.querySelectorAll('pre.dec-xml-pre')].map(e => e.textContent || '').join('\\n')""")
    o = re.search(r"<oblig_realizat ([^>]*)/>", x)
    return dict(re.findall(r'(\w+)="([^"]*)"', o.group(1))) if o else {}


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1400})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        _formular(pg)
        r["optiuni_exceptie"] = pg.evaluate("() => [...document.querySelectorAll('#d212-exccass option')].map(o => o.value)")
        for sel, v in (("#d212-cnp", CNP), ("#d212-nume", "POPESCU ION"), ("#d212-adr", "Bucuresti Sector 1")):
            pg.fill(sel, v)
            pg.dispatch_event(sel, "change")
        pg.fill("#d212-n-norma", "20000")
        pg.click("#d212-n-add")
        pg.wait_for_timeout(300)
        o1 = _xml(pg)
        r["fara_exceptie"] = {k: o1.get(k) for k in ("baza_cass_datorat_ai", "cass_datorat_ai", "oblimpoz_real_total", "dif_de_plata")}
        pg.wait_for_selector("#d212-exccass", timeout=15000)
        pg.select_option("#d212-exccass", "salarii")
        pg.dispatch_event("#d212-exccass", "change")
        o2 = _xml(pg)
        r["cu_exceptie_salarii"] = {k: o2.get(k) for k in ("baza_cass_datorat_ai", "cass_datorat_ai", "dif_de_plata")}
        corp = pg.evaluate("() => document.body.innerText")
        r["duk_text"] = (re.search(r"(?i)(DUK[^\n]{0,120})", corp) or [""])[0][:160] if re.search(r"(?i)DUK", corp) else ""
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()
        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _formular(pm)
        r["mobil"] = pm.evaluate("""() => {
            const z = document.querySelector('#dec-d212-form');
            const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
            return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    tinte_sub_24: [...z.querySelectorAll('select,button')].filter(e => sub(e.getBoundingClientRect())).map(e => e.id)};
        }""")
        r["axe_mobil"] = axe_scan.scaneaza(pm)
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("opțiuni excepție:", r["optiuni_exceptie"])
    print("fără excepție:", r["fara_exceptie"], "· cu excepția salarii:", r["cu_exceptie_salarii"])
    print(r["duk_text"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:200], "· axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:200])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
