# -*- coding: utf-8 -*-
"""GARD (F5/Regula 14.4): mesajele de VALIDARE ale generatoarelor de declaratii (functiile
`erori_generare`/`valideaza`/`erori_*` din core/d*.py) NU expun nume interne de camp catre
contabil. Complementar lui `test_mesaje_fara_camp_intern.py` (care extrage prin rol sintactic
HTTPException/dict-display) — ACELA nu vedea sirurile din LISTELE returnate de erori_generare,
exact unde traia `(nr_doc gol)` al D301.

SEMNAL: token snake_case (litera mica + segment `_alnum`) intr-un sir de mesaj (are spatiu),
IN afara docstring-urilor. Proza romaneasca n-are underscore -> e nume de camp/coloana intern.

RATCHET per-fisier: `_BASELINE` = datoria F5 app-wide de la 19.08 (274 mesaje / 31 fisiere,
descoperita inchizand perimetrul 006/D301). NICIUN fisier nu poate CRESTE (mesaj nou cu nume
intern -> pica); un fisier nou = 0 admis. Burn-down: rescrii mesajele in limba contabilului
(eticheta umana, fara paranteza cu token intern) -> scazi numarul din _BASELINE (constient).
Tinta finala = _BASELINE gol."""
import ast
import glob
import os
import re
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")

# Datorie F5 app-wide (burn-down). D301 = 0 (reparat, perimetru 006). Scade pe masura ce rescrii.
_BASELINE = {
    "core/d104.py": 2, "core/d110.py": 8, "core/d114.py": 12, "core/d119.py": 2, "core/d120.py": 4,
    "core/d130.py": 3, "core/d169.py": 1, "core/d169n.py": 2, "core/d200.py": 9, "core/d201.py": 7,
    "core/d204.py": 12, "core/d208.py": 4, "core/d212.py": 4, "core/d213.py": 13, "core/d214.py": 6,
    "core/d216.py": 9, "core/d220.py": 7, "core/d221.py": 12, "core/d223.py": 9, "core/d230.py": 8,
    "core/d300.py": 2, "core/d318.py": 14, "core/d393.py": 1, "core/d395.py": 1, "core/d397.py": 4,
    "core/d398.py": 19, "core/d399.py": 16, "core/d402.py": 19, "core/d403.py": 36, "core/d407.py": 21,
    "core/d600.py": 7,
}


def _fn_erori(n):
    return n == "valideaza" or n.startswith("erori")


def _flagate_in(path):
    """[(lineno, sir, tokens)] mesaje user-facing cu nume intern, EXCLUZAND docstring-uri."""
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except SyntaxError:
        return []
    excl = {id(n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)}
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and _fn_erori(node.name):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and id(sub) not in excl \
                        and " " in sub.value.strip() and _SNAKE.search(sub.value):
                    out.append((sub.lineno, sub.value, _SNAKE.findall(sub.value)))
    return out


def _fisiere():
    return sorted(set(glob.glob(os.path.join(_RAD, "core", "d*.py"))
                      + glob.glob(os.path.join(_RAD, "core", "*engine*.py"))
                      + [os.path.join(_RAD, "core", "bilant.py")]))


def test_niciun_fisier_nu_creste_peste_baseline():
    peste = []
    for f in _fisiere():
        rel = "core/" + os.path.basename(f)
        n = len(_flagate_in(f))
        baz = _BASELINE.get(rel, 0)
        if n > baz:
            det = _flagate_in(f)
            peste.append("%s: %d mesaje cu nume intern (baseline %d) -> +%d nou. Ex: %s"
                         % (rel, n, baz, n - baz, [d[2] for d in det][:5]))
    assert not peste, ("Mesaje de generare NOI care expun nume intern de camp (F5/Regula 14.4). "
                       "Scrie-le in limba contabilului (eticheta umana, fara token snake_case):\n  "
                       + "\n  ".join(peste))


def test_baseline_nu_e_stale():
    """Daca un fisier a SCAZUT sub baseline, actualizeaza _BASELINE (altfel datoria pare mai mare)."""
    stale = []
    for f in _fisiere():
        rel = "core/" + os.path.basename(f)
        n = len(_flagate_in(f))
        baz = _BASELINE.get(rel, 0)
        if rel in _BASELINE and n < baz:
            stale.append("%s: acum %d < baseline %d -> scade _BASELINE la %d (burn-down)" % (rel, n, baz, n))
    assert not stale, "Baseline F5 stale (ai reparat, actualizeaza):\n  " + "\n  ".join(stale)


def test_criteriu_are_dinti():
    from types import SimpleNamespace as _  # noqa
    # mesaj cu snake_case flagat; docstring/proza NU
    assert _SNAKE.search("fara numar document (nr_doc gol).")
    assert not _SNAKE.search("fara numar document.")
    assert not _SNAKE.search("Operatiunea 3: completeaza numarul documentului.")
