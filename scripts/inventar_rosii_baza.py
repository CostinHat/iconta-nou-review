# -*- coding: utf-8 -*-
"""scripts/inventar_rosii_baza.py — inventarul testelor roșii pe bază, cu cauza (17.5-U, U.7). Fără rulare: citește rândurile «FAILED <fișier>::<test>» ale unei intrări
(antet cu «main <sha de 40 de cifre>») și hotărăște cauza din numele testului și din codul lui de pe commitul din antet (git show <sha>:<cale>), nu din arborele de lucru.

Uz:
  inventar_rosii_baza.py <fișier de intrare> [--iesire=<cale>] [--depozit=<director git>]
  Scrie docs/dovezi/17_5_U/inventar_rosii_baza.txt (sau --iesire), un rând pe FAILED: fișier | test | cauza | fișier:linie. Ieșire 1 dacă numărul rândurilor scrise diferă de al celor FAILED.
Cauze, prima potrivire: necunoscută (funcția sau fișierul lipsesc), ceas înghețat, luna curentă, data de azi, ceasul paginii, altă cauză."""
import ast
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argumente_script  # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISIERE_AJUTOR = ("frontend_test/e2e/conftest.py", "core/ceas_proba.py")
CEAS_REAL = ("date.today", "datetime.now", "datetime.datetime.now", "new Date", "Date.now")
CALENDAR = (".month", ".year", "strftime(", "%B", "%m", "%Y")
CEAS_PAGINA = ("new Date", "Date.now")
ID_RE = re.compile(r"#([A-Za-z][A-Za-z0-9_-]{3,})")


def _git(depozit, *a):
    r = subprocess.run(["git", *a], cwd=depozit, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


class Commit:
    """Fișierele unui commit, citite cu git show (cu cache)."""

    def __init__(self, depozit, sha):
        self.depozit, self.sha, self._c = depozit, sha, {}
        self.caile = (_git(depozit, "ls-tree", "-r", "--name-only", sha) or "").splitlines()

    def text(self, cale):
        if cale not in self._c:
            self._c[cale] = _git(self.depozit, "show", "%s:%s" % (self.sha, cale))
        return self._c[cale]

    def pagini(self):
        return sorted(c for c in self.caile if (c.startswith("static/js/") and c.endswith(".js")) or (c.startswith("templates/") and c.endswith(".html")))


def _functii(text):
    """-> {nume: FunctionDef} la nivelul modulului (și în clase) + arborele."""
    try:
        arbore = ast.parse(text)
    except SyntaxError:
        return {}, None
    return {n.name: n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}, arbore


def _linii(cale, text, nod):
    lst = text.splitlines()
    return [(cale, i, lst[i - 1]) for i in range(nod.lineno, (nod.end_lineno or nod.lineno) + 1)]


def _nume_folosite(nod):
    return {n.id for n in ast.walk(nod) if isinstance(n, ast.Name)}


def domeniu(commit, cale, test):
    """Domeniul testului (U.7): corpul funcției, corpul funcțiilor chemate prin nume (un nivel; din același fișier, din conftest.py al plasei sau din core/ceas_proba.py) și
    liniile atribuirilor / importurilor cu alias de nivel de modul ale numelor folosite. -> (linii [(cale, nr, text)], nodul testului sau None)."""
    text = commit.text(cale)
    if text is None:
        return [], None
    fct, arbore = _functii(text)
    nod = fct.get(test.split("[")[0])
    if nod is None:
        return [], None
    linii = _linii(cale, text, nod)
    folosite = _nume_folosite(nod)
    chemate = {n.func.id for n in ast.walk(nod) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    corpuri = [nod]
    for sursa in (cale,) + FISIERE_AJUTOR:
        t = text if sursa == cale else commit.text(sursa)
        if t is None:
            continue
        f2, _ = _functii(t)
        for nume in sorted(chemate):
            if nume in f2 and f2[nume] is not nod:
                linii += _linii(sursa, t, f2[nume])
                folosite |= _nume_folosite(f2[nume])
    if arbore is not None:
        lst = text.splitlines()
        for n in arbore.body:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in folosite for t in n.targets):
                linii += [(cale, i, lst[i - 1]) for i in range(n.lineno, (n.end_lineno or n.lineno) + 1)]
            elif isinstance(n, (ast.Import, ast.ImportFrom)) and any((a.asname or a.name.split(".")[0]) in folosite for a in n.names):
                linii.append((cale, n.lineno, lst[n.lineno - 1]))
    return linii, nod


def _prima(linii, jetoane):
    for cale, nr, t in linii:
        if any(j in t for j in jetoane):
            return "%s:%d" % (cale, nr)
    return None


def _in_pagina(commit, ids):
    """Fișierele-pagină care conțin un id deschis de test ca cuvânt întreg -> prima apariție «new Date» / «Date.now» (fișier:linie) sau None."""
    if not ids:
        return None
    for cale in commit.pagini():
        t = commit.text(cale) or ""
        if any(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(i), t) for i in ids):
            for nr, ln in enumerate(t.splitlines(), 1):
                if any(j in ln for j in CEAS_PAGINA):
                    return "%s:%d" % (cale, nr)
    return None


def cauza(commit, cale, test):
    """-> (cauza, fișier:linie)."""
    linii, nod = domeniu(commit, cale, test)
    if nod is None:
        return "necunoscută", "-"
    text = "\n".join(t for _, _, t in linii)
    ids = sorted({i for i in ID_RE.findall(text) if not i.endswith("-")})
    ceas = _prima(linii, CEAS_REAL)
    fix = any(j in text for j in ("DATA_REF", "MOMENT_REF"))
    pagina = _in_pagina(commit, ids)
    if fix and "pagina_cu_ceas_fix(" not in text and "set_fixed_time(" not in text and pagina:
        return "ceas înghețat", pagina
    if ceas and any(j in text for j in CALENDAR):
        return "luna curentă", ceas
    if ceas:
        return "data de azi", ceas
    if not fix and pagina:
        return "ceasul paginii", pagina
    return "altă cauză", "%s:%d" % (cale, nod.lineno)


def citeste_intrare(text):
    antet = re.search(r"\bmain ([0-9a-f]{40})\b", text.splitlines()[0] if text.strip() else "")
    cazute = []
    for ln in text.splitlines():
        m = re.match(r"FAILED (\S+?)::(\S+)", ln.strip())
        if m:
            cazute.append((m.group(1), m.group(2)))
    return (antet.group(1) if antet else None), cazute


def main(argv):
    a = argumente_script.citeste(argv, __doc__, cu_valoare=("--iesire=", "--depozit="), pozitionale=1, prefix="[inventar_rosii_baza]")
    poz = [x for x in a if not x.startswith("-")]
    if not poz:
        print("[inventar_rosii_baza] lipsește fișierul de intrare.\n" + __doc__[__doc__.index("Uz:"):], file=sys.stderr)
        return 2
    opt = {x.split("=", 1)[0]: x.split("=", 1)[1] for x in a if x.startswith("--")}
    depozit = opt.get("--depozit", RAD)
    iesire = opt.get("--iesire", os.path.join(RAD, "docs", "dovezi", "17_5_U", "inventar_rosii_baza.txt"))
    sha, cazute = citeste_intrare(open(poz[0], encoding="utf-8").read())
    if not sha:
        print("[inventar_rosii_baza] antetul nu are «main <sha de 40 de cifre>».", file=sys.stderr)
        return 1
    commit = Commit(depozit, sha)
    randuri = []
    for fis, test in cazute:
        c, loc = cauza(commit, fis, test)
        randuri.append("%s | %s | %s | %s" % (fis, test, c, loc))
    os.makedirs(os.path.dirname(iesire) or ".", exist_ok=True)
    with open(iesire, "w", encoding="utf-8") as f:
        f.write("".join(r + "\n" for r in randuri))
    if len(randuri) != len(cazute):
        print("[inventar_rosii_baza] %d rânduri scrise, %d FAILED în intrare." % (len(randuri), len(cazute)), file=sys.stderr)
        return 1
    print("[inventar_rosii_baza] %d rânduri în %s" % (len(randuri), iesire))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
