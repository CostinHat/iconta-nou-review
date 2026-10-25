# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fe3] Regula nouă a verificatorului — ANTET_SCUND (C164, DS cap.9 v2.103 „Antetul documentului pe ecranul scund”).

Comanda Costin 12.3 pct.4, verbatim: „C164: pe ecranele scunde, antetul detaliului facturii se strânge pe un rând (număr, client, total,
stare SPV); acțiunea principală rămâne fixă jos (clasa 285).”

Logica REALĂ, scoasă din `verificator_conformitate.py` cu `ast` (tiparul `core/test_lot12_ui2_verificator.py`): fișierele reale sunt
curate; fiecare jumătate a regulii pică pe o mutație a fișierului real (`stil.css` / `facturi_ecran.js`) sau pe un fragment rău.

Temei: N/A — regulă de interfață (DS cap.9 v2.103).
"""
import ast
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _citeste(rel):
    return io.open(os.path.join(_RAD, rel), encoding="utf-8").read()


@pytest.fixture(scope="module")
def regula():
    arb = ast.parse(_citeste("verificator_conformitate.py"))
    noduri = [n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name == "analiza_lot12"]
    assert len(noduri) == 1, "ANTI-VACUU: analiza_lot12 lipsește din verificator"
    ns = {"re": re}
    exec(compile(ast.Module(body=noduri, type_ignores=[]), "verificator_conformitate.py", "exec"), ns)
    return lambda fis, css: [r for r in ns["analiza_lot12"](fis, css) if r[2] == "ANTET_SCUND"]


@pytest.fixture(scope="module")
def reale():
    fis = {}
    for d in ("static/js/ecrane", "static/js"):
        for f in sorted(os.listdir(os.path.join(_RAD, d))):
            if f.endswith(".js") and ".bak" not in f and f not in fis:
                fis[f] = _citeste(os.path.join(d, f))
    assert re.search(r'class="fd-antet rezumat-fix"', fis.get("facturi_ecran.js") or ""), "ANTI-VACUU: detaliul facturii lipsește"
    return _citeste("static/stil.css"), fis


def test_fisierele_reale_sunt_curate(regula, reale):
    css, fis = reale
    assert regula(fis, css) == []


@pytest.mark.parametrize("ancora, inlocuire, ce", [
    ("@media (max-height: 700px), (max-width: 560px) { :root { --antet-scund: 1; } }", "", "media query-ul"),
    (":root { --antet-scund: 0; }", "", "valoarea de bază"),
    (".fd-antet-scurt { display: flex; align-items: baseline; gap: 12px; flex-wrap: nowrap;",
     ".fd-antet-scurt { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;", "se poate rupe"),
])
def test_stil_fara_forma_ecranului_scund_e_prins(regula, reale, ancora, inlocuire, ce):
    css, fis = reale
    assert css.count(ancora) == 1, ancora
    rez = regula(fis, css.replace(ancora, inlocuire))
    assert [r[0] for r in rez] == ["stil.css"] and ce in rez[0][3], rez


@pytest.mark.parametrize("ancora, inlocuire", [
    ("  aseazaAntetul(corp);   // [lotul 12, C164]", "  // fără așezarea ecranului scund"),
    ('<div class="fd-bara-actiuni" id="fd-bara-actiuni"></div>', ""),
])
def test_detaliul_facturii_fara_forma_ecranului_scund_e_prins(regula, reale, ancora, inlocuire):
    css, fis = reale
    js = fis["facturi_ecran.js"]
    assert js.count(ancora) == 1, ancora
    rez = regula(dict(fis, **{"facturi_ecran.js": js.replace(ancora, inlocuire)}), css)
    assert len(rez) == 1 and rez[0][0] == "facturi_ecran.js" and js.split("\n")[rez[0][1] - 1].count("fd-antet rezumat-fix") == 1, rez


_RAU = """function detaliuDoc(corp) {
  const scund = window.matchMedia("(max-height: 650px)").matches;
  corp.innerHTML = `<div class="fd-antet rezumat-fix"><h2>Doc</h2><button class="buton-secundar" id="x">PDF</button></div><table></table>`;
}"""
_BUN = """function detaliuDoc(corp) {
  corp.innerHTML = `<div class="fd-antet rezumat-fix"><h2>Doc</h2><span class="fd-stare">emis</span></div><table></table>`;
}"""


def test_fragmente_pragul_in_js_si_antetul_cu_actiuni_sunt_prinse(regula, reale):
    css, _fis = reale
    rau = regula({"proba.js": _RAU}, css)
    assert sorted(r[1] for r in rau) == [2, 3], rau            # pragul în JS (linia 2) și antetul cu butoane fără forma scundă (linia 3)
    assert regula({"proba.js": _BUN}, css) == []               # antetul fără acțiuni (ca factura preluată): nu se cere
