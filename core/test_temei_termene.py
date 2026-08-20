# -*- coding: utf-8 -*-
"""GARD (R4, 20.08.2026): fiecare termen de depunere își poartă actul.

DECIZIA (Costin): termenele sunt constante fiscale ca oricare altele — temeiul se atașează PER TIP.
Argumentul care închide „25 e notoriu": notorietatea e o proprietate a CUNOAȘTERII, nu a valorii; cota
TVA de 21% e la fel de notorie și e cazul dominant al datoriei de pe 31.07. Iar excepțiile deja citate
dovedesc că baza are temei — dacă D101 la 25 iunie merită un act, „25 ale lunii următoare" merită la fel,
altfel regula e mai slab susținută decât abaterile de la ea.

DE CE E GARDĂ ȘI NU O NOTĂ. Termenele s-au schimbat de două ori în viața aplicației și NICIUNA n-a fost
prinsă de un test: scadența D101 a ieșit dintr-o plimbare vizuală (era 25.03 hardcodat, marca fals
restanțieri firmele care depuneau apr-iun), iar ziua 30 inexistentă în februarie a ieșit în timpul
cablării D394. O intenție scrisă ar deriva la fel.

FEZABILITATE verificată: `anaf_surse/` are Codul fiscal consolidat (art. 101/132/147/323/324/325) plus
ordinele pentru D300, D406 și D205/D207. Sursarea se face verbatim, nu din memorie.
"""
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAD = os.path.join(_RAD, "core", "scadente.py")

# tipurile care primesc un termen prin `_data_nominala`; `None` = regula implicită (ziua 25)
TIPURI = ["d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406"]
# marcaj de temei acceptat pe linia/blocul care fixează termenul tipului
_ACT = re.compile(r"(OUG|OG|Legea|HG|OPANAF|Ordin|CF art|art\.\s*\d)", re.I)


def _sursa():
    return open(_SCAD, encoding="utf-8").read()


def test_gardul_vede_modulul():
    """Anti-vacuu: dacă `scadente.py` se mută sau se golește, testul de mai jos ar trece pe gol."""
    s = _sursa()
    assert "_data_nominala" in s and "_ZIUA" in s, "scadente.py nu mai are forma așteptată"
    assert len(TIPURI) >= 8


def _tipuri_fara_temei():
    """Un tip are temei dacă numele lui apare într-un bloc care citează un act."""
    s = _sursa()
    fara = []
    for t in TIPURI:
        blocuri = [l for l in s.splitlines() if t in l.lower()]
        # plus contextul: comentariile din jurul menționării
        idx = [i for i, l in enumerate(s.splitlines()) if t in l.lower()]
        ctx = []
        linii = s.splitlines()
        for i in idx:
            ctx += linii[max(0, i - 8):i + 3]
        if not any(_ACT.search(l) for l in (blocuri + ctx)):
            fara.append(t)
    return fara


@pytest.mark.xfail(strict=True, reason=(
    "DATORIE 20.08.2026 (R4, decis de Costin): termenele de depunere sunt constante fiscale fără act "
    "citat. Doar D101 îl are, și l-a primit după ce a marcat fals restanțieri. Regula de bază — «25 ale "
    "lunii următoare», 30 pentru D394, ultima zi pentru D406 — trăiește în `_ZIUA.get(tip, 25)` fără "
    "nicio trimitere. Cade când fiecare tip își poartă actul, verbatim din anaf_surse/."))
def test_fiecare_termen_poarta_actul():
    fara = _tipuri_fara_temei()
    assert not fara, (
        "Tipuri cu termen fără act citat: %s. Temeiul se atașează PER TIP (decis 20.08) — "
        "sursele există în anaf_surse/ (Cod fiscal consolidat + OPANAF pentru D300/D406/D205)." % fara)
