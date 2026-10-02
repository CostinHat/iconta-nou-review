# -*- coding: utf-8 -*-
"""PROBA UI — fișa D212 de pe ecranul RIP după reparația CASS sub 6 salarii minime (02.10.2026).

Contul de test al cabinetului (`nav_ecrane.CONT_TEST`) -> firma de partidă simplă -> «Încasări/plăți» -> «Fișa D212».
Se citește răspunsul real al rutei `/rip/d212/{an}` (câmpurile `cass`), apoi ce scrie ecranul: nota veche
„neobligatoriu - sub 6 salarii minime” nu mai are voie să apară, iar când `diferenta_minim > 0` ecranul o arată.
Plus axe desktop + telefon pe ecranul RIP. Rulează cu app viu pe PROBA_BAZA (8011). Nu scrie nimic.
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

IESIRE = os.path.join(HERE, "proba_rip_cass_ui.json")


def _fisa(pg, raspunsuri):
    nav_ecrane.ecran_rip_pfa(pg)
    pg.on("response", lambda r: raspunsuri.append(r) if "/rip/d212/" in r.url else None)
    pg.click("#r-d212", timeout=8000)
    pg.wait_for_timeout(1500)


def _note(pg):
    return pg.evaluate("""() => { const t = document.body.innerText;
        return {veche: t.includes('neobligatoriu - sub 6 salarii minime'),
                diferenta: t.includes('baza minim\u0103 de 6 salarii minime')}; }""")


def _fisa_20000():
    """Răspunsul rutei pentru un venit net de 20.000 lei (2025), calculat de MOTORUL aplicației — servit ecranului prin
    interceptare, ca randarea notei să se probeze fără a scrie operațiuni în bază."""
    from core import d212_engine as e
    f = e.calculeaza_d212(30000, 10000, e.plafoane_an(2025))
    f.update(an=2025, salariu_minim=4050, cheltuieli_limitate_de_analizat=0, ciorne_nevalidate=0)
    return f


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        init = w_auth.init_pentru(nav_ecrane.CONT_TEST)
        ctx = b.new_context(viewport={"width": 1280, "height": 1200})
        ctx.add_init_script(init)
        pg = ctx.new_page()
        rasp = []
        _fisa(pg, rasp)
        date = rasp[-1].json() if rasp else {}
        r["cass_din_ruta"] = date.get("cass")
        r["note_date_reale"] = _note(pg)
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        # scenariul 2: același ecran, răspuns interceptat cu fișa unui venit net de 20.000 lei (sub 6 sm)
        f20 = _fisa_20000()
        pg.route("**/rip/d212/**", lambda route: route.fulfill(status=200, content_type="application/json",
                                                                body=json.dumps(f20)))
        pg.click("#r-d212", timeout=8000)
        pg.wait_for_timeout(1200)
        r["cass_20000"] = f20["cass"]
        r["note_20000"] = _note(pg)
        ctx.close()
        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(init)
        pm = m.new_page()
        _fisa(pm, [])
        r["mobil"] = pm.evaluate("""() => ({revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth})""")
        r["axe_mobil"] = axe_scan.scaneaza(pm)
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("cass din rută:", r["cass_din_ruta"])
    print("note pe datele reale:", r["note_date_reale"])
    print("fișa 20.000 (motor):", r["cass_20000"], "· note afișate:", r["note_20000"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:300])
    print("axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:300], "· mobil:", r["mobil"])


if __name__ == "__main__":
    main()
