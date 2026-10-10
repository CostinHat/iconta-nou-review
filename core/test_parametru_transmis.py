# -*- coding: utf-8 -*-
"""GARD — o valoare primită de un înveliș ajunge la funcția pe care o învelește (10.10.2026).

Instanța care a deschis clasa: `facturi_api.emite_factura(..., tert_pf=True)` dădea `tert_pf` lui `cere_cod_partener`, dar nu și lui
`creeaza_factura`, care îl are cu implicitul `False` — deci refuza a doua oară partenerul persoană fizică fără cod. Orice comandă
din magazinul online (`woocommerce._importa`, persoane fizice) era refuzată. Găsită de proba R193 (`test_r193_model_fara_conexiune`).

Clasa: funcția F are parametrul `p`, cheamă G, G are `p` cu valoare implicită, iar apelul nu i-l dă — nici cu nume, nici pe
poziție, nici prin `**`. Măsurat pe tot `core/` + `main.py`: 3 apariții — `emite_factura -> creeaza_factura: tert_pf` și
`spv_refresh.ruleaza -> reimprospateaza_token: acum` (selecția după `acum`, expirarea după ceasul real), reparate; a treia,
`etransport_send.fereastra_uit -> azi_ro: acum`, nu pierde nimic: `acum if acum is not None else azi_ro()` folosește chiar valoarea
primită, iar G e chemată numai în lipsa ei — forma asta se recunoaște și nu se numără.

Limita, declarată: G se rezolvă după nume, numai când numele e unic în cod; parametrii de infrastructură (`conn`, `cur`, `schema`,
`ctx`) nu se judecă — conexiunea poartă deja schema, iar contextul cererii nu se transmite mai departe prin nume.
"""
import ast
import glob
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFRASTRUCTURA = {"self", "cls", "conn", "cur", "c", "schema", "ctx"}


def _toti(fn):
    a = fn.args
    return [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]


def _cu_implicit(fn):
    a = fn.args
    poz = a.posonlyargs + a.args
    out = [x.arg for x in poz[len(poz) - len(a.defaults):]] if a.defaults else []
    return out + [x.arg for x, v in zip(a.kwonlyargs, a.kw_defaults) if v is not None]


def pierderi(surse):
    """[(fișier, linie, F, G, p)] peste `{fișier: sursă}`."""
    arbori = {f: ast.parse(s) for f, s in surse.items()}
    defs = {}
    for a in arbori.values():
        for n in ast.walk(a):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs.setdefault(n.name, []).append(n)
    out = []
    for f, a in arbori.items():
        parinte = {c: n for n in ast.walk(a) for c in ast.iter_child_nodes(n)}
        for fn in ast.walk(a):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            pf = set(_toti(fn)) - INFRASTRUCTURA
            for n in ast.walk(fn):
                if not isinstance(n, ast.Call):
                    continue
                nume = n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else None)
                if not nume or nume == fn.name or len(defs.get(nume, ())) != 1:
                    continue
                if any(k.arg is None for k in n.keywords) or any(isinstance(x, ast.Starred) for x in n.args):
                    continue
                g = defs[nume][0]
                date = {k.arg for k in n.keywords} | set(_toti(g)[:len(n.args)])
                p_sus = parinte.get(n)
                # `p if p is not None else G()`: G e chemată numai în lipsa valorii primite, care se folosește ea însăși
                alternativa = (isinstance(p_sus, ast.IfExp) and p_sus.orelse is n
                               and {x.id for x in ast.walk(p_sus.test) if isinstance(x, ast.Name)})
                for p in sorted(pf & set(_cu_implicit(g)) - date - (alternativa or set())):
                    out.append((f, n.lineno, fn.name, nume, p))
    return out


def _cod():
    fis = [f for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) + [os.path.join(RAD, "main.py")]
           if not os.path.basename(f).startswith("test_")]
    return {os.path.relpath(f, RAD): io.open(f, encoding="utf-8").read() for f in fis}


def test_nicio_valoare_primita_nu_se_pierde_pe_drum():
    """MUTAȚIE: `tert_pf=tert_pf` scos din apelul `creeaza_factura` din `emite_factura` -> pică (și proba magazinului din
    `test_r193_model_fara_conexiune` pică pe refuzul codului fiscal)."""
    gasite = pierderi(_cod())
    assert not gasite, "Valori primite și netransmise funcției care le are:\n" + "\n".join(
        "  %s:%d %s -> %s: `%s`" % g for g in gasite)


def test_detectorul_are_dinti():
    src = ("def g(a, tert_pf=False, acum=None):\n    pass\n"
           "def f(a, tert_pf=False):\n    g(a)\n"                                   # pierdut
           "def h(a, tert_pf=False):\n    g(a, tert_pf=tert_pf)\n"                  # transmis
           "def k(a, acum=None):\n    x = acum if acum is not None else g(a)\n"     # folosit el însuși
           "def m(a, tert_pf=False):\n    g(a, **{'tert_pf': tert_pf})\n")          # prin ** — nu se poate judeca
    assert [(F, G, p) for _f, _l, F, G, p in pierderi({"x.py": src})] == [("f", "g", "tert_pf")]
