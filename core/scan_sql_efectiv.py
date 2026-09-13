# -*- coding: utf-8 -*-
"""SQL-ul EFECTIV al unei funcții — cel scris în ea plus cel chemat din depozitul ei.

DE CE EXISTĂ (13.09.2026, valul D4 al lui P7). Până azi, întrebarea *„ce SQL execută funcția asta?"*
se răspundea citind literalele din corpul ei. Valul D4 a mutat **215 instrucțiuni** din 37 de module
în `core/repo_*.py`, iar toate instrumentele care puneau întrebarea au început, în aceeași clipă, să
răspundă **„niciunul"** — nu greșit, ci despre altă lume. Șase gărzi au căzut la prima rulare a
suitei, printre ele una care întreabă *«din câte locuri se naște o factură»* și una care verifică
*«rândul de audit nu mai produce orfani»*.

*Când o fază mută codul, instrumentele care îl citeau trebuie să se mute cu el — altfel măsoară
stratul greșit și o spun cu convingere.* Aceeași clasă cu `scan_trasee`, care a tăcut de două ori în
două valuri, și cu [[gard-care-nu-se-verifica-pe-sine]].

CONTRACTUL, îngust dinadins:
  · se urmărește **un singur pas**, și numai către DEPOZITUL NOMINAL al modulului
    (`core/X.py` → `core/repo_X.py`). Nu e o închidere tranzitivă: un modul nu capătă prin ea decât
    ce și-a dat singur;
  · SQL-ul se ia din **argumentul apelului**, ca nod, nu prin căutare de șiruri în fișier;
  · atribuirea e la funcția APELANTĂ. Întrebarea *„cine face X"* e despre aplicație, nu despre
    stratul în care a ajuns instrucțiunea.

CE NU FACE, declarat: nu urmărește apeluri prin variabile, nu rezolvă depozite chemate sub alt alias
decât `_repo`, și nu coboară în alte module. Ce nu poate rezolva, nu inventează.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: aliasul sub care valul D4 a legat fiecare modul de depozitul lui
ALIAS = "_repo"


def perechea(cale_rel):
    """`core/d406.py` → `core/repo_d406.py`, dacă există; altfel None."""
    baza = os.path.basename(cale_rel)
    if baza.startswith("repo_"):
        return None
    # Depozitul unui modul din radacina (`main.py`) sta tot in `core/`; fara asta perechea
    # nu se gaseste, iar instrumentul raporteaza ABSENTA in loc de necunoastere.
    dosar = os.path.dirname(cale_rel) or "core"
    pereche = os.path.join(dosar, "repo_" + baza).replace(os.sep, "/")
    return pereche if os.path.exists(os.path.join(RAD, pereche)) else None


def _arbore(cale_rel):
    return ast.parse(io.open(os.path.join(RAD, cale_rel), encoding="utf-8").read())


def litera(nod):
    """Litera SQL a unui argument de `execute`, ca text. `{…}` rămâne `{}` — nu se inventează."""
    a = nod
    while isinstance(a, ast.BinOp):
        a = a.left
    if isinstance(a, ast.Constant) and isinstance(a.value, str):
        return a.value
    if isinstance(a, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in a.values)
    if isinstance(a, ast.Call):
        f = a.func
        if isinstance(f, ast.Attribute) and f.attr == "format" and a.args is not None:
            return litera(f.value)
    return ""


def _executii_directe(nod):
    return [litera(n.args[0]) for n in ast.walk(nod)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr in ("execute", "executemany") and n.args]


def _functii_depozit(cale_repo):
    """{nume: nod} pentru funcțiile depozitului."""
    return {f.name: f for f in ast.walk(_arbore(cale_repo))
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _apeluri_depozit(nod):
    """Numele funcțiilor de depozit chemate în `nod`, în ordinea apariției."""
    out = []
    for n in ast.walk(nod):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name) and n.func.value.id == ALIAS):
            out.append(n.func.attr)
    return out


def sql_din_nod(cale_rel, nod):
    """SQL-ul efectiv al unui nod din modulul `cale_rel`: direct + prin depozitul nominal."""
    out = list(_executii_directe(nod))
    repo = perechea(cale_rel)
    if repo:
        fn_repo = _functii_depozit(repo)
        for nume in _apeluri_depozit(nod):
            f = fn_repo.get(nume)
            if f is not None:
                out += _executii_directe(f)
    return out


def sql_functie(cale_rel, nume_functie):
    for f in ast.walk(_arbore(cale_rel)):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == nume_functie:
            return sql_din_nod(cale_rel, f)
    raise LookupError("%s n-are functia %s" % (cale_rel, nume_functie))


def sql_modul(cale_rel):
    return sql_din_nod(cale_rel, _arbore(cale_rel))


def executii_pe_functie(cale_rel):
    """[(nume_functie, sql)] — fiecare instrucțiune, atribuită funcției APELANTE."""
    arb = _arbore(cale_rel)
    repo = perechea(cale_rel)
    fn_repo = _functii_depozit(repo) if repo else {}
    linie_fn = {}
    for f in ast.walk(arb):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for ln in range(f.lineno, (f.end_lineno or f.lineno) + 1):
                linie_fn.setdefault(ln, f.name)
    out = []
    for n in ast.walk(arb):
        if not isinstance(n, ast.Call):
            continue
        gazda = linie_fn.get(n.lineno, "<modul>")
        if isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executemany") and n.args:
            out.append((gazda, litera(n.args[0])))
        elif (isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                and n.func.value.id == ALIAS):
            f = fn_repo.get(n.func.attr)
            if f is not None:
                out += [(gazda, s) for s in _executii_directe(f)]
    return out
