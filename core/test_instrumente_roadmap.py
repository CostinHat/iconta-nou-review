# -*- coding: utf-8 -*-
"""[metoda-ca-poarta] GARD: INSTRUMENTE_ROADMAP.md nu minte — un instrument marcat CONSTRUIT trebuie sa
numeasca un fisier-garda care EXISTA (simetric cu GARZI ACOPERIT). Asa 'construit' e un fapt, nu o afirmatie.

EXTINS 21.08.2026: roadmap-ul trebuie sa poata CRESTE. Vechea versiune cerea exact propunerile #1..#11,
hardcodat — deci al 12-lea instrument (scanul de constante) a putut fi construit si folosit doua zile
fara ca registrul sa afle. Numarul declarat se citeste acum DIN document si se confrunta cu ce e in el:
ca sa adaugi un instrument, esti obligat sa cresti numarul, iar ca sa cresti numarul esti obligat sa-l
adaugi. Nu prinde omisiunea totala (vezi 'CE NU E GARDAT' din roadmap — trei definitii calibrate si
respinse), dar inchide drumul pe care s-a intamplat de fapt.
"""
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _roadmap():
    p = os.path.join(_RAD, "INSTRUMENTE_ROADMAP.md")
    if not os.path.exists(p):
        pytest.fail("INSTRUMENTE_ROADMAP.md lipseste")
    return open(p, encoding="utf-8").read()


def test_construit_numeste_fisiere_care_exista():
    sus = _roadmap().split("## Propuse")[0]
    fisiere = re.findall(r'`(core/[\w/]+\.py|frontend_test/[\w/]+\.py)`', sus)
    assert fisiere, "sectiunea Construite nu numeste niciun fisier-garda"
    lipsa = [f for f in fisiere if not os.path.exists(os.path.join(_RAD, f))]
    assert not lipsa, "INSTRUMENTE_ROADMAP 'Construite' numeste fisiere inexistente: %s" % lipsa


def _declarat(s):
    m = re.search(r"INSTRUMENTE DECLARATE:\s*(\d+)", s)
    assert m, ("roadmap-ul nu-si mai declara numarul de instrumente — randul "
               "'**INSTRUMENTE DECLARATE: N.**' e ancora prin care registrul poate creste")
    return int(m.group(1))


def _gasite(s):
    return {int(n) for n in re.findall(r"#(\d+)\s", s)}


def test_numarul_declarat_se_potriveste_cu_ce_e_in_document():
    """Miezul extinderii. Ca sa adaugi un instrument esti obligat sa cresti numarul; ca sa cresti
    numarul esti obligat sa adaugi instrumentul. Un registru care nu poate creste ramane in urma tacut."""
    s = _roadmap()
    n, gasite = _declarat(s), _gasite(s)
    lipsa = [i for i in range(1, n + 1) if i not in gasite]
    assert not lipsa, "declarate %d instrumente, dar lipsesc din document: %s" % (n, lipsa)
    peste = sorted(i for i in gasite if i > n)
    assert not peste, ("in document exista #%s, dar sunt declarate doar %d — creste numarul din "
                       "'INSTRUMENTE DECLARATE', altfel registrul minte prin omisiune"
                       % (peste, n))


def test_ordinea_de_atac_exista_si_e_confirmata():
    """Ordinea agreata traieste in registru, nu in chat (aceeasi regula ca pentru roadmap insusi).
    Fara ea, prioritatile se renegociaza tacit la fiecare tura."""
    s = _roadmap()
    assert "ORDINEA DE ATAC" in s, "roadmap-ul nu mai poarta ordinea de atac"
    assert re.search(r"\*\*P1\*\*", s) and re.search(r"\*\*P7\*\*", s), \
        "ordinea de atac nu mai e numerotata P1..P7"


def test_ce_nu_e_gardat_ramane_scris():
    """Anti-vacuu pe onestitate: limita gardului (direcția inversă n-are proxy mecanic) trebuie sa
    ramana in document. Stearsa, cineva o s-o reinventeze ca pe o descoperire — sau, mai rau, o s-o
    construiasca vida."""
    s = _roadmap()
    assert "CE NU E GARDAT" in s, "limita declarata a disparut din roadmap"
    assert "calibrare" in s.lower() or "calibrate" in s.lower(), \
        "motivul respingerii celor trei definitii nu mai e scris"
