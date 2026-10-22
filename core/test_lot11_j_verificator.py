# -*- coding: utf-8 -*-
"""Lotul 11 — regulile noi ale verificatorului: DUPA_GENERARE (8c) și TITLU_FARA_DIACRITICE (comanda 11.1 pct.23).

8c, decizia Costin 10.3: „8c: reparația centrală, cu DS cap. 6 actualizat.” Clasa (comanda 10.2 pct.8c): „După generare, titlul «Notă
generată» e roșu, conturile notei nu se văd, iar «Generează notă» rămâne activ.” Comanda 11.1 pct.23: „titluri fără diacritice”.

Temei: N/A — reguli de interfață (DS cap.6 v2.98 „După generarea unei note”; DS cap.14 v2.98 „Titlurile se scriu cu diacritice”).

Logica REALĂ, scoasă din `verificator_conformitate.py` cu `ast` (tiparul `core/test_lot10_fereastra_tabel.py`): fiecare cod are fragmentul
rău care trebuie prins și fragmentul bun care nu; apoi fișierele reale.
"""
import ast
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NUME = ("analiza_dupa_generare", "analiza_titluri_diacritice", "_GENERATOARE", "_TITLU_FARA_DIACRITICE")


def _citeste(rel):
    return io.open(os.path.join(_RAD, rel), encoding="utf-8").read()


@pytest.fixture(scope="module")
def reguli():
    src = _citeste("verificator_conformitate.py")
    arb = ast.parse(src)
    noduri = [n for n in arb.body if (isinstance(n, ast.FunctionDef) and n.name in _NUME)
              or (isinstance(n, ast.Assign) and any(getattr(x, "id", None) in _NUME for x in n.targets))]
    assert len(noduri) == 4, "ANTI-VACUU: regulile lotului 11 lipsesc din verificator (%d din 4)" % len(noduri)
    ns = {"re": re}
    exec(compile(ast.Module(body=noduri, type_ignores=[]), "verificator_conformitate.py", "exec"), ns)
    # chemarea lor din audit (altfel TOTAL nu le-ar număra): `rap["…"] = analiza_…(fisiere)` la nivelul modulului
    for cheie, fn in (("dupa_generare", "analiza_dupa_generare"), ("titlu_fara_diacritice", "analiza_titluri_diacritice")):
        assert [n for n in arb.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript)
                and getattr(n.targets[0].slice, "value", None) == cheie and isinstance(n.value, ast.Call)
                and getattr(n.value.func, "id", None) == fn], "verificatorul nu mai cheamă %s" % fn
    return ns


@pytest.fixture(scope="module")
def reale():
    fis = {}
    for d in ("static/js/ecrane", "static/js"):
        for f in sorted(os.listdir(os.path.join(_RAD, d))):
            if f.endswith(".js") and ".bak" not in f and f not in fis:
                fis[f] = _citeste(os.path.join(d, f))
    assert len(fis) >= 40 and {"firme.js", "api.js"} <= set(fis), "ANTI-VACUU: %d fișiere JS" % len(fis)
    return fis


def _coduri(rez, cod):
    return [r for r in rez if r[2] == cod]


_API_BUN = """
export function butonGenerat(buton, motiv) {
  buton.disabled = true;
}
export function dupaGenerare(zona, buton, opt = {}) {
  zona.className = zona.className.replace(/\\bmsg-(eroare|avert|info|ok)\\b/g, "").trim();
  zona.innerHTML = `<div class="caseta-ok">${liniiNotaHtml(opt.linii)}</div>`;
  if (buton) butonGenerat(buton);
}
"""


# ── DUPA_GENERARE ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_helperul_real_face_ce_cere_regula(reguli, reale):
    """Pe api.js de acum: stilul de succes, conturile, curățarea refuzului, butonul inactiv."""
    assert _coduri(reguli["analiza_dupa_generare"]({"api.js": reale["api.js"]}), "DUPA_GENERARE_HELPER") == []


@pytest.mark.parametrize("scos", ["butonGenerat(buton);", "msg-(eroare|avert|info|ok)", "caseta-ok", "buton.disabled = true;"])
def test_helperul_stricat_e_prins(reguli, scos):
    """MUTAȚIE: fiecare parte a helperului scoasă -> DUPA_GENERARE_HELPER."""
    rau = _API_BUN.replace(scos, "")
    assert _coduri(reguli["analiza_dupa_generare"]({"api.js": rau}), "DUPA_GENERARE_HELPER"), scos


def test_butonul_de_generare_trebuie_declarat_si_legat_de_helper(reguli):
    """Fragmentele: butonul „Generează notă” nedeclarat; declarat, dar handlerul fără helper; forma bună. Escape-urile `\\u0103` contează."""
    rau1 = {"api.js": _API_BUN, "x.js": '<button class="buton-primar" id="z-salveaza" data-actiune="POST /a">Genereaz\\u0103 not\\u0103</button>'}
    assert _coduri(reguli["analiza_dupa_generare"](rau1), "GENERARE_NEDECLARATA")
    rau2 = {"api.js": _API_BUN, "x.js": '<button id="z-salveaza" data-genereaza-nota data-actiune="POST /a">Generează notă</button>\n'
            'corp.querySelector("#z-salveaza").addEventListener("click", async () => { arataMesaj(z, "gata", "ok"); });'}
    assert _coduri(reguli["analiza_dupa_generare"](rau2), "GENERARE_FARA_HELPER")
    bun = {"api.js": _API_BUN, "x.js": '<button id="z-salveaza" data-genereaza-nota data-actiune="POST /a">Generează notă</button>\n'
           'const b = corp.querySelector("#z-salveaza");\nb.addEventListener("click", async () => { dupaGenerare(z, b, {}); });'}
    assert reguli["analiza_dupa_generare"](bun) == []


def test_textul_confirmarii_numai_in_helper(reguli):
    """„Notă generată” scris de mână într-un ecran (culoarea și conturile ar depinde de ecran). Comentariile nu contează."""
    rau = {"api.js": _API_BUN, "x.js": 'arataMesaj(z, `Not\\u0103 generat\\u0103: ${n}`, "ok");\n// Notă generată, comentariu'}
    assert [r[1] for r in _coduri(reguli["analiza_dupa_generare"](rau), "TEXT_GENERAT_DE_MANA")] == [1]


def test_fisierele_mele_trec_regula(reguli, reale):
    """firme.js (Z, amortizare, închiderea lunii, inventarul, descărcarea gestiunii, salariile), operațiunile și borderoul — trecute pe
    helper în lotul 11."""
    rez = [r for r in reguli["analiza_dupa_generare"](reale) if r[0] in ("firme.js", "api.js", "navigator.js", "operatiuni_ecran.js", "borderou_ecran.js")]
    assert rez == [], rez


def test_inventarul_claselor_e_complet(reguli, reale):
    """Domeniul nu e gol (ANTI-VACUU): cel puțin butoanele de generare din firme.js sunt găsite de `_GENERATOARE` și declarate."""
    t = reale["firme.js"]
    ids = set(re.findall(r'<button[^>]*\bid="([\w-]+)"[^>]*data-genereaza-nota', t))
    assert {"z-salveaza", "j-amort", "il-amort-restanta", "s-desc", "cvi-salveaza", "im-fin", "z-desc-gv", "sp-contare-scrie"} <= ids, ids


@pytest.mark.parametrize("ancora, inlocuire, cod", [
    ('id="z-salveaza" data-genereaza-nota', 'id="z-salveaza"', "GENERARE_NEDECLARATA"),
    ("      dupaGenerare(zona, zSalveaza, {", "      void(zona, zSalveaza, {", "GENERARE_FARA_HELPER"),
    ('dupaGenerare(corp.querySelector("#j-mesaj"), corp.querySelector("#j-amort"), {', 'dupaGenerare(corp.querySelector("#j-mesaj"), null, {',
     "GENERARE_FARA_HELPER"),
])
def test_mutatiile_pe_firme_js_real_sunt_prinse(reguli, reale, ancora, inlocuire, cod):
    """MUTAȚIE pe firme.js real (în memorie): butonul Z nedeclarat; apelul helperului scos din handlerul Z; butonul amortizării nedat
    helperului (alt `dupaGenerare` din apropiere nu-l acoperă) -> codul așteptat."""
    t = reale["firme.js"]
    assert t.count(ancora) == 1, "ANTI-VACUU: ancora %r" % ancora
    rez = [r for r in reguli["analiza_dupa_generare"](dict(reale, **{"firme.js": t.replace(ancora, inlocuire)})) if r[0] == "firme.js"]
    assert [r[2] for r in rez] == [cod], rez


# ── TITLU_FARA_DIACRITICE ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_titlurile_fara_diacritice_sunt_prinse(reguli):
    """MUTAȚIE: `<th>Factura</th>`, `nav.deschide("Iesiri", …)`, `<h2 class="pf-titlu">Inregistrare</h2>` -> prinse; formele corecte, nu."""
    rau = {"x.js": '<th>Factura</th>\nnav.deschide("Iesiri", f);\n<h2 class="pf-titlu">Inregistrare factura</h2>\n<option value="f">Factura</option>'}
    assert [(r[1], r[2]) for r in reguli["analiza_titluri_diacritice"](rau)] == [(1, "Factura"), (2, "Iesiri"), (3, "Inregistrare"),
                                                                                (4, "Factura")]
    bun = {"x.js": '<th>Factură</th>\nnav.deschide("Ieșiri", f);\n<h2 class="pf-titlu">Factura F1A3 din 12.03</h2>\n// <th>Factura</th>'}
    assert reguli["analiza_titluri_diacritice"](bun) == []


def test_titlurile_reale(reguli, reale):
    """Starea fișierelor de acum, în afara celor două instanțe din ecranele altor subagenți (raportul J §10, patch-uri cerute):
    date_firma.js („<th>Factura</th>”) și emitere_ecran.js („<option>Factura</option>”). Când patch-urile se aplică, lista e goală."""
    rest = reguli["analiza_titluri_diacritice"](reale)   # [lotul 11] date_firma.js:746 și emitere_ecran.js:359 corectate
    assert rest == [], rest
