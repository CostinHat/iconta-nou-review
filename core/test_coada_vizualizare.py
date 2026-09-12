# -*- coding: utf-8 -*-
"""GARD (audit patru-ochi): coada de validare are TRASEU de VIZUALIZARE a conținutului. Fără el,
validarea în doi e oarbă — cine aprobă nu vede declarația/XML/verdictul DUK (defect prins pe
tenant_003/006). Gard static: (a) backend expune GET /coada/{id}/continut care citește payload-ul
stocat; (b) frontend-ul (validat.js) rendează o afordanță de vizualizare pe fiecare element din
coadă și cheamă endpoint-ul. Reversul oricăreia -> pică."""
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _citeste(rel):
    return open(os.path.join(_RAD, rel), encoding="utf-8").read()


def test_backend_expune_continut_coada():
    main = _citeste("main.py")
    assert '@app.get("/coada/{coada_id}/continut")' in main, \
        "endpoint-ul GET /coada/{id}/continut lipsește — coada nu poate fi vizualizată"
    # citește payload-ul stocat (xml) al elementului din coadă
    # [P7 · V1, 13.09.2026] Citirea a plecat în repository. Apelul se cere pe STRUCTURĂ (AST),
    # nu pe text: un apel scris într-un comentariu n-ar trebui să treacă.
    import ast as _ast
    arb = _ast.parse(main)
    ruta = [n for n in _ast.walk(arb)
            if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))
            and n.name == "coada_continut"]
    assert ruta, "ruta `coada_continut` nu mai există — garda ar măsura ce nu vede"
    apelate = {getattr(c.func, "attr", None) for c in _ast.walk(ruta[0])
               if isinstance(c, _ast.Call)}
    assert apelate >= {"continutul_din_coada"}, \
        "endpoint-ul nu mai cheamă citirea conținutului din coadă"


def test_frontend_are_traseu_vizualizare():
    v = _citeste("static/js/ecrane/validat.js")
    assert "deschideContinut" in v, "validat.js nu are funcția de deschidere a conținutului"
    assert re.search(r"val-vezi", v), "elementul din coadă nu are afordanță de vizualizare (val-vezi)"
    assert re.search(r"/coada/\$\{[^}]+\}/continut", v), \
        "validat.js nu cheamă endpoint-ul /coada/{id}/continut"
    # decodare UTF-8-safe (nu atob brut, care mângâie diacriticele)
    assert "decodeURIComponent(escape(atob" in v, \
        "XML-ul se decodează UTF-8-safe (atob brut mângâie diacriticele)"


def test_citirea_din_coada_ia_payloadul():
    """Perechea probei de mai sus, cu sursa EI: ce cheamă ruta chiar citește payload-ul din coadă.

    Ruptă în două deliberat — o probă care citește două fișiere nu-și mai poate rezolva ancorele
    (v. `core/test_ancore_in_cod.py`), deci n-ar mai fi păzită de gardul peste gărzi.
    """
    f = _citeste("core/repo_declaratii.py").split("def continutul_din_coada")[1][:600]
    assert "declaratii_coada" in f and "payload" in f, \
        "citirea din repository nu mai ia payload-ul (xml) din declaratii_coada"
