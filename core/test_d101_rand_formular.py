# -*- coding: utf-8 -*-
"""GARD — rândul D101 numit pe ecran („rândul 8.1”) e rândul din FORMULARUL OPANAF 206/2025, nu numele atributului XML („P081”).

Comanda Costin 09.10.2026, „Retest 2” pct.2. Gardul ia fiecare atribut pe care îl scrie generatorul (`core/d101.py`), îl trece prin
`rand_d101`, și cere ca rândul obținut să existe în formular (`anaf_surse/opanaf_206_2025_d101.txt`) cu textul atributului din
structură (`anaf_surse/d101_struct_anaf.txt`): primele două cuvinte, pe rădăcină.
"""
import io
import os
import re
import unicodedata

from core.d101_randuri import rand_d101

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: atribute la care confruntarea textului nu se poate face, fiecare cu motivul:
NECONFRUNTABILE = {
    "P084": "textul din structură e stricat la extragere („Elemente  fferen veniturilor”); formularul: rd.8.4 „Elemente similare veniturilor potrivit art. 25”",
    "P122": "textul din structură e stricat la extragere („Sume din anul  fferen”); formularul: rd.12.2 „Sume deductibile în anul curent”",
    "P14": "structura îl numește „Provizioane fiscale”, formularul „Provizioane şi ajustări pentru depreciere” (rd.14, același rând)",
    "P141": "subrândul 14.1 („Filtre prudenţiale”) nu e tipărit ca rând separat în formularul extras",
    "P38a": "poziție intermediară a structurii (fără rând tipărit în formular)",
    "P39a": "poziție intermediară a structurii (fără rând tipărit în formular)",
    "P40a": "poziție intermediară a structurii (fără rând tipărit în formular)",
    "P43a": "poziție intermediară a structurii (fără rând tipărit în formular)",
}


def _norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _radacini(text, n=2):
    return [w[:5] for w in _norm(text).split()[:n]]


def _formular():
    linii = io.open(os.path.join(_RAD, "anaf_surse", "opanaf_206_2025_d101.txt"), encoding="utf-8").read().splitlines()
    a = next(i for i, ln in enumerate(linii) if re.match(r"^\s*1\s+Venituri din exploatare", ln))
    out = {}
    for ln in linii[a:a + 220]:
        m = re.match(r"^\s{0,2}(\d{1,2}(?:\.\d){0,2}[a-z]?)\s+(\S.*)$", ln)
        if m and m.group(1) not in out:
            out[m.group(1)] = m.group(2)
    return out


def _structura():
    st = io.open(os.path.join(_RAD, "anaf_surse", "d101_struct_anaf.txt"), encoding="utf-8").read().splitlines()
    den = {}
    for i, ln in enumerate(st):
        m = re.match(r"^\s*\d+[a-z]?\.?\s+(P\d+[a-z]?)\s+(.*)$", ln)
        if m and m.group(1) not in den:
            den[m.group(1)] = m.group(2)
    return den


def test_fiecare_atribut_scris_cade_pe_randul_lui():
    atribute = sorted(set(re.findall(r'"(P\d+[a-z]?)"', io.open(os.path.join(_RAD, "core", "d101.py"), encoding="utf-8").read())))
    assert len(atribute) > 60, "anti-vacuu: %d atribute citite din generator" % len(atribute)
    f, den = _formular(), _structura()
    gresite = []
    for p in atribute:
        if p in NECONFRUNTABILE:
            continue
        rand = rand_d101(p).replace("rândul ", "")
        if rand not in f or (den.get(p) and _radacini(den[p]) != _radacini(f[rand])):
            gresite.append("%s -> rd.%s: formularul %r, structura %r" % (p, rand, f.get(rand, "")[:50], den.get(p, "")[:50]))
    assert not gresite, "atribute D101 numite greșit pe ecran:\n  " + "\n  ".join(gresite)


def test_textul_randului():
    assert rand_d101("P1") == "rândul 1"
    assert rand_d101("P081") == "rândul 8.1"            # OPANAF 206/2025: rd.8.1 Elemente similare veniturilor potrivit art. 46
    assert rand_d101("P91") == "rândul 9.1"
    assert rand_d101("P4221") == "rândul 42.2.1"
    assert rand_d101("P53") == "rândul 53"
    assert rand_d101("P38a") == "rândul 38a"
    assert rand_d101("X1") == "X1"
