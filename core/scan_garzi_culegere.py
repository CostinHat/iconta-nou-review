# -*- coding: utf-8 -*-
"""Rafinarea sub-instrumentului B.

PRIMA FORMA a dat 753 din 2072 (36%) - o cifra care nu spune nimic. Motivul, gasit uitandu-ma la
rezultate, nu la cod: „nicio asertiune de existenta" prinde si testele unitare pure, unde
`assert f(x) == 0` pe o intrare CONSTRUITA e exact ce trebuie. Acolo nu exista risc de vid: intrarea
e in test, nu culeasa.

Riscul de vid apare cand subiectul e CULES - fisiere plimbate, randuri interogate, un corpus scanat -
fiindca multimea culeasa poate fi goala si atunci orice afirmatie negativa e adevarata degeaba.

Deci B masoara: test care CULEGE + nicio asertiune de existenta + niciun control pozitiv in modul.
"""
import ast

CULEGERE = ("walk", "glob", "rglob", "iglob", "listdir", "execute", "read", "read_text",
            "readlines", "open", "finditer", "findall", "get", "post")
FIXTURI_DATE = ("pe_tenant", "conn", "cur", "client", "db", "tenant", "c")


def _numele_apelate(nod):
    out = set()
    for x in ast.walk(nod):
        if isinstance(x, ast.Call):
            f = x.func
            out.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    return out


def culege(test, ajutoare):
    """True daca testul isi ia subiectul dintr-o multime CULEASA (direct sau printr-un ajutor)."""
    nume = _numele_apelate(test)
    if nume & set(CULEGERE):
        return True
    for a in test.args.args:
        if a.arg in FIXTURI_DATE:
            return True
    for n in nume:
        if n in ajutoare and ajutoare[n] & set(CULEGERE):
            return True
    return False


def ajutoare_modul(arb):
    """nume_functie -> numele apelate in ea (o singura treapta; ajunge pentru `_sursa()`/`_read()`)."""
    out = {}
    for nod in ast.walk(arb):
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[nod.name] = _numele_apelate(nod)
    return out


def control_pozitiv(arb, stabileste):
    """Modulul are un test-frate care AFIRMA EXISTENTA pe acelasi corpus? Ala e anti-vacuumul:
    `test_gardul_vede_modulul` din `test_temei_termene` e chiar forma canonica."""
    for nod in ast.walk(arb):
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and nod.name.startswith("test_") and stabileste(nod):
            return True
    return False
