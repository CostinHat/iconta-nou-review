# -*- coding: utf-8 -*-
"""[Rotunjire fiscală] GARD: în tot `core/` + `main.py` (până la 16.10.2026, 280: numai modulele de declarații `core/d*.py`,
`*engine*.py` — garda veche, scoasă fiindcă noua le cuprinde) o sumă fiscală NU se rotunjește cu `round()` (bancar, half-to-even —
greșit pe .XX5), ci cu `common._q()` (Decimal + ROUND_HALF_UP).
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


def test_rotunjirea_in_toata_aplicatia_e_aritmetica_sau_motivata():
    """[deficiența 280, comanda Costin 16.10.2026, verbatim în DECIZII] „Verifici regula de rotunjire la sursă și toate locurile unde se
    rotunjesc sume fiscale; dacă e rotunjire «la par», o repari în toată clasa.” Garda veche vedea numai modulele de declarații;
    în rest erau 102 `round()` în 28 de module. Clasificate: o sumă NOUĂ (produs / împărțire: TVA în lei la curs, linia casei × factor,
    amortizarea RIP, cantitate × preț) se rotunjește aritmetic (`common._q`) — reparate; sumele de valori care au deja bani și
    indicatorii (procent, oră) poartă `# round-ok: <motiv>`. Acum în TOT `core/` + `main.py`.
    MUTAȚIE: `float(_q(_dec(a["cantitate"]) * _dec(a["pret"])))` -> `round(a["cantitate"] * a["pret"], 2)` în articole_import_api -> pică."""
    rele, fisiere = [], sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))) + [os.path.join(_RAD, "main.py")]
    assert len([f for f in fisiere if os.path.basename(f).startswith("d1")]) >= 5, "premisa: modulele de declarații sunt în listă"
    for f in fisiere:
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
                ln = lines[node.lineno - 1]
                if "int(round(" in ln or "round-ok:" in ln or "_q(" in ln:
                    continue
                rele.append("%s:%d %s" % (os.path.basename(f), node.lineno, ln.strip()[:80]))
    assert not rele, ("`round()` (la par) fără motiv: o sumă nouă se rotunjește cu `common._q()` (ROUND_HALF_UP); o sumă de valori "
                      "cu bani sau un indicator se marchează `# round-ok: <motiv>`: %s" % rele)


def test_280_valoarea_articolului_rotunjeste_aritmetic_nu_la_par():
    """0,125 lei: `round(0.125, 2)` = 0,12 (la par — 0,125 e exact în binar), aritmetic = 0,13 (CLAUDE.md „Rotunjire fiscală”)."""
    from core import articole_import_api as a
    assert round(0.125, 2) == 0.12   # calibrare: capcana există
    assert a.rezumat([{"valid": True, "cantitate": 1, "pret": 0.125}])["valoare_totala"] == 0.13
