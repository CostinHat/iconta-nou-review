# -*- coding: utf-8 -*-
"""GARD — o cheie de registru nu se repetă (comanda Costin 07.10.2026, C7).

Instanța: în registrul „Operațiuni speciale” două operațiuni aveau cheia `agricultor`; ecranul alege cu `REGISTRU.find(cheie)`,
deci butonul „Achiziție de la agricultor (compensare 8%)” deschidea formularul „Vânzare către agricultor” și scria o VÂNZARE.
Clasa: orice registru căutat după cheie — tablourile `{ cheie: … }` din ecrane, obiectele literale JS (`const X = { k: … }`, unde
o cheie repetată o înlocuiește tacit pe prima) și dicționarele literale din Python (la fel). Măsurat la 07.10: o singură
apariție (cea de mai sus); 132 de obiecte JS și 6.188 de dicționare Python curate.
LIMITA: obiectele JS se citesc lexical (nivelul întâi al acoladelor); o cheie calculată (`[k]: v`) nu se vede.
"""
import ast
import collections
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = sorted(glob.glob(os.path.join(RAD, "static/js/**/*.js"), recursive=True))


def _dublate(chei):
    return sorted(k for k, n in collections.Counter(chei).items() if n > 1)


def test_cheile_din_registrele_ecranelor_sunt_unice():
    """MUTAȚIE: cheia `agricultor_achizitie` dată înapoi la `agricultor` -> pică."""
    rele = {os.path.relpath(f, RAD): _dublate(re.findall(r'\bcheie:\s*"([^"]+)"', open(f, encoding="utf-8").read())) for f in JS}
    assert {f: d for f, d in rele.items() if d} == {}


def _obiecte(s):
    for m in re.finditer(r"(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=\s*\{", s):
        i = j = m.end(); d = 1
        while j < len(s) and d:
            c = s[j]
            if c in "{[(":
                d += 1
            elif c in "}])":
                d -= 1
            elif c in "\"'`":
                j += 1
                while j < len(s) and s[j] != c:
                    j += 2 if s[j] == "\\" else 1
            j += 1
        plat, d = [], 0
        for c in s[i:j - 1]:
            if c in "{[(":
                d += 1
            elif c in "}])":
                d -= 1
            elif d == 0:
                plat.append(c)
        yield m.group(1), [a or b for a, b in re.findall(r'(?:^|[,\n])\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*))\s*:', "".join(plat))]


def test_obiectele_literale_din_ecrane_nu_repeta_chei():
    rele, n = [], 0
    for f in JS:
        for nume, chei in _obiecte(open(f, encoding="utf-8").read()):
            n += 1
            if _dublate(chei):
                rele.append((os.path.relpath(f, RAD), nume, _dublate(chei)))
    assert n > 100                                                   # premisă: obiectele chiar s-au citit
    assert rele == []


def test_dictionarele_literale_din_python_nu_repeta_chei():
    rele, n = [], 0
    for f in glob.glob(os.path.join(RAD, "core", "*.py")) + [os.path.join(RAD, "main.py")]:
        try:
            t = ast.parse(open(f, encoding="utf-8").read())
        except SyntaxError:
            continue
        for d in ast.walk(t):
            if isinstance(d, ast.Dict):
                n += 1
                ks = [k.value for k in d.keys if isinstance(k, ast.Constant)]
                if _dublate(ks):
                    rele.append((os.path.relpath(f, RAD), d.lineno, _dublate(ks)))
    assert n > 1000
    assert rele == []
