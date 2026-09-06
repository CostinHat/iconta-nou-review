# -*- coding: utf-8 -*-
"""PROBA arborelui de navigare al asistentului (06.09.2026) — pe ARBORELE DE RANDARE, in browser.

DE CE O PROBA SEPARATA, si nu o intrare in `nav_ecrane.ECRANE`. Cele trei unelte vizuale plimba un
SINGUR cont (patronul de cabinet) peste lista de ecrane; desktopul asistentului cere alt ROL, iar
`app.js` alege desktopul din `sesiune.rol()` la pornirea filei — deci un al doilea cont inseamna un
al doilea CONTEXT de browser, nu un ecran in plus. Hamul stie deja s-o faca (`w_auth.new_page(pw,
email)`); uneltele de lista, nu.

CE PROBEAZA, si de ce asa. Cerinta lui Costin: *„Fiecare nod duce la același loc unde duce cardul
corespunzător azi."* Asta NU se poate proba citind sursa — `"randeazaControl" in text` e adevarat si
intr-o lume in care nodul nu cheama nimic. Se probeaza APASAND: se deschide fereastra din nod, i se
citeste titlul, se inchide, se apasa cardul, se citeste iar. Doua drumuri, acelasi capat.

Ordinea se citeste tot din arborele de randare: secventa `data-nod` din panou fata de secventa
`data-cheie` din grila. Daca cele doua liste s-ar despica vreodata, egalitatea cade.
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

CONT = "asistent@prisma-cont.test"
IESIRE = os.path.join(HERE, "proba_r175_arbore_asistent.json")


def _desktop(pg):
    pg.goto(w_auth.BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore", timeout=20000)
    pg.wait_for_timeout(600)


def _secvente(pg):
    noduri = pg.eval_on_selector_all(".asi-arbore .asi-nod", "els => els.map(e => e.dataset.nod)")
    carduri = pg.eval_on_selector_all(".cab-grila .cab-card-sinteza",
                                      "els => els.map(e => e.dataset.cheie)")
    grupe = pg.eval_on_selector_all(".asi-arbore .asi-grup-titlu", "els => els.map(e => e.textContent)")
    return noduri, carduri, grupe


def _titlu_din_nod(pg, cheie):
    _desktop(pg)
    pg.click(".asi-nod[data-nod='%s']" % cheie, timeout=8000)
    pg.wait_for_selector(".fereastra-corp", timeout=20000)
    pg.wait_for_timeout(500)
    return pg.inner_text(".fereastra-fir").strip()


def _titlu_din_card(pg, cheie):
    _desktop(pg)
    pg.click("button.cab-card:has([data-cheie='%s'])" % cheie, timeout=8000)
    pg.wait_for_selector(".fereastra-corp", timeout=20000)
    pg.wait_for_timeout(500)
    return pg.inner_text(".fereastra-fir").strip()


def main():
    # AMPRENTA UI, ca proba sa nu imbatraneasca tacut: garda o compara cu cea de acum, deci un
    # `asistent.js` schimbat dupa proba face proba INVALIDA, nu doar veche.
    raport = {"cont": CONT, "ui_hash": ui_hash(), "perechi": [], "axe": {}, "mobil": {}}
    with sync_playwright() as pw:
        b, pg = w_auth.new_page(pw, CONT)
        _desktop(pg)

        noduri, carduri, grupe = _secvente(pg)
        raport["noduri"] = noduri
        raport["carduri"] = carduri
        raport["grupe"] = [g.strip() for g in grupe]
        raport["ordine_identica"] = (noduri == carduri)

        # axe pe desktopul asistentului (cu arborele randat)
        _viol, _title_only = axe_scan.scaneaza(pg)
        raport["axe"] = {"violari": _viol, "title_only": _title_only}

        # fiecare nod, fata in fata cu cardul lui — apasate, nu citite
        for k in noduri:
            tn = _titlu_din_nod(pg, k)
            tc = _titlu_din_card(pg, k)
            raport["perechi"].append({"cheie": k, "din_nod": tn, "din_card": tc, "la_fel": tn == tc})
        b.close()

        # MOBIL (Pixel 5): arborele nu dispare, si nimic nu se revarsa orizontal
        b2 = pw.chromium.launch(headless=True)
        ctx = b2.new_context(**pw.devices["Pixel 5"])
        ctx.add_init_script(w_auth.init_pentru(CONT))
        m = ctx.new_page()
        _desktop(m)
        raport["mobil"] = {
            "arbore_vizibil": m.is_visible(".asi-arbore"),
            "noduri": m.eval_on_selector_all(".asi-arbore .asi-nod", "els => els.length"),
            "revarsare_x": m.evaluate("document.documentElement.scrollWidth > "
                                      "document.documentElement.clientWidth"),
            "tinte_sub_24": m.eval_on_selector_all(
                ".asi-nod", "els => els.filter(e => e.getBoundingClientRect().height < 24).length"),
        }
        b2.close()

    json.dump(raport, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ordine identica arbore/carduri:", raport["ordine_identica"])
    print("grupe:", raport["grupe"])
    print("noduri:", raport["noduri"])
    rele = [p for p in raport["perechi"] if not p["la_fel"]]
    print("perechi nod/card care NU duc in acelasi loc:", len(rele))
    for p in rele:
        print("   ", p)
    # `title_only` e un DICT cu trei liste ({strict, glif, extra}); `len(dict)` ar fi dat mereu 3,
    # adica un instrument care raporteaza „3 gasite" peste zero gasite. Se numara CONTINUTUL.
    _to = raport["axe"]["title_only"] or {}
    _n_to = sum(len(v) for v in _to.values()) if isinstance(_to, dict) else len(_to)
    print("axe violari:", len(raport["axe"]["violari"] or []), "· title-only:", _n_to)
    print("mobil:", raport["mobil"])
    print("JSON:", IESIRE)


if __name__ == "__main__":
    main()
