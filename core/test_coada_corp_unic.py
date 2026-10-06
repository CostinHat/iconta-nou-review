# -*- coding: utf-8 -*-
"""GARD — ce se trimite în coadă e exact ce s-a generat și validat (comanda Costin 07.10.2026, C2).

Instanța: D307 completat pe ecran, DUK „fără erori” la pasul 2, apoi „Trimite în coadă” -> „D307 nu are ce genera”: pasul 3 își
construia SINGUR corpul, fără formularul manual și fără obligațiile D710; iar serverul (`CoadaIn`) nici nu primea `obligatii`.
CE FACE IMPOSIBIL: (1) un corp al cozii construit altfel decât cel al generării (ecranul are UN constructor, `corpGenerare`);
(2) un câmp pe care generarea îl primește (`DeclaratieIn`) și coada îl aruncă tacit (`CoadaIn`).
"""
import ast
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = open(os.path.join(RAD, "static/js/ecrane/declaratii.js"), encoding="utf-8").read()


def _functie(nume):
    i = JS.index("function %s(" % nume)
    j = JS.index("\n}\n", i)
    return JS[i:j]


def test_pasul_2_si_pasul_3_folosesc_acelasi_constructor():
    """MUTAȚIE: pasul 3 cu `const body = { tenant_id: … }` construit pe loc -> pică."""
    assert re.search(r"const body = corpGenerare\(\);", _functie("pas2"))
    assert re.search(r"const body = Object\.assign\(corpGenerare\(\),", _functie("pas3"))
    assert not re.search(r"const body = \{", _functie("pas3"))


def test_constructorul_poarta_toate_formularele_manuale():
    """Fiecare `_dXXXManual()` din ecran ajunge în corp; D710 își trimite obligațiile."""
    corp = _functie("corpGenerare")
    toate = set(re.findall(r"function (_d\d{3}Manual)\(", JS))
    assert len(toate) >= 20                                         # premisă: formularele chiar s-au citit
    lipsa = sorted(f for f in toate if not re.search(r"body\.manual = %s\(\)" % f, corp))
    assert lipsa == []
    assert re.search(r"body\.obligatii = S\.d710_obligatii", corp)


def _campuri(clasa):
    t = ast.parse(open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    c = [n for n in ast.walk(t) if isinstance(n, ast.ClassDef) and n.name == clasa][0]
    return {s.target.id for s in c.body if isinstance(s, ast.AnnAssign)}


def test_coada_primeste_tot_ce_primeste_generarea():
    """MUTAȚIE: `obligatii` scos din `CoadaIn` -> pică."""
    assert sorted(_campuri("DeclaratieIn") - _campuri("CoadaIn")) == []
