# -*- coding: utf-8 -*-
"""PROBA UI D394 op2 Î1 (decizia B): câmpul „Nr. bonuri fiscale” pe ecranul Raport Z.

Firma implicită a contului de probă (`w_auth`) -> cardul «Raport Z» -> completează tot în afară de numărul de bonuri ->
„Generează notă” -> refuz pe câmpul `z-bonuri` (cap.6), FĂRĂ cerere la server (nu scrie nimic). Plus axe desktop +
telefon (ținte ≥ 24px, fără derulare orizontală). Rulează cu app viu pe PROBA_BAZA (8011).
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
from vizual import axe_scan  # noqa: E402

IESIRE = os.path.join(HERE, "proba_raport_z_ui.json")


def _ecran(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-raportz")
    pg.wait_for_selector("#z-bonuri", timeout=15000)


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1200})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        _ecran(pg)
        cereri = []
        pg.on("request", lambda q: cereri.append(q.url) if "/horeca/raport-z" in q.url else None)
        for sel, v in (("#z-data", "2026-09-10"), ("#z-nui", "8000000101"), ("#z-nr", "0031"),
                       ("#z-21", "1210"), ("#z-num", "1210")):
            pg.fill(sel, v)
        pg.click("#z-salveaza")
        pg.wait_for_timeout(600)
        r["eroare_bonuri"] = pg.evaluate("""() => { const e = document.querySelector('.msg-eroare[data-camp="z-bonuri"]');
                                              return e ? e.innerText : ''; }""")
        r["cereri_la_server"] = len(cereri)
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()
        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _ecran(pm)
        r["mobil"] = pm.evaluate("""() => {
            const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
            const el = [...document.querySelectorAll('.fereastra-corp button, .fereastra-corp input')];
            return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    tinte_sub_24: el.filter(e => sub(e.getBoundingClientRect())).map(e => e.id || e.className)};
        }""")
        r["axe_mobil"] = axe_scan.scaneaza(pm)
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("eroare bonuri:", repr(r["eroare_bonuri"][:120]), "· cereri la server:", r["cereri_la_server"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:300])
    print("axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:300])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
