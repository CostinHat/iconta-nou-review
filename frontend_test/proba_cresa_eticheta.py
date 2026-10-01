# -*- coding: utf-8 -*-
"""PROBA zonei „Tichete de creșă" din statul de plată (01.10.2026, ferestrele de indexare).

DE CE O PROBĂ PROPRIE. Textul schimbat stă într-o zonă care apare abia după ce se apasă butonul de
creșă al unui salariat; scanul de interacțiune apasă doar o parte din butoane, deci nu garantează că o
vede. Aici se deschide EXPLICIT zona și se măsoară pe randare:

  ETICHETA   textul nu mai scrie o valoare fiscală (450/740) și nici „GRI — blocată", ci temeiul
  A11Y       axe pe desktop (zona deschisă) și, pe telefon, ținte >= 24px + fără derulare orizontală
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
from vizual.nav_ecrane import ecran_stat_plata  # noqa: E402

IESIRE = os.path.join(HERE, "proba_cresa_eticheta.json")


def _zona(pg):
    ecran_stat_plata(pg)
    pg.click("[data-cresa]", timeout=15000)
    pg.wait_for_selector("#cresa-input", timeout=10000)
    pg.wait_for_timeout(300)
    return pg.eval_on_selector("#sp-cresa-zona", "e => e.innerText")


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        text = _zona(pg)
        r["eticheta"] = text
        r["valoare_fiscala_in_text"] = bool(re.search(r"\b(450|740|770)\b", text))
        r["gri_blocata"] = bool(re.search(r"GRI|blocat", text))
        r["temei_in_text"] = bool(re.search(r"Legea 165/2018 art\.19", text) and re.search(r"HG 1045/2018", text))
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()

        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _zona(pm)
        r["mobil"] = pm.evaluate("""() => {
            const z = document.querySelector('#sp-cresa-zona');
            const mici = [...z.querySelectorAll('button,input')].filter(e => {
                const b = e.getBoundingClientRect(); return b.width > 0 && (b.width < 24 || b.height < 24); })
                .map(e => e.id || e.className);
            return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    tinte_sub_24: mici};
        }""")
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ax = r["axe_desktop"]
    print("eticheta:", r["eticheta"].replace("\n", " | ")[:300])
    print("valoare fiscala in text:", r["valoare_fiscala_in_text"], "· GRI/blocata:", r["gri_blocata"],
          "· temei:", r["temei_in_text"])
    print("axe:", json.dumps(ax, ensure_ascii=False)[:300])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
