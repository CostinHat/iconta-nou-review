# -*- coding: utf-8 -*-
"""[metoda-ca-poarta] GARD: INSTRUMENTE_ROADMAP.md nu minte — un instrument marcat CONSTRUIT trebuie sa
numeasca un fisier-garda care EXISTA (simetric cu GARZI ACOPERIT). Asa 'construit' e un fapt, nu o afirmatie.
Plus: cele 11 propuneri agreate raman toate in roadmap (nu se pierd din chat)."""
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


def test_toate_cele_11_propuneri_prezente():
    s = _roadmap()
    lipsa = [n for n in range(1, 12) if ("#%d " % n) not in s]
    assert not lipsa, "propuneri lipsa din roadmap: %s" % lipsa
