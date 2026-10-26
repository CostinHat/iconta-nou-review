# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), zona DS — regulile noi ale verificatorului (analiza `lot13`): 655 (SUMA_CITITA_BRUT, SUMA_TEXT), 673
(FEREASTRA_INLINE), 674 (ACTIUNE_FARA_BUTON), 675 (BUTON_ASCUNS), 676 (LISTA_SCURTA), 504 (PRECOMPLETARE), 509 (GRILA_INLINE).

Logica REALĂ, scoasă din `verificator_conformitate.py` cu `ast` (tiparul `core/test_lot12_ui2_verificator.py`): fragmentul rău e prins,
cel bun nu; mecanismele comune ale fișierelor reale (api.js, navigator.js, stil.css, core/numere.py) există — fără ele regula n-ar putea
fi respectată; fișierele zonei DS (api.js, navigator.js, coaja.js, app.js, sesiune.js, ciorna_formular.js, drepturi.js, cautare.js) sunt
curate. Locurile din fișierele altor zone NU se scutesc: le listează raportul lotului, iar verificatorul rămâne roșu pe ele până le repară
proprietarii (comanda 13.1: „se repară peste tot, cu lista locurilor în raport”).

Temei: N/A — reguli de interfață (DS cap.1, cap.2a, cap.6, cap.9, v2.104).
"""
import ast
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISIERE_DS = ("api.js", "navigator.js", "coaja.js", "app.js", "sesiune.js", "ciorna_formular.js", "drepturi.js", "cautare.js")


def _citeste(rel):
    return io.open(os.path.join(_RAD, rel), encoding="utf-8").read()


@pytest.fixture(scope="module")
def analiza():
    arb = ast.parse(_citeste("verificator_conformitate.py"))
    noduri = [n for n in arb.body if (isinstance(n, ast.FunctionDef) and (n.name == "analiza_lot13" or n.name.startswith("_l13_")))
              or (isinstance(n, ast.Assign) and any(getattr(t, "id", "").startswith("_L13") for t in n.targets))]
    assert len([n for n in noduri if isinstance(n, ast.FunctionDef)]) >= 4, "ANTI-VACUU: analiza lotului 13 lipsește din verificator"
    ns = {"re": re}
    exec(compile(ast.Module(body=noduri, type_ignores=[]), "verificator_conformitate.py", "exec"), ns)
    return ns["analiza_lot13"]


@pytest.fixture(scope="module")
def reale():
    fis = {}
    for d in ("static/js/ecrane", "static/js"):
        for f in sorted(os.listdir(os.path.join(_RAD, d))):
            if f.endswith(".js") and ".bak" not in f and f not in fis:
                fis[f] = _citeste(os.path.join(d, f))
    return fis, _citeste("static/stil.css"), _citeste("core/numere.py")


def _coduri(rez, cod, fisier="x.js"):
    return [r for r in rez if r[2] == cod and r[0] == fisier]


def _una(analiza, reale, sursa):
    fis, css, num = reale
    return analiza(dict(fis, **{"x.js": sursa}), css, num)


CAZURI = [
    # (cod, rău, bun)
    ("SUMA_CITITA_BRUT", 'const s = parseFloat(String(inp.value).replace(",", "."));', "const s = numarRo(inp.value).valoare;"),
    ("SUMA_TEXT", '<input type="text" id="x-suma" class="camp-input" aria-label="Suma (lei)">',
     '<input type="number" step="0.01" id="x-suma" class="camp-input" aria-label="Suma (lei)">'),
    ("PRECOMPLETARE", '<input type="text" id="x-cont" class="camp-input" value="446">', '<input type="text" id="x-cont" class="camp-input">'),
    ("PRECOMPLETARE", '<input type="number" id="x-cota" class="camp-input" placeholder="21">',
     '<input type="number" id="x-cota" class="camp-input" placeholder="ex. 21">'),
    ("PRECOMPLETARE", '<input id="x-tara" class="camp-input" value="${esc(d.tara || "RO")}">', '<input id="x-tara" class="camp-input" value="${esc(d.tara || "")}">'),
    ("FEREASTRA_INLINE",
     'const zona = corp.querySelector("#x-zona");\nb.addEventListener("click", () => {\n  zona.innerHTML = `<input id="x-v" class="camp-input">`;\n});',
     'b.addEventListener("click", () => {\n  nav.deschide("X", (c2) => { c2.innerHTML = `<input id="x-v" class="camp-input">`; });\n});'),
    ("ACTIUNE_FARA_BUTON", '<details class="dec-xml"><summary>▸ Compoziția netului</summary><table class="fd-tabel"></table></details>',
     '<details class="dec-xml"><summary>Cum se face</summary><p>Pașii.</p></details>'),
    ("ACTIUNE_FARA_BUTON", '<div class="x-rand" style="cursor:pointer">Deschide</div>', '<button class="buton-secundar">Deschide</button>'),
    ("BUTON_ASCUNS", '${o.poate ? `<button class="buton-secundar" data-x="1">Stornează</button>` : ""}',
     '<button class="buton-secundar" data-x="1"${o.poate ? "" : atributeInactiv("Nota e validată.")}>Stornează</button>'),
    ("LISTA_SCURTA", '<select id="x-fel" class="camp-input">${ALEGE}<option value="a">Avans</option><option value="d">Decont</option></select>',
     '<select id="x-fel" class="camp-input" data-butoane>${ALEGE}<option value="a">Avans</option><option value="d">Decont</option></select>'),
    ("LISTA_SCURTA", 'const FEL = [["a", "Avans"], ["d", "Decont"]];\nconst h = `<select id="x-fel">${FEL.map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}</select>`;',
     'const h = `<select id="x-firma">${firme.map((f) => `<option value="${f.id}">${esc(f.nume)}</option>`).join("")}</select>`;'),
    ("GRILA_INLINE", '<div style="display:grid;grid-template-columns:1fr 1fr">\n<label class="camp"><input class="camp-input"></label></div>',
     '<div class="grila-campuri">\n<label class="camp"><input class="camp-input"></label></div>'),
]


@pytest.mark.parametrize("cod,rau,bun", CAZURI, ids=["%s-%d" % (c[0], i) for i, c in enumerate(CAZURI)])
def test_fragmentul_rau_e_prins_iar_cel_bun_nu(analiza, reale, cod, rau, bun):
    assert _coduri(_una(analiza, reale, rau), cod), (cod, rau)
    assert not _coduri(_una(analiza, reale, bun), cod), (cod, bun, _coduri(_una(analiza, reale, bun), cod))


@pytest.mark.parametrize("fisier,ancora,inlocuire,cod", [
    ("api.js", "export function numarRo(", "export function numarRo_(", "SUMA_CITITA_BRUT"),
    ("api.js", "if (gresit) throw gresit;", "", "SUMA_CITITA_BRUT"),
    ("api.js", "export function alegereButoane(", "export function alegereButoane_(", "LISTA_SCURTA"),
    ("api.js", "export function inactiv(", "export function inactiv_(", "BUTON_ASCUNS"),
    ("navigator.js", '"fer-lucru"', '"fer-alta"', "FEREASTRA_INLINE"),
])
def test_mecanismul_scos_e_prins(analiza, reale, fisier, ancora, inlocuire, cod):
    """MUTAȚIE (în memorie, pe textul real): mecanismul comun scos -> regula nu mai poate fi respectată -> prins."""
    fis, css, num = reale
    assert fis[fisier].count(ancora) >= 1, ancora
    rez = analiza(dict(fis, **{fisier: fis[fisier].replace(ancora, inlocuire)}), css, num)
    assert [r for r in rez if r[2] == cod and r[1] == 0], (fisier, ancora)


def test_stilul_mecanismelor_scos_e_prins(analiza, reale):
    fis, css, num = reale
    for ancora, cod in ((".fereastra.fer-lucru {", "FEREASTRA_INLINE"), (".alegere-butoane {", "LISTA_SCURTA"),
                        ('.buton-secundar[aria-disabled="true"]', "BUTON_ASCUNS")):
        assert ancora in css, ancora
        rez = analiza(fis, css.replace(ancora, ".altceva {"), num)
        assert [r for r in rez if r[2] == cod and r[0] == "stil.css"], ancora
    assert [r for r in analiza(fis, css, num.replace("def numar_ro(", "def numar_ro_(")) if r[2] == "SUMA_CITITA_BRUT" and r[1] == 0]


def test_mecanismele_reale_exista_si_fisierele_zonei_ds_sunt_curate(analiza, reale):
    fis, css, num = reale
    rez = analiza(fis, css, num)
    assert not [r for r in rez if r[1] == 0], [r for r in rez if r[1] == 0]
    assert not [r for r in rez if r[0] in FISIERE_DS], [r for r in rez if r[0] in FISIERE_DS]
    # ANTI-VACUU: regulile văd ce măsoară (locurile din fișierele altor zone, raportate în l13_raport/ds.md)
    assert {r[2] for r in rez} >= {"LISTA_SCURTA", "BUTON_ASCUNS", "PRECOMPLETARE", "FEREASTRA_INLINE"} or not rez
