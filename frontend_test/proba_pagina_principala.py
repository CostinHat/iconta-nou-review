# -*- coding: utf-8 -*-
"""PROBA paginii principale, la AMBELE roluri (comanda Costin 12.10.2026, verbatim în DECIZII) — pe arborele de randare, în browser.

Înlocuiește proba arborelui asistentului (R175, 06.09.2026): meniul din stânga s-a scos (231). Ce probează, pe contabilul-șef ȘI pe
asistent, fiecare în contextul lui de browser (`app.js` alege pagina din `sesiune.rol()`, deci al doilea rol = al doilea context):
  · 231 — aceeași STRUCTURĂ: sub conținutul paginii, exact banda de salut și grila de carduri; niciun meniu lateral (`nav`);
  · 225 — „Recomandă” și „Suport”: două benzi, una lângă alta (același rând), deasupra cardurilor, mai scunde decât un card;
  · 224 — cardul Control fiscal: un rând cu 4 buline și numărul fiecăreia, fără text; înălțimea lui = a celorlalte carduri;
  · axe (desktop) și telefonul (Pixel 5): nimic nu iese din ecran pe orizontală, benzile nu sunt ținte sub 24 px.
Rulare: pe instanța de PROBĂ (`PROBA_BAZA=http://127.0.0.1:8011`, baza de test), niciodată pe producție (8010).
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
from acoperire_hash import ui_hash  # noqa: E402

CONTURI = {"cabinet": w_auth.EMAIL_IMPLICIT, "asistent": "asistent@prisma-cont.test"}
IESIRE = os.path.join(HERE, "proba_pagina_principala.json")

_MASURA = """() => {
  const salut = document.querySelector('.cab-salut'), grila = document.querySelector('.cab-grila');
  const r = (e) => { const b = e.getBoundingClientRect(); return {top: Math.round(b.top), bottom: Math.round(b.bottom), h: Math.round(b.height)}; };
  const carduri = [...grila.querySelectorAll(':scope > .cab-card')];
  const control = grila.querySelector('[data-cheie="control"]');
  return {
    structura: [...salut.parentElement.children].map((e) => e.className),
    meniu_lateral: document.querySelectorAll('.cab-salut ~ nav, .asi-arbore, .asi-nod').length,
    benzi: [...salut.querySelectorAll('.cab-banda')].map((b) => ({titlu: b.innerText.trim(), ...r(b)})),
    grila_top: r(grila).top,
    inaltimi_carduri: carduri.map((c) => r(c).h),
    control: control ? {h: r(control.closest('.cab-card')).h, text: control.innerText.replace(/\\s+/g, ' ').trim(),
                         lumini: [...control.querySelectorAll('.cab-stare')].map((s) => s.dataset.stare),
                         randuri: new Set([...control.querySelectorAll('.cab-stare')].map((s) => Math.round(s.getBoundingClientRect().top))).size}
                     : null,
  };
}"""


def _acasa(pg):
    pg.goto(w_auth.BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila .cab-card", timeout=30000)
    pg.wait_for_function("() => { const z = document.querySelector('[data-cheie=\"control\"]'); return z && z.querySelector('.cab-semafor4'); }",
                         timeout=60000)
    pg.wait_for_timeout(600)


def main():
    # AMPRENTA UI: garda o compară cu cea de acum — un `cabinet.js` / `asistent.js` / `salut.js` / `stil.css` schimbat după probă face
    # proba INVALIDĂ, nu doar veche.
    raport = {"ui_hash": ui_hash(), "roluri": {}}
    with sync_playwright() as pw:
        for rol, cont in CONTURI.items():
            b, pg = w_auth.new_page(pw, cont)
            _acasa(pg)
            m = pg.evaluate(_MASURA)
            pg.screenshot(path=os.path.join(os.environ.get("PROBA_CAPTURI", "/tmp"), "proba_pagina_principala_%s.png" % rol), full_page=True)
            _viol, _title_only = axe_scan.scaneaza(pg)
            m["axe"] = {"violari": _viol, "title_only": _title_only}
            b.close()
            b2 = pw.chromium.launch(headless=True)
            ctx = b2.new_context(**pw.devices["Pixel 5"])
            ctx.add_init_script(w_auth.init_pentru(cont))
            t = ctx.new_page()
            _acasa(t)
            m["mobil"] = {
                "revarsare_x": t.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
                "benzi_sub_24": t.eval_on_selector_all(".cab-banda", "els => els.filter(e => e.getBoundingClientRect().height < 24).length"),
            }
            b2.close()
            raport["roluri"][rol] = m
    json.dump(raport, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for rol, m in raport["roluri"].items():
        _to = m["axe"]["title_only"] or {}
        print(rol, "· structura:", m["structura"], "· meniu lateral:", m["meniu_lateral"])
        print("   benzi:", [(x["titlu"], x["top"], x["h"]) for x in m["benzi"]], "· grila de la", m["grila_top"])
        print("   carduri (înălțimi):", m["inaltimi_carduri"], "· Control fiscal:", m["control"])
        print("   axe:", len(m["axe"]["violari"] or []), "· title-only:", sum(len(v) for v in _to.values()) if isinstance(_to, dict) else len(_to),
              "· mobil:", m["mobil"])
    print("JSON:", IESIRE)


if __name__ == "__main__":
    main()
