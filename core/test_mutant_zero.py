# -*- coding: utf-8 -*-
"""core/test_mutant_zero.py — GARD C5 (rest): mutant-zero pe generatoare.

Clasa cat.9 "onestitatea testelor": un generator care INGHITE datele (returneaza [] / output gol cand datele EXISTA)
trece TACIT daca niciun test nu-i aserta continutul. Aici: pe date REALE (fixtura smoke), fiecare generator vizat
produce output NON-gol; MUTATIE (pull fortat sa nu vada datele) -> markerul de continut DISPARE, dovada ca guardul de
continut ar prinde inghitirea. d205 are guard EXPLICIT (ridica pe zero beneficiari).

LIMITA declarata: gol vs non-gol - un output gol e LEGITIM pentru o firma fara date (D112 fara salariati e valid);
mutant-zero NU marcheaza golul in sine ca bug, ci INGHITIREA (gol cand datele exista). Aici sunt gardate d112
(marker <asigurat) si d205 (raise); extinderea la d100/d101/d300/d394/d406 cu acelasi tipar (marker de continut pe
date reale + mutatie pull) ramane - un generator nou trebuie sa-si adauge markerul aici (altfel inghitirea lui trece).
"""
import re
import pytest
from core.common import Perioada
from core import d112, d205
from core.test_smoke_duk import conn_smoke, _SCHEMA, _DBOK   # reutilizeaza fixtura cu date reale


def _pull_gol(orig):
    def w(*a, **k):
        r = list(orig(*a, **k))
        for i, e in enumerate(r):
            if isinstance(e, list):
                r[i] = []
        return tuple(r)
    return w


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_mutant_zero_d112_nu_inghite_salariatii(conn_smoke):
    """Pe date reale D112 contine <asigurat (nu inghite salariatii). MUTATIE: pull fortat sa intoarca 0 salariati ->
    <asigurat DISPARE -> un test care asertă <asigurat ar prinde inghitirea."""
    xml, _ = d112.genereaza(conn_smoke, _SCHEMA, 2026, 6)
    assert "<asigurat " in xml, "D112 pe date reale trebuie sa aiba salariati - altfel a inghitit datele"
    # MUTATIE: generatorul nu mai vede salariatii (pull -> lista goala)
    orig = d112.pull
    d112.pull = _pull_gol(orig)
    try:
        xml_gol, _ = d112.genereaza(conn_smoke, _SCHEMA, 2026, 6)
    finally:
        d112.pull = orig
    assert "<asigurat " not in xml_gol, "mutant-zero: cu salariatii inghititi, <asigurat trebuie sa DISPARA (dovada)"


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_mutant_zero_d205_ridica_pe_zero_beneficiari(conn_smoke):
    """d205 are guard EXPLICIT: fara niciun beneficiar de venit ridica (nu emite declaratie goala tacut). MUTATIE:
    pull fortat sa intoarca 0 beneficiari -> ValueError."""
    orig = d205.pull
    d205.pull = _pull_gol(orig)
    try:
        with pytest.raises(ValueError, match="beneficiar"):
            d205.genereaza(conn_smoke, _SCHEMA, Perioada(2026))
    finally:
        d205.pull = orig
