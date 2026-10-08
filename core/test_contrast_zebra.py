# -*- coding: utf-8 -*-
"""GARD — linkul de acțiune pe rândul zebră are contrast AA (DS cap.15 v2.81, găsit de axe 08.10.2026: „Contează” din Istoric facturi,
#2f6fa6 pe --albastru-clar = 4,13:1). Calculează din `static/stil.css` culoarea EFECTIVĂ a `.btn-link` într-o `.zebra-lista` (regula
proprie, altfel cea de bază) și o confruntă cu AMBELE fundaluri ale zebrei (WCAG 1.4.3: 4,5:1 pentru text normal).
MUTAȚIE: regula `.zebra-lista .btn-link` scoasă -> rămâne #2f6fa6 -> 4,13 -> pică.
"""
import io
import os
import re

_CSS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "stil.css")


def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _culoare(css, selector):
    m = [x for x in re.finditer(r"(?m)^%s\s*\{([^}]*)\}" % re.escape(selector), css)]
    for x in reversed(m):
        c = re.search(r"(?<![-\w])color:\s*(#[0-9a-fA-F]{6})", x.group(1))
        if c:
            return c.group(1).lower()
    return None


def test_linkul_pe_randul_zebra_are_contrast_aa():
    css = io.open(_CSS, encoding="utf-8").read()
    tok = dict(re.findall(r"--(albastru-clar|alb):\s*(#[0-9a-fA-F]{6})", css))
    efectiv = _culoare(css, ".zebra-lista .btn-link") or _culoare(css, ".btn-link")
    assert efectiv and set(tok) == {"albastru-clar", "alb"}, (efectiv, tok)
    valori = {fund: round(_contrast(efectiv, tok[fund]), 2) for fund in ("albastru-clar", "alb")}
    assert min(valori.values()) >= 4.5, "linkul %s pe zebră: %s (sub 4,5:1)" % (efectiv, valori)



def test_textul_colorat_pe_randul_zebra_al_tabelelor_are_contrast_aa():
    """[08.10.2026, găsit de axe pe Balanță] Tokenii de TEXT folosiți în celule (verde, roșu, gri, amber) pe rândul impar al oricărui
    tabel (`table tbody tr:nth-child(odd) td`, fundal --albastru-clar) trec 4,5:1 — luând în calcul redefinirile de token din chiar
    regula zebrei. MUTAȚIE: `--verde: var(--verde-inchis)` scos din regula zebrei -> verdele rămâne #1d7a4d -> 4,13 -> pică."""
    css = io.open(_CSS, encoding="utf-8").read()
    tok = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", css))
    regula = re.search(r"table tbody tr:nth-child\(odd\) td\s*\{([^}]*)\}", css)
    assert regula, "regula zebrei tabelelor a dispărut"
    redef = dict(re.findall(r"--([a-z-]+):\s*var\(--([a-z-]+)\)", regula.group(1)))
    efectiv = {t: tok[redef.get(t, t)] for t in ("verde", "rosu", "gri", "galben-text")}
    valori = {t: round(_contrast(c, tok["albastru-clar"]), 2) for t, c in efectiv.items()}
    assert min(valori.values()) >= 4.5, "text pe rândul zebră sub 4,5:1: %s" % valori
