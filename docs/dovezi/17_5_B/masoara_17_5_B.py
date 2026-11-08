# -*- coding: utf-8 -*-
"""Măsurătoarea lotului 17.5-B (pct.3): cele nouă ferestre de lucru la 603×590 și 1366×768, deschise ca în e2e_pilot_x09.py.
Comandă: ./venv/bin/python docs/dovezi/17_5_B/masoara_17_5_B.py <fișier_ieșire>   (serverul 8019 pornit din arborele măsurat, baza restaurată; mediul: test.env și cheia de sesiune din api_keys.env, ca în scripts/e2e_poarta.py::_env_test)
Coloane: fereastră | rezoluție | luna | corp (px) | prag (px) | zone (px) | locuri de derulare | elemente ieșite | derulări orizontale (numai Casă).
JS_DERULARI vine din e2e_pilot_x06.py, JS_IESITE și JS_ORIZONTALE din e2e_pilot_x09.py, fără modificări."""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, os.path.join(RAD, "frontend_test", "e2e"))   # ultimul pus = primul căutat: conftest.py al plasei, nu cel din rădăcină

from conftest import BAZA, sesiune   # noqa: E402
from e2e_pilot_x06 import JS_DERULARI   # noqa: E402
from e2e_pilot_x09 import (ADMIN, F1_CARDURI, JS_DESCHIDE_CARD, JS_IESITE, JS_ORIZONTALE, TOP,   # noqa: E402
                           _incarca_parcurs_17_1)


def _deschide(pg, parcurs, firma, sel):
    """Ca _card din e2e_pilot_x09.py, dar întoarce și luna la care s-a măsurat."""
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return None, "-"
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector("#fa-facturi", state="detached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    luna = "-"
    buton = pg.locator(TOP + ".fereastra-corp button", has_text="← luna")
    try:
        buton.first.wait_for(state="visible", timeout=3000)   # fereastra își desenează butoanele după ce firma dispare; e2e_pilot_x09.py nu așteaptă
    except Exception:   # noqa: BLE001 — fereastră fără „← luna”
        pass
    if buton.count():
        buton.first.click(timeout=10000)
        pg.wait_for_timeout(1500)
        luna = "10/2026"
    return _masoara(pg), luna


def _masoara(pg):
    pg.wait_for_timeout(900)
    return {"derulari": pg.evaluate(JS_DERULARI), "iesite": pg.evaluate(JS_IESITE), "orizontale": pg.evaluate(JS_ORIZONTALE)}


def _rand(nume, w, h, luna, m):
    if m is None or not m["derulari"] or not m["derulari"].get("fereastra"):
        return "%s | %dx%d | %s | fereastra nu s-a deschis" % (nume, w, h, luna)
    d = m["derulari"]
    prag = round((0.4 if w <= 700 else 0.5) * d["corpInaltime"])
    zone = ",".join(str(z["inaltime"]) for z in d["zone"]) or "fără zonă"
    derulante = "%d (%s)" % (len(d["derulante"]), ", ".join(d["derulante"]) or "-")
    iesite = "%d (%s)" % (len(m["iesite"]), "; ".join(m["iesite"][:4]) or "-")
    oriz = str(m["orizontale"]) if nume.startswith("Casă") else "n/a"
    return " | ".join([nume, "%dx%d" % (w, h), luna, str(d["corpInaltime"]), "%d%s" % (prag, "" if w <= 700 else " (informativ, 816)"), zone, derulante, iesite, oriz])


def main(iesire):
    from playwright.sync_api import sync_playwright
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    randuri = ["# ./venv/bin/python docs/dovezi/17_5_B/masoara_17_5_B.py %s" % os.path.basename(iesire),
               "# fereastră | rezoluție | luna | corp (px) | prag (px) | zone (px) | locuri de derulare | elemente ieșite | derulări orizontale (Casă)"]
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1366, "height": 768})
        ctx.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        ctx.add_init_script(sesiune(ADMIN))
        pg = ctx.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        for (w, h) in ((603, 590), (1366, 768)):
            pg.set_viewport_size({"width": w, "height": h})
            for sel, nume in F1_CARDURI:
                m, luna = _deschide(pg, parcurs, "F1 Comert Stoc", sel)
                randuri.append(_rand(nume, w, h, luna, m))
            m, luna = _deschide(pg, parcurs, "F5 SRL Salariati", "#fa-salariati")
            randuri.append(_rand("Salariați F5", w, h, luna, m))
            try:
                pg.locator(TOP + "button, " + TOP + "tr, " + TOP + "td", has_text="Ionescu Vasile").first.click(timeout=10000)
                m = _masoara(pg)
            except Exception:   # noqa: BLE001
                m = None
            randuri.append(_rand("Fișa salariatului Ionescu F5", w, h, "-", m))
        br.close()
    with open(iesire, "w", encoding="utf-8") as f:
        f.write("\n".join(randuri) + "\n")
    print("\n".join(randuri))


if __name__ == "__main__":
    main(sys.argv[1])
