# -*- coding: utf-8 -*-
"""GARD import_mesaje_afisate: mesajele ridicate cu `raise ValueError/TypeError` din parserele de
import ajung la utilizator (endpointul de import face HTTPException(422, str(e)) -> ecran). Sunt text
AFISAT -> diacritice. Garda generala test_diacritice_afisate scaneaza doar 3 roluri AST (HTTPException
detail / dict display-key / ClassDef de exceptie), NU `raise ValueError` inline dintr-o functie de
modul -> unghi mort dovedit la mesajul asociatilor (Q17) si CAEN (Q2). Aici acoperim acel rol pe
suprafata de import (unde str(e) surface la user), fara sa fortam diacritice pe erori interne/dev."""
import ast
import glob
import io

FISIERE = sorted(glob.glob("core/*_import_api.py")) + ["core/solduri_api.py", "core/solduri_parteneri_api.py"]


def test_mesaje_import_raise_au_diacritice():
    from core.test_diacritice_afisate import flag  # criteriul UNIC de continut (proza RO + trigger, fara diacritice)
    probleme = []
    for fn in FISIERE:
        try:
            tree = ast.parse(io.open(fn, encoding="utf-8").read())
        except (OSError, SyntaxError):
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call):
                f = n.exc.func
                nm = f.id if isinstance(f, ast.Name) else getattr(f, "attr", "")
                if nm in ("ValueError", "TypeError", "RuntimeError"):
                    for a in n.exc.args:
                        for sub in ast.walk(a):
                            if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and flag(sub.value):
                                probleme.append("%s:%s  %s" % (fn, sub.lineno, sub.value[:60]))
    assert not probleme, "mesaje de import AFISATE fara diacritice (scapa garzii generale prin rol):\n" + "\n".join(probleme)
