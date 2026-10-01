# -*- coding: utf-8 -*-
"""PROBA UI D212 Etapa 2: formularul Declarației unice cu bifa „Include venitul din registrul RIP".

Traseul real din ecranul Declarații (firma implicită a contului de probă, `w_auth`): tip D212 -> formularul
-> identitate + bifa RIP -> Regenerează -> XML-ul generat conține subsecțiunea I.1.1 (`<cap11`, categ_venit
1016, bifa111=1). Plus validarea pe câmp (CAEN greșit -> mesaj de contabil pe câmp) și A11Y: axe desktop +
telefon (ținte >= 24px, fără derulare orizontală). Rulează cu app viu pe PROBA_BAZA (8011, rețeta din predare).
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

IESIRE = os.path.join(HERE, "proba_d212_formular_ui.json")
CNP = "1800101221144"   # cifra de control verificata


def _formular(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000)
    pg.select_option("#dec-tip", "d212")
    pg.wait_for_timeout(500)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_selector("#d212-cnp", timeout=20000)


def _completeaza(pg, caen=""):
    for sel, v in (("#d212-cnp", CNP), ("#d212-nume", "POPESCU ION"), ("#d212-adr", "Bucuresti Sector 1"),
                   ("#d212-caen", caen)):
        pg.fill(sel, v)
        pg.dispatch_event(sel, "change")
    if not pg.is_checked("#d212-rip"):
        pg.check("#d212-rip")
    pg.dispatch_event("#d212-rip", "change")


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1400})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        _formular(pg)
        r["campuri_noi"] = all(pg.query_selector(s) for s in ("#d212-rip", "#d212-pp", "#d212-caen"))

        _completeaza(pg, caen="62A1")      # CAEN invalid -> refuz pe camp
        pg.click("#d212-regen")
        pg.wait_for_timeout(600)
        r["eroare_caen"] = pg.evaluate("""() => { const e = document.querySelector('.msg-eroare[data-camp="d212-caen"]');
                                              return e ? e.innerText : ''; }""")

        _completeaza(pg, caen="6201")
        pg.click("#d212-regen")
        pg.wait_for_timeout(9000)
        corp = pg.evaluate("() => document.body.innerText")
        # XML-ul stă în <details> închis: innerText e gol pe elemente ascunse -> textContent
        xml = pg.evaluate("""() => [...document.querySelectorAll('pre.dec-xml-pre')].map(e => e.textContent || '').join('\\n')""")
        r["xml_are_cap11"] = bool(re.search(r"<cap11[^>]*categ_venit=\"1016\"", xml))
        r["bifa111"] = bool(re.search(r'bifa111="1"', xml))
        r["duk_text"] = (re.search(r"(?i)(DUK[^\n]{0,120})", corp) or [""])[0][:160] if re.search(r"(?i)DUK", corp) else ""
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()

        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _formular(pm)
        r["mobil"] = pm.evaluate("""() => {
            const z = document.querySelector('#dec-d212-form');
            // ținta unei căsuțe dintr-un <label class="set-bifa"> e eticheta (click pe text bifează);
            // se raportează AMBELE: căsuța singură (cum o măsoară scanul oficial) și eticheta.
            const tinta = e => (e.type === 'checkbox' && e.closest('label')) ? e.closest('label') : e;
            const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
            const el = [...z.querySelectorAll('button,input')];
            return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    tinte_sub_24: el.filter(e => sub(tinta(e).getBoundingClientRect())).map(e => e.id || e.className),
                    casute_sub_24_masurate_singure: el.filter(e => e.type === 'checkbox' && sub(e.getBoundingClientRect()))
                        .map(e => e.id + ' ' + Math.round(e.getBoundingClientRect().width) + 'px')};
        }""")
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("campuri noi:", r["campuri_noi"], "· eroare CAEN:", repr(r["eroare_caen"][:120]))
    print("xml cap11 1016:", r["xml_are_cap11"], "· bifa111:", r["bifa111"], "·", r["duk_text"])
    print("axe:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:300])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
