# -*- coding: utf-8 -*-
"""REPROBARE R168 — etichetele celor 32 de formulare, citite DE PE ECRAN, nu din sursă.

Gardul din `core/test_diacritice_afisate.py` verifică SURSA. Aici se verifică **randarea**: se
deschide fiecare din cele 32 de operațiuni, se culeg toate etichetele de câmp (`.camp-eticheta`),
toate opțiunile de `<select>` și toate textele de ajutor, iar ce se culege trece prin **criteriul
gardului** (`_flag_js`) — proză, minuscule, zero diacritice, cuvânt din lista high-precision.

*Un `?v=` nepotrivit, un fișier nepublicat sau o etichetă construită la runtime nu se văd în sursă.*

NAVIGAREA E PE NUME, nu pe poziție, și cu RE-INTRARE în ecran de fiecare dată — lecția lotului 13:
pozițiile `data-op` se re-atribuie, iar un `go_back()` nu întoarce în meniul unui SPA. Prima formă a
probei ăsteia a căzut exact acolo, la a doua operațiune.

Nu apasă niciun buton de generare: doar deschide și citește. Nimic nu se scrie.
"""
import json
import os
import sys

_H = os.path.dirname(os.path.abspath(__file__))
_R = os.path.abspath(os.path.join(_H, "..", ".."))
sys.path.insert(0, os.path.join(_R, "frontend_test"))
sys.path.insert(0, _H)
sys.path.insert(0, _R)

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
import nav_ecrane  # noqa: E402
from core.test_diacritice_afisate import _flag_js  # noqa: E402

JS_OPERATIUNI = """
() => {
  const R = document.querySelector(".fereastra-corp") || document.body;
  const out = [];
  R.querySelectorAll("button[data-op]").forEach((e) => {
    const t = (e.textContent || "").trim().replace(/\\s+/g, " ");
    if (t) out.push(t);
  });
  return out;
}
"""

JS_TEXTE = """
() => {
  const R = document.querySelector(".fereastra-corp") || document.body;
  const out = [];
  R.querySelectorAll(".camp-eticheta").forEach(
    (e) => out.push(["eticheta", (e.textContent || "").replace("*", "").trim()]));
  R.querySelectorAll("option").forEach(
    (e) => out.push(["optiune", (e.textContent || "").trim()]));
  R.querySelectorAll(".camp-ajutor").forEach(
    (e) => out.push(["ajutor", (e.textContent || "").trim()]));
  R.querySelectorAll("button, h2, .pf-intro").forEach(
    (e) => out.push(["text", (e.textContent || "").trim().replace(/\\s+/g, " ")]));
  return out;
}
"""


def main():
    rez = {"baza": w_auth.BAZA, "formulare": 0, "texte": 0, "flagate": []}
    _toate = dict(list(nav_ecrane.ECRANE) + list(nav_ecrane.ECRANE_CAMPANIE))
    deschide = _toate["operatiuni"]

    with sync_playwright() as p:
        b, pg = w_auth.new_page(p)
        erori = []
        pg.on("pageerror", lambda e: erori.append(str(e)))
        deschide(pg)
        pg.wait_for_timeout(1400)
        nume_op = pg.evaluate(JS_OPERATIUNI)
        print("operatiuni gasite: %d" % len(nume_op))
        assert len(nume_op) >= 30, "gasite doar %d — navigarea a esuat" % len(nume_op)

        vazute = set()
        for nume in nume_op:
            deschide(pg)
            pg.wait_for_timeout(700)
            pg.get_by_role("button", name=nume, exact=True).first.click(timeout=6000)
            pg.wait_for_timeout(900)
            for (rol, t) in pg.evaluate(JS_TEXTE):
                if not t or (rol, t) in vazute:
                    continue
                vazute.add((rol, t))
                h = _flag_js(t)
                if h:
                    rez["flagate"].append({"operatiune": nume, "rol": rol, "text": t,
                                           "triggere": h})
            rez["formulare"] += 1
        rez["erori_js"] = erori
        b.close()

    rez["texte"] = len(vazute)
    print("formulare deschise: %d · texte distincte citite de pe ecran: %d · erori JS: %d"
          % (rez["formulare"], rez["texte"], len(rez.get("erori_js") or [])))
    for f in rez["flagate"]:
        print("  FARA DIACRITICE  [%s / %s] %r  <- %s"
              % (f["operatiune"], f["rol"], f["text"], ",".join(f["triggere"])))
    with open(os.path.join(_H, "proba_r168_etichete.json"), "w", encoding="utf-8") as fh:
        json.dump(rez, fh, ensure_ascii=False, indent=1)

    assert rez["formulare"] >= 30, "prea putine formulare deschise"
    # ANTI-VACUU: daca selectorii n-ar prinde nimic, o lista goala de flagate ar arata ca reusita.
    assert rez["texte"] > 200, "prea putine texte citite (%d) — selectorii nu vad ecranul" % rez["texte"]
    assert not rez["flagate"], "%d texte afisate fara diacritice" % len(rez["flagate"])
    print("\nOK: %d texte afisate distincte, niciunul fara diacritice." % rez["texte"])


main()
