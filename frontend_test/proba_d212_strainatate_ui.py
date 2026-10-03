# -*- coding: utf-8 -*-
"""PROBA UI D212 Etapa 5c: lista „Venituri din străinătate” din formularul Declarației unice.

Traseul real din ecranul Declarații (firma implicită a contului de probă, `w_auth`): tip D212, anul 2025 -> formularul ->
identitate -> „+ adaugă” fără țară (refuz pe câmp) -> la fiecare categorie se arată doar câmpurile ei -> trei venituri
(Germania cu credit, Franța pe scutire, Italia titluri) -> ștergerea unuia -> Regenerează -> XML-ul are o secțiune `<cap14`
pe sursă, bifa121, creditul plafonat, DUK. Plus A11Y: axe desktop + telefon. Rulează cu app viu pe PROBA_BAZA (8011).
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

IESIRE = os.path.join(HERE, "proba_d212_strainatate_ui.json")
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
    pg.wait_for_selector("#d212-s-add", timeout=20000)


def _vizibile(pg):
    return pg.evaluate("""() => [...document.querySelectorAll('#dec-d212-form [id^="d212-s-"]')]
        .filter(e => e.closest('label') && e.closest('label').offsetParent !== null).map(e => e.id).sort()""")


def _venit(pg, cat, metoda="", **v):
    pg.select_option("#d212-s-cat", cat)
    pg.dispatch_event("#d212-s-cat", "change")
    pg.select_option("#d212-s-metoda", metoda)
    for k, val in v.items():
        pg.fill("#d212-s-" + k, str(val))
    pg.click("#d212-s-add")
    pg.wait_for_timeout(300)


def _randuri(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#dec-d212-form .d212-s-del')].length")


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
        pg.click("#d212-s-add")                                                 # fără țară -> refuz pe câmp
        pg.wait_for_timeout(300)
        r["eroare_tara"] = pg.evaluate("""() => { const e = document.querySelector('.msg-eroare[data-camp="d212-s-tara"]');
                                              return e ? e.innerText : ''; }""")
        r["campuri"] = {}
        for cat in ("2027", "2003", "2012", "2018", "2016", "2025", "2013", "2029", "2020", "2015"):
            pg.select_option("#d212-s-cat", cat)
            pg.dispatch_event("#d212-s-cat", "change")
            r["campuri"][cat] = _vizibile(pg)
        _venit(pg, "2027", "1", tara="DE", brut=80000, chelt=20000, platit=4000)
        _venit(pg, "2004", "2", tara="FR", brut=30000, platit=5000)
        _venit(pg, "2012", "", tara="IT", castig=6000, pp=9000)
        r["randuri_dupa_trei"] = _randuri(pg)
        pg.click("#dec-d212-form .d212-s-del[data-idx='2']")
        pg.wait_for_timeout(300)
        r["randuri_dupa_stergere"] = _randuri(pg)
        r["identitate_pastrata"] = pg.input_value("#d212-cnp") == CNP
        _venit(pg, "2012", "", tara="IT", castig=6000, pp=9000)
        pg.click("#d212-regen")
        pg.wait_for_timeout(9000)
        xml = pg.evaluate("""() => [...document.querySelectorAll('pre.dec-xml-pre')].map(e => e.textContent || '').join('\\n')""")
        r["sectiuni_cap14"] = re.findall(r'<cap14\b[^>]*str_categ_venit="(\d+)"', xml)
        r["bifa121"] = bool(re.search(r'bifa121="1"', xml))
        r["credite"] = re.findall(r'str_credit_fiscal="(\d+)"', xml)
        r["de_plata"] = re.findall(r'str_dif_impozit_datorat="(\d+)"', xml)
        corp = pg.evaluate("() => document.body.innerText")
        r["duk_text"] = (re.search(r"(?i)(DUK[^\n]{0,120})", corp) or [""])[0][:160] if re.search(r"(?i)DUK", corp) else ""
        r["axe_desktop"] = axe_scan.scaneaza(pg)
        ctx.close()

        m = b.new_context(**pw.devices["Pixel 5"])
        m.add_init_script(w_auth.INIT)
        pm = m.new_page()
        _formular(pm)
        _venit(pm, "2027", "1", tara="DE", brut=80000, chelt=20000, platit=4000)
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
    print("eroare țară:", repr(r["eroare_tara"][:120]))
    for cat, c in r["campuri"].items():
        print("câmpuri la %s: %s" % (cat, c))
    print("rânduri: 3 adăugate ->", r["randuri_dupa_trei"], "· după ștergere ->", r["randuri_dupa_stergere"],
          "· identitate păstrată:", r["identitate_pastrata"])
    print("xml: cap14 %s · bifa121=%s · credite %s · de plată %s ·" % (r["sectiuni_cap14"], r["bifa121"], r["credite"], r["de_plata"]), r["duk_text"])
    print("axe desktop:", json.dumps(r["axe_desktop"], ensure_ascii=False)[:300])
    print("axe mobil:", json.dumps(r["axe_mobil"], ensure_ascii=False)[:300])
    print("mobil:", r["mobil"])


if __name__ == "__main__":
    main()
