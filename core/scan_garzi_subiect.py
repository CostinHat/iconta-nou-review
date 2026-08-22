# -*- coding: utf-8 -*-
"""Rafinarea sub-instrumentului A: se separa tiparele dupa CE CAUTA, nu dupa cum arata.

Un tipar cu zero potriviri pe corpus e MORT doar daca subiectul lui e SURSA din repo. Daca subiectul
e un artefact produs la rulare (XML generat, raspuns HTTP, PDF randat), corpusul nu spune nimic
despre el - si atunci instrumentul TACE, nu acuza.

PRIMA FORMA A TRACERULUI A ORBIT SCANUL: cauta citirea de fisier in expresia-argument, pe loc. Dar
subiectul ajunge acolo prin variabile: `_ACT.search(l)` <- `l` din `s.splitlines()` <- `s = _sursa()`
<- `open(_SCAD).read()`. Trei salturi. Cazul de calibrare (octetul 0x08) a DISPARUT din rezultate -
adica rafinarea scadea cifra prin orbire, nu prin precizie. Acum rezolvarea e TRANZITIVA, cu limita
de adancime, si calibrarea se reface dupa fiecare atingere a tracerului.
"""
import ast

CITIRI = ("read", "read_text", "readlines", "open")
ADANCIME = 6


def _leaga(arb):
    """nume -> lista de expresii care il pot produce (atribuiri, tinte de comprehensiune, return)."""
    leg = {}

    def pune(nume, expr):
        leg.setdefault(nume, []).append(expr)

    for nod in ast.walk(arb):
        if isinstance(nod, ast.Assign):
            for t in nod.targets:
                if isinstance(t, ast.Name):
                    pune(t.id, nod.value)
        elif isinstance(nod, (ast.For, ast.AsyncFor)):
            if isinstance(nod.target, ast.Name):
                pune(nod.target.id, nod.iter)
        elif isinstance(nod, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            for g in nod.generators:
                if isinstance(g.target, ast.Name):
                    pune(g.target.id, g.iter)
        elif isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # numele functiei -> ce intoarce (ca sa se poata urmari `s = _sursa()`)
            for x in ast.walk(nod):
                if isinstance(x, ast.Return) and x.value is not None:
                    pune(nod.name + "()", x.value)
    return leg


def _citeste_fisier(expr, leg, adanc=ADANCIME, vazute=None):
    """True daca expresia poate proveni dintr-o CITIRE DE FISIER, urmarind variabilele."""
    if adanc <= 0 or expr is None:
        return False
    vazute = vazute or set()
    for x in ast.walk(expr):
        if isinstance(x, ast.Call):
            f = x.func
            n = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if n in CITIRI:
                return True
            # apel de functie locala: se urmareste ce intoarce
            cheie = (n or "") + "()"
            if cheie in leg and cheie not in vazute:
                vazute.add(cheie)
                if any(_citeste_fisier(e, leg, adanc - 1, vazute) for e in leg[cheie]):
                    return True
        if isinstance(x, ast.Name) and x.id in leg and x.id not in vazute:
            vazute.add(x.id)
            if any(_citeste_fisier(e, leg, adanc - 1, vazute) for e in leg[x.id]):
                return True
    return False


def subiecte(arb):
    """{('inline', lineno): 'SURSA'|'RULARE'} — ce cauta fiecare tipar."""
    leg = _leaga(arb)
    out = {}
    compilate = {}
    for nod in ast.walk(arb):
        if isinstance(nod, ast.Assign) and isinstance(nod.value, ast.Call):
            f = nod.value.func
            if isinstance(f, ast.Attribute) and f.attr == "compile" \
                    and getattr(getattr(f, "value", None), "id", "") == "re":
                for t in nod.targets:
                    if isinstance(t, ast.Name):
                        compilate[t.id] = nod.value.lineno

    def noteaza(ln, fel):
        if out.get(("inline", ln)) != "SURSA":       # o folosire pe SURSA e de ajuns
            out[("inline", ln)] = fel

    METODE = ("search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split")
    for nod in ast.walk(arb):
        if not isinstance(nod, ast.Call):
            continue
        f = nod.func
        n = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if n not in METODE or not isinstance(f, ast.Attribute):
            continue
        tinta = getattr(f.value, "id", None)
        if tinta == "re":                                   # re.search(TIPAR, x)
            if len(nod.args) >= 2 and isinstance(nod.args[0], ast.Constant):
                noteaza(nod.args[0].lineno,
                        "SURSA" if _citeste_fisier(nod.args[1], leg) else "RULARE")
        elif tinta in compilate:                            # NUME.search(x)
            arg = nod.args[0] if nod.args else None
            noteaza(compilate[tinta], "SURSA" if _citeste_fisier(arg, leg) else "RULARE")
    return out
