# -*- coding: utf-8 -*-
"""core/scan_respingeri.py — ce coduri de respingere sunt CHIAR FOLOSITE in module?

Perechea lui `migrare_api.REGULI`, care le DECLARA. Confruntarea celor doua (ca scan<->verificator la
constante) prinde despartirea: un cod folosit si nedeclarat inseamna ca nomenclatorul nu inchide ce
crede ca inchide; un cod declarat si nefolosit e o intrare moarta.

CE NU POATE SPUNE. Vede doar codurile scrise LITERAL la apelul lui `respinge(...)`. Un cod calculat
(dintr-o variabila, dintr-un dictionar) nu se vede - si e raportat separat, nu ignorat.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fisiere():
    d = os.path.join(RAD, "core")
    for f in sorted(os.listdir(d)):
        if f.endswith(".py") and not f.startswith(("test_", "scan_")):
            yield os.path.join(d, f), "core/" + f
    yield os.path.join(RAD, "main.py"), "main.py"


def apeluri():
    """[(fisier, linie, cod_sau_None)] — None = codul nu e literal, deci nu se poate verifica."""
    out = []
    for p, rel in _fisiere():
        try:
            arb = ast.parse(io.open(p, encoding="utf-8").read())
        except (SyntaxError, FileNotFoundError):
            continue
        for n in ast.walk(arb):
            if not isinstance(n, ast.Call):
                continue
            nume = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
            if nume != "respinge":
                continue
            # semnatura: respinge(tip, rand, regula, mesaj, **campuri)
            cod = None
            if len(n.args) >= 3 and isinstance(n.args[2], ast.Constant) \
               and isinstance(n.args[2].value, str):
                cod = n.args[2].value
            for kw in n.keywords:
                if kw.arg == "regula" and isinstance(kw.value, ast.Constant):
                    cod = kw.value.value
            out.append((rel, n.lineno, cod))
    return out


def coduri_folosite():
    return sorted({c for _f, _l, c in apeluri() if c})


def nerezolvate():
    """Apelurile al caror cod nu e literal. Se NUMARA — un cod calculat ocoleste confruntarea."""
    return [(f, l) for f, l, c in apeluri() if not c]


if __name__ == "__main__":
    from core import migrare_api
    folosite, declarate = set(coduri_folosite()), set(migrare_api.REGULI)
    print("apeluri `respinge`: %d | coduri literale distincte: %d | nerezolvate: %d"
          % (len(apeluri()), len(folosite), len(nerezolvate())))
    print("folosite si NEdeclarate : %s" % (sorted(folosite - declarate) or "(niciuna)"))
    print("declarate si NEfolosite : %s" % (sorted(declarate - folosite) or "(niciuna)"))
