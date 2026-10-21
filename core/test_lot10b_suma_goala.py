# -*- coding: utf-8 -*-
"""[lotul 10, comanda Costin 10.2 pct.7h] „Notă nouă în Registru jurnal: câmpul Sumă vine precompletat cu «0,00»; câmpurile de sumă sunt
goale.” — CLASA: un câmp de sumă care se deschide cu 0 / 0,00 scris de ecran (nu de om și nu din date), oriunde în aplicație.

Formele găsite (cum ajunge un 0 într-un câmp de sumă):
  a. valoarea șablonului cade pe 0 când datele lipsesc: `value="${x || 0}"`, `value="${Number(x || 0).toFixed(2)}"`, `?? 0`, `: 0`,
     sau literal `value="0"` / `"0.00"`;
  b. butonul care deschide formularul îi dă valoarea prin `data-val="${x || 0}"` (statul de plată: „+ vacanță”, „Salariu”);
  c. linia implicită a formularului nou are `suma: 0` (Registrul jurnal) — păzită pe comportament în
     `core/test_lot10b_jurnal_nota_noua.py::test_7h_*` (montat în Chromium), nu aici.
Un câmp de sumă = `<input type="number">` cu pas de bani (`step="0.01"`) sau numit ca sumă (sumă, valoare, total, TVA, salariu, preț, lei).
Numărătorile (persoane în întreținere, zile, copii) nu sunt sume: 0 e acolo o valoare, nu un gol.

Temei: N/A — UI (comanda 10.2 pct.7h).
MUTAȚIE: `data-val="${s.salariu_baza || ""}"` -> `|| 0` -> pică (forma b); `value="${Number(b.total || 0).toFixed(2)}"` -> pică (forma a).
"""
import glob
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SUMA = re.compile(r'step="0\.01"|(?i:aria-label="[^"]*(sum[aă]|valoare|total|tva|salariu|pre[tț]|lei)|id="[^"]*(sum|val|tot|tva|salariu|pret)[^"]*")')
_ZERO = re.compile(r'^(0|0[.,]0+)$|\|\|\s*0\b|\?\?\s*0\b|:\s*0\s*\)?\s*\}?$')


def _capat(txt, i, stop):
    """Sfârșitul unei bucăți de șablon (`>` al etichetei sau `"` al atributului) din afara unei interpolări `${…}`."""
    d, j = 0, i
    while j < len(txt):
        if txt.startswith("${", j):
            d += 1
            j += 2
            continue
        if txt[j] == "}" and d:
            d -= 1
        elif txt[j] == stop and d == 0:
            return j
        j += 1
    return j


def sume_cu_zero(fisiere):
    """[(fișier:linie, ce)] — câmpurile de sumă care se deschid cu 0 pus de ecran (formele a și b)."""
    out = []
    for nume, txt in fisiere:
        for m in re.finditer(r"<input\b", txt):
            tag = txt[m.start():_capat(txt, m.end(), ">") + 1]
            if 'type="number"' not in tag or not _SUMA.search(tag):
                continue
            v = re.search(r'\bvalue="', tag)
            if v:
                expr = tag[v.end():_capat(tag, v.end(), '"')]
                if _ZERO.search(expr):
                    out.append(("%s:%d" % (nume, txt[:m.start()].count("\n") + 1), expr))
        for m in re.finditer(r'data-val="(\$\{[^"]*?(\|\||\?\?)\s*0\b[^"]*)"', txt):
            out.append(("%s:%d" % (nume, txt[:m.start()].count("\n") + 1), "data-val " + m.group(1)))
    return out


def _fisiere():
    out = []
    for f in sorted(glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True)):
        if ".bak" not in f and os.sep + "vendor" + os.sep not in f:
            out.append((os.path.relpath(f, _RAD), io.open(f, encoding="utf-8").read()))
    return out


def test_niciun_camp_de_suma_nu_se_deschide_cu_zero():
    fis = _fisiere()
    nr_sume = sum(len([1 for m in re.finditer(r"<input\b[^>]*type=\"number\"", t)]) for _n, t in fis)
    assert nr_sume >= 50, "ANTI-VACUU: numai %d câmpuri numerice citite în static/js" % nr_sume
    # 10.2 pct.7h: „câmpul Sumă vine precompletat cu «0,00»; câmpurile de sumă sunt goale.”
    assert sume_cu_zero(fis) == [], sume_cu_zero(fis)


@pytest.mark.parametrize("fragment, prins", [
    ('<input type="number" step="0.01" id="d-tot" value="${Number(b.total || 0).toFixed(2)}">', True),
    ('<input type="number" step="0.01" class="je-sum" aria-label="Sumă" value="0.00">', True),
    ('<input type="number" step="0.01" id="x-suma" value="${x.suma ?? 0}">', True),
    ('<input type="number" step="0.01" id="x-suma" value="${x.suma == null ? 0 : x.suma}">', False),   # ramura „0” nu e la capăt
    ('<input type="number" step="0.01" id="x-suma" value="${x.suma != null ? x.suma : 0}">', True),
    ('<button data-salariu="${s.id}" data-val="${s.salariu_baza || 0}">Salariu</button>', True),
    ('<input type="number" step="0.01" class="je-sum" value="${l.suma == null ? "" : Number(l.suma).toFixed(2)}">', False),
    ('<input type="number" step="0.01" id="d-tot" value="${b.total == null ? "" : Number(b.total).toFixed(2)}">', False),
    ('<input type="number" min="0" step="1" id="dv-persoane" value="${esc(String(s0.persoane_intretinere || 0))}">', False),   # număr
    ('<button data-salariu="${s.id}" data-val="${s.salariu_baza || ""}">Salariu</button>', False),
])
def test_scanerul_pe_fragmente(fragment, prins):
    # „câmpurile de sumă sunt goale” — fiecare formă a clasei e prinsă, iar forma reparată și numărătoarea nu
    assert bool(sume_cu_zero([("proba.js", fragment)])) is prins, sume_cu_zero([("proba.js", fragment)])
