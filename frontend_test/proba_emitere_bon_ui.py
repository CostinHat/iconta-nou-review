# -*- coding: utf-8 -*-
"""PROBA UI — câmpurile „Emisă pe baza bonului fiscal” pe ecranul de emitere (decizia Costin A, 02.10.2026).

Firma implicită a contului de probă -> «Emite factură»: câmpurile `em-bon-nr` / `em-bon-data` există, sunt etichetate și
accesibile; cererea trimisă la emitere le poartă (interceptată și OPRITĂ înainte de server — nu se emite nimic). Plus axe
desktop + telefon. Rulează cu app viu pe PROBA_BAZA (8011).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "vizual"))
sys.path.insert(0, os.path.dirname(HERE))

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
import nav_ecrane  # noqa: E402
from vizual import axe_scan  # noqa: E402

IESIRE = os.path.join(HERE, "proba_emitere_bon_ui.json")


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1300})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        nav_ecrane.ecran_emitere(pg)
        pg.wait_for_selector("#em-bon-nr", timeout=15000)
        r["campuri"] = pg.evaluate("""() => ['em-bon-nr','em-bon-data'].map(id => {
            const e = document.getElementById(id); const l = document.querySelector('label[for="'+id+'"]');
            return {id, exista: !!e, eticheta: l ? l.innerText.trim() : ''}; })""")
        trimise = []

        def opreste(route):
            trimise.append(route.request.post_data_json)
            route.abort()
        pg.route("**/facturi/emite", opreste)
        pg.fill("#em-nume", "CLIENT SRL")
        pg.fill("#em-bon-nr", "0042")
        pg.fill("#em-bon-data", "2026-09-10")
        pg.click("#em-emite")
        pg.wait_for_timeout(1500)
        cerere = trimise[0] if trimise else {}
        r["cerere"] = {k: cerere.get(k) for k in ("bon_fiscal_nr", "bon_fiscal_data")}
        r["poarta_stoc_afisata"] = pg.evaluate("() => !!document.querySelector('#em-poarta-da')")
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()
        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        nav_ecrane.ecran_emitere(pm)
        pm.wait_for_selector("#em-bon-nr", timeout=15000)
        r["mobil"] = pm.evaluate("""() => {
            const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
            return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    tinte_sub_24: ['em-bon-nr','em-bon-data'].filter(id => sub(document.getElementById(id).getBoundingClientRect()))};
        }""")
        r["axe_mobil"] = axe_scan.scaneaza(pm)
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("câmpuri:", r["campuri"])
    print("cererea de emitere (oprită):", r["cerere"], "· poarta de stoc afișată:", r["poarta_stoc_afisata"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:200], "· axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:200])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
