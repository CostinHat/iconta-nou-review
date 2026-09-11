# -*- coding: utf-8 -*-
"""Familia `_trimite_brevo`, masurata MECANIC pe arborele pe care ruleaza. (val 3)

Cifra veche «29 -> 25» nu se reutilizeaza: era a altui arbore, dinaintea R68. Aici se remasoara,
si se spune EXACT ce inseamna fiecare numar, ca sa nu se compare rezultate ale unor clasificatoare
diferite.

DEFINITII, scrise inainte de a masura:

  CALE (path)  = un PUNCT DE INTRARE (ruta / middleware / job) din care lantul de apeluri ajunge
                 la `_trimite_brevo`. Acelasi inteles ca in inventarul P5: se numara intrari, nu
                 apeluri. Doua rute care cheama aceeasi functie sunt doua cai.

  C5           = dintre acelea, cele in care primitiva de retea se executa CAT TIMP e tinuta o
                 conexiune din pool. Asta e clasa valului 3 — restul sunt cai care ating Brevo, dar
                 fara sa lege resursa rara de latenta altcuiva.

  LOC DE APEL  = o aparitie sintactica a apelului in cod (`_trimite_brevo(...)`), numarata pe AST,
                 nu pe text: un nume intr-un comentariu sau intr-un docstring nu e un apel.

Se ruleaza din radacina arborelui masurat.
"""
from __future__ import annotations

import ast
import json
import os
import sys

TINTE = ("_trimite_brevo", "alerteaza_in_fundal")


def cai(inv, nume="_trimite_brevo"):
    """Candidatii al caror lant de apeluri trece prin `nume`."""
    out = []
    for x in inv:
        for p in x.get("primitive", []):
            if nume in (p.get("via") or "") or nume in (p.get("loc") or ""):
                out.append(x)
                break
    return out


def locuri_de_apel(radacina, nume):
    """Aparitiile lui `nume` ca APEL, pe AST. Intoarce [(fisier, linie)]."""
    gasite = []
    for d in ("core", "."):
        baza = os.path.join(radacina, d) if d != "." else radacina
        for dirpath, dirnames, filenames in os.walk(baza):
            dirnames[:] = [x for x in dirnames
                           if x not in ("__pycache__", "venv", ".git", "_arhiva_patchuri",
                                        "date_test", "frontend_test", "masuratori")]
            for f in filenames:
                if not f.endswith(".py") or f.startswith("test_"):
                    continue
                cale = os.path.join(dirpath, f)
                try:
                    arbore = ast.parse(open(cale, encoding="utf-8").read())
                except (SyntaxError, UnicodeDecodeError, OSError):
                    continue
                for n in ast.walk(arbore):
                    if not isinstance(n, ast.Call):
                        continue
                    f_ = n.func
                    ident = (f_.attr if isinstance(f_, ast.Attribute)
                             else f_.id if isinstance(f_, ast.Name) else None)
                    if ident == nume:
                        gasite.append((os.path.relpath(cale, radacina), n.lineno))
        if d == ".":
            break
    return sorted(set(gasite))


def main():
    rad = os.path.abspath(".")
    sys.path.insert(0, rad)
    sys.path.insert(0, os.path.join(rad, "scripts"))
    import scan_blocante as sb

    inv, stat = sb.inventar()
    rez = {"radacina": rad, "intrari": stat["intrari"], "candidati": stat["candidati"]}

    for nume in TINTE:
        c = cai(inv, nume)
        c5 = [x for x in c if "C5" in x["detectori"]]
        c2 = [x for x in c if "C2" in x["detectori"]]
        rez[nume] = {
            "cai": len(c),
            "cai_C5": len(c5),
            "cai_C2": len(c2),
            "intrari": sorted(x["intrare"] for x in c),
            "intrari_C5": sorted(x["intrare"] for x in c5),
            "locuri_de_apel": [("%s:%d" % t) for t in locuri_de_apel(rad, nume)],
        }

    print(json.dumps(rez, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
