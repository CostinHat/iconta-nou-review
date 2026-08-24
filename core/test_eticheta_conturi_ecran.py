# -*- coding: utf-8 -*-
"""Eticheta din ECRAN și conturile din BACKEND nu pot diverge tăcut.

  core/test_eticheta_conturi_ecran.py

Întrebarea lui Costin, 24.08.2026: *„nimic nu împiedică o modificare viitoare în unul singur. Se poate
face ca unul să-l citească pe celălalt, sau rămân două surse aliniate manual?"*

**Nu se poate face să-l citească, și motivul e de moment, nu de arhitectură.** Conturile trăiesc
într-un singur loc — `main.py`, în `nota_tva_incasare` — iar ecranul **nu le trimite**: postează doar
`sens`. Deci nu sunt două surse ale ADEVĂRULUI. Ce e duplicat e **eticheta**, textul care descrie
perechea de conturi *înainte* ca omul să apese: `«Încasare de la client (4428=4427)»`. Ea se afișează
în selector, deci nu poate veni dintr-un răspuns care încă n-a fost cerut.

**Rămâne a doua variantă — dar aliniate de un GARD, nu de mână.** Asta face fișierul ăsta: citește
perechile din sursa Python și perechile din eticheta JS, și cade dacă diferă. O modificare în oricare
strat, fără celălalt, devine roșie la prima poartă. **Interdicția 17, închisă pe instanța asta.**

CE NU FACE, declarat: nu spune că perechile sunt cele cerute de NORMĂ. Aia e verificarea 3 din Partea 0
și rămâne o citire umană — confruntată la 24.08.2026: la încasare TVA-ul devine exigibil (4428→4427),
la plata furnizorului deducerea devine exigibilă (4428→4426), art. 282. Gardul păzește **acordul dintre
straturi**, nu adevărul lor față de lege.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PY = re.compile(
    r'debit,\s*credit\s*=\s*\(\s*"(\d{3,4})"\s*,\s*"(\d{3,4})"\s*\)\s*'
    r'if\s+sens\s*==\s*"incasare"\s*else\s*\(\s*"(\d{3,4})"\s*,\s*"(\d{3,4})"\s*\)')

JS_INC = re.compile(r'\[\s*"incasare"\s*,\s*"[^"]*?\((\d{3,4})=(\d{3,4})\)[^"]*"\s*\]')
JS_PLT = re.compile(r'\[\s*"plata"\s*,\s*"[^"]*?\((\d{3,4})=(\d{3,4})\)[^"]*"\s*\]')


def _sursa(rel, minim=2000):
    cale = os.path.join(RAD, rel)
    assert os.path.exists(cale), "fisier inexistent: %s — gardul masoara altceva" % rel
    t = io.open(cale, encoding="utf-8").read()
    assert len(t) > minim, "fisier suspect de scurt (%d): %s" % (len(t), rel)
    return t


def _perechi_py():
    m = PY.search(_sursa("main.py", minim=100000))
    assert m, ("nu mai gasesc maparea sens->conturi in main.py (nota_tva_incasare) — "
               "ori s-a mutat, ori s-a rescris; gardul nu poate confrunta ce nu vede")
    return (m.group(1), m.group(2)), (m.group(3), m.group(4))


def _perechi_js():
    js = _sursa("static/js/ecrane/operatiuni_ecran.js")
    mi, mp = JS_INC.search(js), JS_PLT.search(js)
    assert mi, "eticheta de INCASARE din operatiuni_ecran.js nu mai poarta perechea de conturi"
    assert mp, "eticheta de PLATA din operatiuni_ecran.js nu mai poarta perechea de conturi"
    return (mi.group(1), mi.group(2)), (mp.group(1), mp.group(2))


def test_incasarea_spune_acelasi_lucru_in_ambele_straturi():
    py, js = _perechi_py()[0], _perechi_js()[0]
    assert py == js, (
        "DIVERGENTA pe INCASARE: backend %s, eticheta din ecran %s — un adevar in doua locuri, "
        "rupt (interdictia 17)" % (py, js))


def test_plata_spune_acelasi_lucru_in_ambele_straturi():
    assert _perechi_py()[1] == _perechi_js()[1], (
        "DIVERGENTA pe PLATA: backend %s, eticheta din ecran %s (interdictia 17)"
        % (_perechi_py()[1], _perechi_js()[1]))


def test_cele_doua_perechi_sunt_distincte():
    """Calibrare: daca incasarea si plata ar coincide, testele de mai sus ar trece pe o mapare
    degenerata — ar confrunta acelasi lucru cu el insusi."""
    inc, plt = _perechi_py()
    assert inc != plt, "incasare si plata au ajuns aceeasi pereche — mapare degenerata"


def test_conturile_exista_ca_forma_de_cont_sintetic():
    """Anti-vacuu pe continut: perechile trebuie sa fie conturi din clasa 4 (terti/TVA), nu orice
    numar. Nu verifica NORMA — verifica sa nu fi ajuns acolo un numar strain."""
    for pereche in _perechi_py():
        for cont in pereche:
            assert cont.startswith("44"), "cont neasteptat in maparea TVA la incasare: %s" % cont
