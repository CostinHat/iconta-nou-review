# -*- coding: utf-8 -*-
"""Lotul 11, subagentul U0 — regulile verificatorului pentru 440 / 441 / 443 / 445 (comanda Costin 11.1 pct.16, 17, 19, 21, verbatim în
DECIZII „Comanda 11.1”): ERORI_TOATE, DATA_GOLIBILA, SERIE_LIPITA, INTOARCERE_DIN_REFUZ (DS v2.99).

Temei: N/A — reguli de interfață.

Logica REALĂ, scoasă din `verificator_conformitate.py` cu `ast` (tiparul `core/test_lot11_j_verificator.py`): fiecare cod are fragmentul
rău care trebuie prins și fragmentul bun care nu; apoi fișierele reale. Plus textele trimise ecranului din core/ (Python): fără
„(vezi mai sus)” / „motivul e mai jos” în locul textului erorii.
"""
import ast
import glob
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _citeste(rel):
    return io.open(os.path.join(_RAD, rel), encoding="utf-8").read()


@pytest.fixture(scope="module")
def regula():
    arb = ast.parse(_citeste("verificator_conformitate.py"))
    noduri = [n for n in arb.body if (isinstance(n, ast.FunctionDef) and n.name == "analiza_lot11_u0")
              or (isinstance(n, ast.Assign) and any(getattr(x, "id", None) == "_MAI_SUS" for x in n.targets))]
    assert len(noduri) == 2, "ANTI-VACUU: regula lotului 11 (U0) lipsește din verificator"
    assert [n for n in arb.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript)
            and getattr(n.targets[0].slice, "value", None) == "lot11_u0"], "verificatorul nu mai cheamă analiza_lot11_u0"
    ns = {"re": re}
    exec(compile(ast.Module(body=noduri, type_ignores=[]), "verificator_conformitate.py", "exec"), ns)
    return ns["analiza_lot11_u0"]


def _reale():
    f = {}
    for d in (os.path.join(_RAD, "static", "js", "ecrane"), os.path.join(_RAD, "static", "js")):
        for x in sorted(os.listdir(d)):
            if x.endswith(".js") and ".bak" not in x and x not in f:
                f[x] = io.open(os.path.join(d, x), encoding="utf-8").read()
    return f


def _coduri(rez):
    return sorted({c for _, _, c, _ in rez})


def test_fragmentele_rele_sunt_prinse(regula):
    """MUTAȚIE: oricare din cele patru ramuri ale regulii scoasă -> codul ei lipsește din listă -> pică."""
    f = _reale()
    rau = dict(f)
    rau["api.js"] = f["api.js"].replace('a.textContent = (mesaj.textContent || "").trim();',
                                        'a.textContent = "motivul e " + (jos ? "mai jos" : "mai sus");')
    rau["navigator.js"] = f["navigator.js"].replace("_dePastrat(dinRefuz)", "_dePastrat()")
    rau["x_ecran.js"] = ('const a = `Factura ${f.serie}${f.numar}`;\n'
                         'arataMesaj(z, "Nu s-a salvat — motivul e mai sus.", "eroare");\n')
    gasite = regula(rau, ".data-golibila { display: flex; }")
    assert {("api.js", "ERORI_TOATE"), ("navigator.js", "INTOARCERE_DIN_REFUZ"), ("x_ecran.js", "SERIE_LIPITA"),
            ("x_ecran.js", "ERORI_TOATE")} <= {(n, c) for n, _, c, _ in gasite}, gasite
    assert ("stil.css", 0, "DATA_GOLIBILA") in [(n, i, c) for n, i, c, _ in regula(f, "/* fara regula */")]


def test_fragmentele_bune_nu_sunt_prinse(regula):
    """Forma corectă: `numarCuSerie`, textul erorii, fraza despre conținut („o vezi mai jos”) — niciun cod."""
    bun = {"x_ecran.js": 'const a = `Factura ${esc(numarCuSerie(f.serie, f.numar))}`;\n'
                         'arataMesaj(z, "Nota e generată — o vezi mai jos.", "ok");\n'
                         'arataMesaj(z, "Perioada 09/2026 e încheiată.", "eroare");\n'}
    assert regula(bun, "") == [x for x in regula(bun, "") if x[0] in ("api.js", "navigator.js", "ecran_destinatie.js")]


def test_fisierele_reale_sunt_curate(regula):
    """Fișierele reale: zero. (Roșu până se aplică listele de lucru ale lui U0 pe firme.js / facturi_ecran.js / emitere_ecran.js /
    date_firma.js / compensari_ecran.js — `scratchpad/agenti/u0_lista_*.md`.)"""
    rez = regula(_reale(), _citeste("static/stil.css"))
    assert not rez, "\n".join("%s:%d %s %s" % x for x in rez)


_MAI_SUS_PY = re.compile(r"(?:motivul e|motivele(?: sunt)?|\(vezi|marcat|marcate)\s+(?:de\s+)?mai\s+(?:sus|jos)", re.I)


def test_textele_din_core_nu_trimit_la_mai_sus():
    """440 în textele trimise ecranului de server: „(vezi mai sus)” în locul textului. Se citesc numai șirurile (ast), nu comentariile.
    MUTAȚIE: `"%s din declarație (vezi mai sus)."` repus în d394 -> pică."""
    rele = []
    for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))):
        nume = os.path.basename(p)
        if nume.startswith(("test_", "scan_")):
            continue
        src = io.open(p, encoding="utf-8").read()
        if "mai sus" not in src and "mai jos" not in src:
            continue
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and _MAI_SUS_PY.search(n.value) and not n.value.lstrip().startswith(("[", "**")):
                if isinstance(getattr(n, "parent", None), ast.Expr):
                    continue
                rele.append("%s:%d" % (nume, n.lineno))
    # docstring-urile nu sunt texte pentru om: se scot (primul șir din modul / funcție / clasă)
    doc = set()
    for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))):
        for n in ast.walk(ast.parse(io.open(p, encoding="utf-8").read())):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr) \
                    and isinstance(getattr(n.body[0], "value", None), ast.Constant):
                doc.add("%s:%d" % (os.path.basename(p), n.body[0].value.lineno))
    rele = [r for r in rele if r not in doc]
    assert not rele, "trimitere „mai sus / mai jos” în locul textului erorii (440): %s" % rele
