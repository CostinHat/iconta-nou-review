# -*- coding: utf-8 -*-
"""[Rotunjire fiscală] GARD: în modulele de declarații (`core/d*.py`, `*engine*.py`) o sumă fiscală NU se
rotunjește cu `round()` (bancar, half-to-even — greșit pe .XX5), ci cu `common._q()` (Decimal + ROUND_HALF_UP).
`round()` e permis DOAR pe RATE/COTE (`int(round(...))` — cotele RO sunt întregi, bancar==aritmetic) sau
explicit marcat `# round-ok: <motiv>` (rație/medie/verificare, nu sumă persistată).

Grounded: CLAUDE.md „Rotunjire fiscală". A scos bug real în d212_engine (CAS/CASS/venit_net/impozit cu round
bancar) — reparat. Detectare AST (apeluri reale, nu comentarii/docstring-uri).
"""
import os
import re
import ast
import glob
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _module():
    return (glob.glob(os.path.join(_RAD, "core", "d[0-9]*.py"))
            + glob.glob(os.path.join(_RAD, "core", "*engine*.py")))


def test_sume_fiscale_rotunjesc_aritmetic():
    rele = []
    for f in _module():
        if os.path.basename(f).startswith("test_"):
            continue
        src = open(f, encoding="utf-8").read()
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "round":
                ln = lines[node.lineno - 1] if node.lineno - 1 < len(lines) else ""
                if "int(round(" in ln or "round-ok:" in ln or "_q(" in ln:
                    continue  # rata->int, sau marcat, sau deja _q
                rele.append("%s:%d %s" % (os.path.basename(f), node.lineno, ln.strip()[:70]))
    assert not rele, ("`round()` bancar pe sumă în modul de declarații (folosește `common._q()` = ROUND_HALF_UP, "
                      "sau marchează `# round-ok:` dacă e rație/rată/verificare): %s" % rele)
