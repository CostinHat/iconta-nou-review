# -*- coding: utf-8 -*-
"""Inventarul familiei `trimite_email_html`, pe AST. Citeste depozitul, nu-l atinge.

DEFINITII, scrise INAINTE de a masura — ca sa nu se compare cifre ale unor clasificatoare diferite:

  LOC DE APEL = o aparitie SINTACTICA a apelului `trimite_email_html(...)` in cod de PRODUCTIE
                (`core/*.py` fara `test_*`, plus `main.py`), numarata pe AST. Un nume intr-un
                comentariu, intr-un docstring sau intr-un fisier de proba NU e un apel.

  CALE        = o pereche (loc de apel, context de tranzactie). Doua apeluri in aceeasi functie
                sunt doua cai daca stau in blocuri diferite; acelasi apel chemat din doua rute
                ramane o singura cale, fiindca reparatia se face o data, acolo.
                *Nu e aceeasi unitate cu «cale» din inventarul P5, care numara PUNCTE DE INTRARE.
                Cele doua nu se compara fara mapping.*

  SUB CONEXIUNE = apelul se executa lexical in interiorul unui `with ...get_conn(...)`. Asta e
                clasa valului 3: leaga o conexiune din pool (10) de latenta unui serviciu strain
                (termen 15 s).

Pentru fiecare cale se raporteaza si: functia care o contine, daca e ruta (decorator `@app.*`),
daca exista `commit()` inainte in acelasi bloc, si daca rezultatul apelului e CITIT.
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys

NUME = "trimite_email_html"


def fisiere(rad):
    out = []
    m = os.path.join(rad, "main.py")
    if os.path.isfile(m):
        out.append(m)
    core = os.path.join(rad, "core")
    if os.path.isdir(core):
        for f in sorted(os.listdir(core)):
            if f.endswith(".py") and not f.startswith("test_"):
                out.append(os.path.join(core, f))
    return out


def _e_ruta(fn):
    for d in fn.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "app":
            cale = ""
            if isinstance(d, ast.Call) and d.args and isinstance(d.args[0], ast.Constant):
                cale = d.args[0].value
            return "%s %s" % (f.attr.upper(), cale)
    return None


def _get_conn(nod):
    """`with`-ul dat deschide o conexiune din pool?"""
    for it in nod.items:
        e = it.context_expr
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Attribute) and f.attr.startswith("get_conn"):
                return True
    return False


def analizeaza(cale, rad):
    text = io.open(cale, encoding="utf-8").read()
    arbore = ast.parse(text)
    rel = os.path.relpath(cale, rad)
    rez = []

    # parintii, ca sa pot urca de la apel la functie si la `with`
    parinte = {}
    for n in ast.walk(arbore):
        for c in ast.iter_child_nodes(n):
            parinte[c] = n

    for n in ast.walk(arbore):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        ident = (f.attr if isinstance(f, ast.Attribute)
                 else f.id if isinstance(f, ast.Name) else None)
        if ident != NUME:
            continue

        # urc pana la functia care il contine si adun `with`-urile de pe drum
        fn, withuri, p = None, [], parinte.get(n)
        while p is not None:
            if isinstance(p, ast.With):
                withuri.append(p)
            if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn is None:
                fn = p
            p = parinte.get(p)

        sub_conexiune = any(_get_conn(w) for w in withuri)
        blocul = next((w for w in withuri if _get_conn(w)), None)

        # exista `commit()` INAINTE de apel, in acelasi bloc de conexiune?
        comis_inainte = False
        if blocul is not None:
            for x in ast.walk(blocul):
                if (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                        and x.func.attr == "commit" and x.lineno < n.lineno):
                    comis_inainte = True

        # rezultatul e citit? (apelul e valoarea unui Assign / conditie / return)
        pn = parinte.get(n)
        rezultat_citit = not isinstance(pn, ast.Expr)

        rez.append({
            "fisier_linie": "%s:%d" % (rel, n.lineno),
            "functie": fn.name if fn else "(modul)",
            "e_ruta": _e_ruta(fn) if fn else None,
            "sub_conexiune": sub_conexiune,
            "bloc_conexiune_linii": ("%d..%d" % (blocul.lineno, blocul.end_lineno)
                                     if blocul is not None else None),
            "commit_inainte": comis_inainte,
            "rezultat_citit": rezultat_citit,
            "async": isinstance(fn, ast.AsyncFunctionDef) if fn else False,
        })
    return rez


def inventar(rad):
    """Toate locurile de apel din codul de productie al arborelui `rad`, ordonate. PURA fata de
    depozit: citeste, nu scrie. Garda `core/test_email_html_dupa_commit.py` o cheama pe asta."""
    toate = []
    for c in fisiere(rad):
        toate.extend(analizeaza(c, rad))
    toate.sort(key=lambda x: (x["fisier_linie"].split(":")[0],
                              int(x["fisier_linie"].split(":")[1])))
    return toate


def main():
    rad = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    toate = inventar(rad)
    sub = [x for x in toate if x["sub_conexiune"]]
    print("EMAIL_HTML_CALLSITES=%d" % len(toate))
    print("EMAIL_HTML_PATHS_SUB_CONEXIUNE=%d" % len(sub))
    print()
    print("%-28s %-34s %-5s %-7s %-7s %s" % ("FILE:LINE", "FUNCTIE", "RUTA", "SUB_CX",
                                             "COMMIT?", "REZULTAT_CITIT"))
    for x in toate:
        print("%-28s %-34s %-5s %-7s %-7s %s"
              % (x["fisier_linie"], x["functie"][:34], "da" if x["e_ruta"] else "-",
                 "DA" if x["sub_conexiune"] else "nu",
                 "da" if x["commit_inainte"] else "-",
                 "da" if x["rezultat_citit"] else "nu"))
    print()
    print(json.dumps(toate, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
