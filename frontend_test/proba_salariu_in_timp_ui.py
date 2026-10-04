# -*- coding: utf-8 -*-
"""PROBA UI — salariul în timp (decizia Costin 04.10.2026): zona „Salariu de bază · de la” din statul de plată.
Rulează cu app viu pe PROBA_BAZA (8011, baza de test), pe firma implicită a contului (`w_auth`, tenant_003).

Salariata 1 (Popescu Ana). Starea istoricului se citește înainte și se restaurează la final (rândurile adăugate de probă se
șterg). Pași:
  A. zona se deschide cu istoricul (ce date sunt ocupate);
  B. dată înainte de angajare -> refuz pe câmpul „de la” (aria-invalid), suma tastată RĂMÂNE în casetă;
  C. dată deja în istoric -> refuz pe câmp + butonul „Înlocuiește salariul de la …”; casetele rămân cum au fost tastate;
  D. dată nouă validă -> salvat (zona se închide), intrarea apare în istoric;
  E. axe pe zona cu refuz (desktop) + telefon (Pixel 5): revărsare orizontală, ținte sub 24px, axe.
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
from core import db  # noqa: E402

IESIRE = os.path.join(HERE, "proba_salariu_in_timp_ui.json")
SCHEMA, SID, DATA_NOUA = "tenant_003", 1, "2026-10-15"
MOBIL_JS = """(sel) => {
    const z = document.querySelector(sel) || document.body;
    const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
    const el = [...z.querySelectorAll('button,input,select')].filter(e => e.offsetParent !== null);
    return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            tinte_sub_24: el.filter(e => sub(e.getBoundingClientRect())).map(e => e.id || e.textContent.trim().slice(0, 20))};
}"""


def _istoric():
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT valabil_din::text, salariu_brut FROM %s.salariu_istoric WHERE salariat_id=%%s ORDER BY 1" % SCHEMA,
                    (SID,))
        return [(d, float(s)) for d, s in cur.fetchall()]


def _restaureaza(inainte):
    with db.get_conn() as c:
        with c.cursor() as cur:
            pastrate = [d for d, _s in inainte]
            cur.execute("DELETE FROM %s.salariu_istoric WHERE salariat_id=%%s AND NOT (valabil_din::text = ANY(%%s))" % SCHEMA,
                        (SID, pastrate))
            for d, s in inainte:
                cur.execute("UPDATE %s.salariu_istoric SET salariu_brut=%%s WHERE salariat_id=%%s AND valabil_din=%%s" % SCHEMA,
                            (s, SID, d))
        c.commit()


def _zona(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-salariati")
    pg.wait_for_selector("button[data-salariu='%s']" % SID, timeout=20000)
    pg.click("button[data-salariu='%s']" % SID)
    pg.wait_for_selector("#salariu-save", timeout=8000)
    pg.wait_for_timeout(1200)


def main():
    db.init_pool()
    inainte = _istoric()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT data_angajare::text FROM %s.salariati WHERE id=%%s" % SCHEMA, (SID,))
        angajare = cur.fetchone()[0]
    r = {"istoric_inainte": inainte, "angajare": angajare}
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            ctx = b.new_context(viewport={"width": 1280, "height": 1400})
            ctx.add_init_script(w_auth.INIT)
            pg = ctx.new_page()
            _zona(pg)
            r["A_istoric_afisat"] = (pg.text_content("#salariu-istoric") or "").strip()
            # B
            pg.fill("#salariu-input", "5100")
            pg.fill("#salariu-data", "2019-01-01")
            pg.click("#salariu-save")
            pg.wait_for_timeout(2500)
            r["B_aria_invalid"] = pg.get_attribute("#salariu-data", "aria-invalid")
            r["B_suma_pastrata"] = pg.input_value("#salariu-input")
            r["B_data_pastrata"] = pg.input_value("#salariu-data")
            # C
            pg.fill("#salariu-data", inainte[0][0])
            pg.click("#salariu-save")
            pg.wait_for_timeout(2500)
            r["C_aria_invalid"] = pg.get_attribute("#salariu-data", "aria-invalid")
            r["C_buton_inlocuire"] = (pg.text_content("#salariu-inlocuieste") or "").strip() if pg.locator(
                "#salariu-inlocuieste").count() else None
            r["C_suma_pastrata"] = pg.input_value("#salariu-input")
            r["axe_refuz"] = axe_scan.scaneaza(pg)
            # D
            pg.fill("#salariu-data", DATA_NOUA)
            pg.click("#salariu-save")
            pg.wait_for_timeout(3000)
            r["D_zona_inchisa"] = pg.locator("#salariu-save").count() == 0
            r["D_istoric_dupa"] = _istoric()
            ctx.close()
            # E — telefon
            m = b.new_context(**pw.devices["Pixel 5"])
            m.add_init_script(w_auth.INIT)
            pm = m.new_page()
            _zona(pm)
            r["mobil_zona"] = pm.evaluate(MOBIL_JS, "#sp-salariu-zona")
            r["axe_mobil"] = axe_scan.scaneaza(pm)
            b.close()
    finally:
        _restaureaza(inainte)
        r["istoric_restaurat"] = _istoric() == inainte
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("A. istoric afișat: %r" % r.get("A_istoric_afisat"))
    print("B. înainte de angajare (%s): aria-invalid=%r · suma păstrată=%r · data păstrată=%r" % (
        angajare, r.get("B_aria_invalid"), r.get("B_suma_pastrata"), r.get("B_data_pastrata")))
    print("C. dată ocupată: aria-invalid=%r · buton=%r · suma păstrată=%r" % (
        r.get("C_aria_invalid"), r.get("C_buton_inlocuire"), r.get("C_suma_pastrata")))
    print("D. dată nouă %s: zona închisă=%r · istoric=%r" % (DATA_NOUA, r.get("D_zona_inchisa"), r.get("D_istoric_dupa")))
    for k in ("axe_refuz", "axe_mobil"):
        print("%s: %s" % (k, json.dumps(r.get(k), ensure_ascii=False)[:200]))
    print("mobil zona:", r.get("mobil_zona"), "· istoric restaurat:", r.get("istoric_restaurat"))


if __name__ == "__main__":
    main()
