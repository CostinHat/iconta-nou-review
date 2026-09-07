# -*- coding: utf-8 -*-
"""PROBA celor 50 de declaratii pe ecranul PUBLIC de logare (07.09.2026).

CE PROBEAZA, si de ce in browser: „toate cele 50, fara bara de derulare, incapand vizibil" e o
afirmatie despre RANDARE. Nu se poate proba citind JS-ul — numarul de celule si inaltimea lor se
stiu abia dupa asezare. Deci: se deschide ecranul de logare (neautentificat), se apasa butonul, si
se masoara pe arborele de randare.

  NUMAR      cate celule sunt efectiv in grila, fata de cate tipuri are `DECLARATII`
  DERULARE   grila si fereastra NU trebuie sa aiba continut peste marginile lor (scrollHeight >
             clientHeight ar insemna ca ceva e ascuns sub o bara)
  VIZIBILE   fiecare celula trebuie sa aiba dreptunghi cu inaltime > 0 SI sa fie in viewport
  EXPLICATIA `?` chiar scrie ceva, si scrie ALTCEVA pentru doua declaratii diferite (altfel ar
             merge si cu un text fix)
  A11Y       axe pe desktop, si tinta de atingere >= 24px pe telefon
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
from vizual.acoperire_hash import ui_hash  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
from core import declaratii_api as da  # noqa: E402

IESIRE = os.path.join(HERE, "proba_decl50.json")
ASTEPTAT = len(da.DECLARATII)


def _deschide(pg):
    pg.goto(w_auth.BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_timeout(900)
    # butonul e „Vezi tot", nu titlul cardului — prima forma a probei apasa titlul si nu deschidea
    # nimic, apoi cauta un card care nu aparuse. Masurat pe pagina, nu presupus.
    pg.click("button:has-text('Vezi tot')", timeout=15000)
    pg.wait_for_selector(".func-card-decl", timeout=15000)
    pg.click(".func-card-decl")
    pg.wait_for_selector(".decl-grila", timeout=15000)
    pg.wait_for_timeout(400)


def main():
    r = {"asteptat": ASTEPTAT, "ui_hash": ui_hash()}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        pg = ctx.new_page()
        _deschide(pg)

        r["celule"] = pg.eval_on_selector_all(".decl-chip", "e => e.length")
        r["coduri"] = pg.eval_on_selector_all(".decl-cod", "e => e.map(x => x.textContent.trim())")
        r["butoane_ce"] = pg.eval_on_selector_all(".decl-ce", "e => e.length")
        r["derulare"] = pg.evaluate(
            "() => { const g = document.querySelector('.decl-grila'),"
            "        c = document.querySelector('.fereastra-corp');"
            "  return { grila: g.scrollHeight > g.clientHeight + 1,"
            "           corp: c.scrollHeight > c.clientHeight + 1,"
            "           pagina: document.documentElement.scrollHeight >"
            "                   document.documentElement.clientHeight + 1 }; }")
        r["invizibile"] = pg.evaluate(
            "() => Array.from(document.querySelectorAll('.decl-chip')).filter(e => {"
            "  const b = e.getBoundingClientRect();"
            "  return b.height < 1 || b.bottom > innerHeight || b.right > innerWidth; })"
            "  .map(e => e.textContent.trim()).slice(0, 8)")

        # `?` chiar explica, si explica DIFERIT
        texte = []
        for cod in ("D100", "D406"):
            pg.click(".decl-ce[data-tip='%s']" % cod)
            pg.wait_for_timeout(200)
            texte.append(pg.inner_text(".decl-explicatie").strip())
        r["explicatii"] = texte
        r["explicatii_diferite"] = len(set(texte)) == 2

        v, t = axe_scan.scaneaza(pg)
        r["axe"] = {"violari": v, "title_only": t}
        b.close()

        # MOBIL
        b2 = pw.chromium.launch(headless=True)
        c2 = b2.new_context(**pw.devices["Pixel 5"])
        m = c2.new_page()
        _deschide(m)
        r["mobil"] = {
            "celule": m.eval_on_selector_all(".decl-chip", "e => e.length"),
            "revarsare_x": m.evaluate("document.documentElement.scrollWidth >"
                                      " document.documentElement.clientWidth"),
            "tinte_sub_24": m.eval_on_selector_all(
                ".decl-ce", "e => e.filter(x => x.getBoundingClientRect().height < 24).length"),
        }
        b2.close()

    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("celule: %d / asteptat %d · butoane ?: %d" % (r["celule"], ASTEPTAT, r["butoane_ce"]))
    print("coduri lipsa:", sorted({d.upper() for d in da.DECLARATII} - set(r["coduri"])))
    print("derulare:", r["derulare"])
    print("celule netaiate/invizibile:", r["invizibile"] or "niciuna")
    print("explicatii diferite:", r["explicatii_diferite"])
    for t_ in r["explicatii"]:
        print("   ", t_[:100])
    print("axe violari:", len(r["axe"]["violari"] or []),
          "· title-only:", sum(len(x) for x in r["axe"]["title_only"].values()))
    print("mobil:", r["mobil"])
    print("JSON:", IESIRE)


if __name__ == "__main__":
    main()
