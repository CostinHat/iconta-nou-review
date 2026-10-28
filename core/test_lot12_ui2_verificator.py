# -*- coding: utf-8 -*-
"""[lotul 12, pachetul ui2] Regulile noi ale verificatorului — REZUMAT_CASETA (621) și TABEL_NOTE (617 / 622).

Comanda Costin 12.2, verbatim: pct.11 (621) „Balanța: casetele de sus ocupă jumătate din fereastră, se văd 2–3 rânduri de tabel”; cerința
„Casetele nu mănâncă tabelul (regulă globală, nu doar pe balanță)”. Pct.9 (617) „tabel cu un rând pe notă, detaliul la clic, explicațiile o
singură dată”; pct.12 (622) „același tabel ca la 617” (CLAUDE.md §9: „situații identice, soluții identice”).

Logica REALĂ, scoasă din `verificator_conformitate.py` cu `ast` (tiparul `core/test_lot10_fereastra_tabel.py`): fragmentul rău e prins,
cel bun nu; fișierele reale sunt curate; versiunea de dinainte a Balanței (din git, HEAD-ul ramurii la începutul pachetului, sau
fragmentul ei) e prinsă.

Temei: N/A — reguli de interfață (DS cap.9 v2.102).
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
def reguli():
    arb = ast.parse(_citeste("verificator_conformitate.py"))
    noduri = [n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name in ("analiza_fereastra_tabel", "analiza_lot12")]
    assert len(noduri) == 2, "ANTI-VACUU: funcțiile regulilor lipsesc din verificator"
    ns = {"re": re}
    exec(compile(ast.Module(body=noduri, type_ignores=[]), "verificator_conformitate.py", "exec"), ns)
    return ns


@pytest.fixture(scope="module")
def reale():
    fis = {}
    for d in ("static/js/ecrane", "static/js"):
        for f in sorted(os.listdir(os.path.join(_RAD, d))):
            if f.endswith(".js") and ".bak" not in f and f not in fis:
                fis[f] = _citeste(os.path.join(d, f))
    assert len(fis) >= 40 and {"firme.js", "validat.js", "tabel_note.js", "navigator.js"} <= set(fis), len(fis)
    return _citeste("static/stil.css"), fis


def _coduri(rez, cod):
    return [r for r in rez if r[2] == cod]


# ── REZUMAT_CASETA ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
_REZ_RAU = '''function ecranX(corp) {
  corp.innerHTML = `<div class="rezumat-fix"><h2 class="pf-titlu">X</h2>
      ${casetaCiorne(b)}
      <div class="caseta-atentie" id="x-rulaje"><div class="ca-mesaj">${esc(a.motiv)}</div></div>
      </div><table class="fd-tabel"><tbody></tbody></table>`;
}'''
_REZ_BUN = '''function ecranX(corp) {
  corp.innerHTML = `<div class="rezumat-fix"><h2 class="pf-titlu">X</h2>
      <details class="dec-xml"><summary>Concluzia</summary><div class="caseta-info"><span class="ci-mesaj">explicația</span></div></details>
      </div>${casetaRulaje}<div class="caseta-atentie"><div class="ca-mesaj">sub rezumat</div></div><table class="fd-tabel"><tbody></tbody></table>`;
}'''


def test_rezumat_caseta_fragmentul_rau_e_prins_cel_bun_nu(reguli, reale):
    css, fis = reale
    nav = fis["navigator.js"]
    rau = _coduri(reguli["analiza_fereastra_tabel"](css, nav, {"proba.js": _REZ_RAU}), "REZUMAT_CASETA")
    bun = _coduri(reguli["analiza_fereastra_tabel"](css, nav, {"proba.js": _REZ_BUN}), "REZUMAT_CASETA")
    assert [r[1] for r in rau] == [3, 4], rau          # `${casetaCiorne(…)}` și caseta literală, amândouă în rezumat
    assert bun == [], bun                               # pliată în rezumat, sau sub el: nu se prinde


def test_rezumat_caseta_fisierele_reale_sunt_curate(reguli, reale):
    css, fis = reale
    assert _coduri(reguli["analiza_fereastra_tabel"](css, fis["navigator.js"], fis), "REZUMAT_CASETA") == []


def test_rezumat_caseta_mutatia_balanta_veche_e_prinsa(reguli, reale):
    """MUTAȚIA: caseta rulajelor pusă înapoi în rezumatul Balanței (forma de dinainte de 621; [lotul 14, 687] acum rulajele sunt card-rezumat
    în `#b-carduri`, deci caseta se pune înapoi în `.rezumat-fix`, înaintea cardurilor) -> prinsă."""
    css, fis = reale
    f = fis["firme.js"]
    ancora = '      </div>\n      <div id="b-carduri"></div>\n      ${tabel}\n'
    assert f.count(ancora) == 1, "ANTI-VACUU: ancora Balanței lipsește"
    mutat = f.replace(ancora, '      <div class="caseta-atentie" id="b-rulaje"><div class="ca-mesaj">rulaje lipsă</div></div>\n' + ancora)
    rez = _coduri(reguli["analiza_fereastra_tabel"](css, fis["navigator.js"], dict(fis, **{"firme.js": mutat})), "REZUMAT_CASETA")
    assert [r[0] for r in rez] == ["firme.js"] and "caseta-atentie" in rez[0][3], rez


# ── TABEL_NOTE ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_tabel_note_fisierele_reale_sunt_curate(reguli, reale):
    css, fis = reale
    assert _coduri(reguli["analiza_lot12"](fis, css), "TABEL_NOTE") == []


@pytest.mark.parametrize("fisier, ancora, inlocuire", [
    # rândul-card de dinainte (`.pf-frand data-nota-id`) pus înapoi într-un ecran
    ("firme.js", "const randJn = (n) => {", 'const _vechi = (n) => `<div class="pf-frand" data-nota-id="${n.id}"></div>`;\n    const randJn = (n) => {'),
    # Registrul jurnal fără tabelul comun
    ("firme.js", 'htmlTabelNote({ pre: "jn"', 'htmlTabeleleMele({ pre: "jn"'),
    # „De validat” cu cardul notei de dinainte
    ("validat.js", "function randNotaCoada(", "function randNota(c) {}\nfunction randNotaCoada("),
    ("validat.js", 'htmlTabelNote({ pre: "val-n"', 'htmlAltceva({ pre: "val-n"'),
])
def test_tabel_note_mutatiile_sunt_prinse(reguli, reale, fisier, ancora, inlocuire):
    css, fis = reale
    assert fis[fisier].count(ancora) == 1, "ANTI-VACUU: ancora %r lipsește din %s" % (ancora, fisier)
    rez = _coduri(reguli["analiza_lot12"](dict(fis, **{fisier: fis[fisier].replace(ancora, inlocuire)}), css), "TABEL_NOTE")
    assert [r[0] for r in rez] == [fisier], rez


def test_regulile_sunt_chemate_de_audit():
    """Fără chemarea de la nivelul modulului, TOTAL n-ar număra regulile (`rap["…"] = analiza_…(…)`) — nodurile AST ale atribuirilor,
    nu un șir căutat în sursă (`core/test_garzi_pe_text.py`)."""
    arb = ast.parse(_citeste("verificator_conformitate.py"))
    chemate = {(n.targets[0].slice.value, n.value.func.id) for n in arb.body
               if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript) and isinstance(n.targets[0].slice, ast.Constant)
               and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)}
    assert {("fereastra_tabel", "analiza_fereastra_tabel"), ("lot12", "analiza_lot12")} <= chemate, chemate
