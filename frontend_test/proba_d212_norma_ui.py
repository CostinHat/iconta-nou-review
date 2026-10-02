# -*- coding: utf-8 -*-
"""PROBA UI D212 Etapa 3: lista „Venit pe normă de venit” din formularul Declarației unice.

Traseul real din ecranul Declarații (firma implicită a contului de probă, `w_auth`): tip D212 -> formularul ->
identitate -> „+ adaugă activitatea” fără normă (refuz pe câmp) -> două activități -> ștergerea uneia (lista se
re-randează din model, DS cap.24) -> din nou două -> Regenerează -> XML-ul conține două secțiuni `<cap12`, bifa112=1.
Plus A11Y: axe desktop + telefon (ținte >= 24px, fără derulare orizontală). Rulează cu app viu pe PROBA_BAZA (8011).
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

IESIRE = os.path.join(HERE, "proba_d212_norma_ui.json")
CNP = "1800101221144"   # cifra de control verificată


def _formular(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000)
    pg.select_option("#dec-tip", "d212")
    pg.wait_for_timeout(500)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_selector("#d212-n-add", timeout=20000)


def _activitate(pg, **v):
    for k, sel in (("caen", "#d212-n-caen"), ("sediu", "#d212-n-sediu"), ("norma", "#d212-n-norma"),
                   ("ajust", "#d212-n-ajust"), ("inc", "#d212-n-inc"), ("scut", "#d212-n-scut")):
        pg.fill(sel, str(v.get(k, "")))
    pg.click("#d212-n-add")
    pg.wait_for_timeout(300)


def _randuri(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#dec-d212-form .d212-n-del')].length")


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1400})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        _formular(pg)
        for sel, v in (("#d212-cnp", CNP), ("#d212-nume", "POPESCU ION"), ("#d212-adr", "Bucuresti Sector 1")):
            pg.fill(sel, v)
            pg.dispatch_event(sel, "change")
        _activitate(pg, caen="9602")                                          # fără normă -> refuz pe câmp
        r["eroare_norma"] = pg.evaluate("""() => { const e = document.querySelector('.msg-eroare[data-camp="d212-n-norma"]');
                                              return e ? e.innerText : ''; }""")
        r["randuri_dupa_refuz"] = _randuri(pg)
        _activitate(pg, caen="9602", sediu="Bucuresti, Str. Lunga 1", norma=30000)
        _activitate(pg, caen="4520", norma=27000, ajust=24000, inc="2026-07-01", scut=20)
        r["randuri_dupa_doua"] = _randuri(pg)
        pg.click("#dec-d212-form .d212-n-del[data-idx='1']")
        pg.wait_for_timeout(300)
        r["randuri_dupa_stergere"] = _randuri(pg)
        r["identitate_pastrata"] = pg.input_value("#d212-cnp") == CNP
        _activitate(pg, caen="4520", norma=27000, ajust=24000, inc="2026-07-01", scut=20)
        pg.click("#d212-regen")
        pg.wait_for_timeout(9000)
        xml = pg.evaluate("""() => [...document.querySelectorAll('pre.dec-xml-pre')].map(e => e.textContent || '').join('\\n')""")
        r["sectiuni_cap12"] = len(re.findall(r"<cap12\b", xml))
        r["bifa112"] = bool(re.search(r'bifa112="1"', xml))
        r["impozite"] = re.findall(r'real_impozit="(\d+)"', xml)
        corp = pg.evaluate("() => document.body.innerText")
        r["duk_text"] = (re.search(r"(?i)(DUK[^\n]{0,120})", corp) or [""])[0][:160] if re.search(r"(?i)DUK", corp) else ""
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()

        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _formular(pm)
        _activitate(pm, caen="9602", norma=30000)
        r["mobil"] = pm.evaluate("""() => {
            const z = document.querySelector('#dec-d212-form');
            const tinta = e => (e.type === 'checkbox' && e.closest('label')) ? e.closest('label') : e;
            const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
            const el = [...z.querySelectorAll('button,input,select')];
            return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    tinte_sub_24: el.filter(e => sub(tinta(e).getBoundingClientRect())).map(e => e.id || e.className)};
        }""")
        r["axe_mobil"] = axe_scan.scaneaza(pm)
        b.close()
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("eroare normă:", repr(r["eroare_norma"][:120]), "· rânduri după refuz:", r["randuri_dupa_refuz"])
    print("rânduri: 2 adăugate ->", r["randuri_dupa_doua"], "· după ștergere ->", r["randuri_dupa_stergere"],
          "· identitate păstrată:", r["identitate_pastrata"])
    print("xml: cap12 x%d · bifa112=%s · impozite %s ·" % (r["sectiuni_cap12"], r["bifa112"], r["impozite"]), r["duk_text"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:300])
    print("axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:300])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
