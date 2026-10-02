# -*- coding: utf-8 -*-
"""PROBA UI D212 Etapa 5: lista „Alte venituri ale persoanei” și câmpurile CASS 2.2 din formularul Declarației unice.

Traseul real din ecranul Declarații (firma implicită a contului de probă, `w_auth`): tip D212, anul 2025 -> formularul ->
identitate -> la fiecare categorie se arată doar câmpurile ei -> trei venituri (drepturi de autor, chirie, alte surse) ->
ștergerea unuia (lista se re-randează din model, DS cap.24) -> dividendele nete -> Regenerează -> XML-ul are o secțiune
`<cap11` pe sursă, CASS 2.2 pe treaptă, DUK. Plus A11Y: axe desktop + telefon. Rulează cu app viu pe PROBA_BAZA (8011).
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

IESIRE = os.path.join(HERE, "proba_d212_venituri_ui.json")
CNP = "1800101221144"   # cifra de control verificată


def _formular(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000)
    pg.select_option("#dec-tip", "d212")
    pg.fill("#dec-an", "2025")
    pg.dispatch_event("#dec-an", "change")
    pg.wait_for_timeout(500)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_selector("#d212-v-add", timeout=20000)


def _vizibile(pg):
    return pg.evaluate("""() => [...document.querySelectorAll('#dec-d212-form [id^="d212-v-"]')]
        .filter(e => e.closest('label') && e.closest('label').offsetParent !== null).map(e => e.id).sort()""")


def _venit(pg, cat, **v):
    pg.select_option("#d212-v-cat", cat)
    pg.dispatch_event("#d212-v-cat", "change")
    for k, val in v.items():
        pg.fill("#d212-v-" + k, str(val))
    pg.click("#d212-v-add")
    pg.wait_for_timeout(300)


def _randuri(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#dec-d212-form .d212-v-del')].length")


def main():
    r = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1600})
        ctx.add_init_script(w_auth.INIT)
        pg = ctx.new_page()
        _formular(pg)
        for sel, v in (("#d212-cnp", CNP), ("#d212-nume", "POPESCU ION"), ("#d212-adr", "Bucuresti Sector 1")):
            pg.fill(sel, v)
            pg.dispatch_event(sel, "change")
        r["campuri"] = {}
        for cat in ("1003", "1015", "1012", "1024"):
            pg.select_option("#d212-v-cat", cat)
            pg.dispatch_event("#d212-v-cat", "change")
            r["campuri"][cat] = _vizibile(pg)
        _venit(pg, "1003", brut=30000)
        _venit(pg, "1015", brut=24000, sediu="Bucuresti, Str. Lunga 3")
        _venit(pg, "1024", vimp=3000)
        r["randuri_dupa_trei"] = _randuri(pg)
        pg.click("#dec-d212-form .d212-v-del[data-idx='2']")
        pg.wait_for_timeout(300)
        r["randuri_dupa_stergere"] = _randuri(pg)
        r["identitate_pastrata"] = pg.input_value("#d212-cnp") == CNP
        _venit(pg, "1024", vimp=3000)
        pg.fill("#d212-c-div", "10000")
        pg.dispatch_event("#d212-c-div", "change")
        pg.click("#d212-regen")
        pg.wait_for_timeout(9000)
        xml = pg.evaluate("""() => [...document.querySelectorAll('pre.dec-xml-pre')].map(e => e.textContent || '').join('\\n')""")
        r["sectiuni_cap11"] = re.findall(r'<cap11\b[^>]*categ_venit="(\d+)"', xml)
        r["impozite"] = re.findall(r'impozit11="(\d+)"', xml)
        r["cass22"] = {k: (re.search(r'\b%s="([^"]+)"' % k, xml) or [None, None])[1]
                       for k in ("bifa_cass_real", "cass_total_ven", "cass_baza", "cass_datorat", "dif_de_plata")}
        corp = pg.evaluate("() => document.body.innerText")
        r["duk_text"] = (re.search(r"(?i)(DUK[^\n]{0,120})", corp) or [""])[0][:160] if re.search(r"(?i)DUK", corp) else ""
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()

        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _formular(pm)
        _venit(pm, "1015", brut=24000)
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
    for cat, c in r["campuri"].items():
        print("câmpuri la %s: %s" % (cat, c))
    print("rânduri: 3 adăugate ->", r["randuri_dupa_trei"], "· după ștergere ->", r["randuri_dupa_stergere"],
          "· identitate păstrată:", r["identitate_pastrata"])
    print("xml: cap11 %s · impozite %s · CASS 2.2 %s ·" % (r["sectiuni_cap11"], r["impozite"], r["cass22"]), r["duk_text"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:300])
    print("axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:300])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
