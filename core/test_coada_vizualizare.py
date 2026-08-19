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
    seg = main.split('/coada/{coada_id}/continut')[1][:800]
    assert "declaratii_coada" in seg and "payload" in seg, \
        "endpoint-ul nu citește payload-ul (xml) din declaratii_coada"


def test_frontend_are_traseu_vizualizare():
    v = _citeste("static/js/ecrane/validat.js")
    assert "deschideContinut" in v, "validat.js nu are funcția de deschidere a conținutului"
    assert re.search(r"val-vezi", v), "elementul din coadă nu are afordanță de vizualizare (val-vezi)"
    assert re.search(r"/coada/\$\{[^}]+\}/continut", v), \
        "validat.js nu cheamă endpoint-ul /coada/{id}/continut"
    # decodare UTF-8-safe (nu atob brut, care mângâie diacriticele)
    assert "decodeURIComponent(escape(atob" in v, \
        "XML-ul se decodează UTF-8-safe (atob brut mângâie diacriticele)"
