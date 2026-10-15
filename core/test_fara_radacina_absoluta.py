# -*- coding: utf-8 -*-
"""GARD C35 — nicio cale absolută spre checkout-ul publicat în codul depozitului (decizia Costin 15.10.2026, verbatim în DECIZII
„Lotul 3 — C35”: „rădăcina calculată din fișierul însuși în verificator, scanuri și uneltele din poartă; efactura_zip inclus, cu
aceeași cale calculată (în producție rezultatul identic). Gard «nicio cale absolută spre ~/iconta_nou» în codul judecat de poartă, cu
mutație.”).

DE CE. Din 14.10.2026 lucrul se face într-un worktree, iar `~/iconta_nou` e versiunea PUBLICATĂ. Un instrument cu rădăcina scrisă
`/home/costin/iconta_nou` judecă, rulat din worktree, codul publicat, nu commitul: verificatorul de conformitate din poarta lotului 2
a scanat arborele publicat (448 de rute, față de 451 în arborele lotului 3), iar clichetul constantelor a fost măsurat pe alt arbore.
Rădăcina se calculează acum din fișierul însuși (`os.path.dirname(os.path.abspath(__file__))`, `$(dirname "$0")`,
`new URL("..", import.meta.url)`); în producție dă exact același director.

CE SE SCANEAZĂ: toate fișierele urmărite de git cu cod executabil (`.py`, `.sh`, `.mjs`, `.js`, hook-urile din `scripts/githooks/`).
În Python se citesc numai literalele de COD (AST), fără docstringuri și comentarii — proza care numește checkout-ul de producție
(„rulează pe server, din ~/iconta_nou”) nu deschide niciun fișier. În shell / JS se sar liniile de comentariu.
MUTAȚIA: `RAD = "/home/costin/iconta_nou/core"` repus în `core/scan_constante.py` -> ROȘU, cu fișierul și linia."""
import ast
import os
import re
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIPAR = re.compile(r"(?:/home/costin|~)/iconta_nou")
EXTENSII = (".py", ".sh", ".mjs", ".js")


def _fisiere_cod():
    r = subprocess.run(["git", "ls-files", "-z"], cwd=_RAD, capture_output=True, timeout=60, check=True)
    toate = [f for f in r.stdout.decode("utf-8").split("\0") if f]
    return [f for f in toate if f.endswith(EXTENSII) or (f.startswith("scripts/githooks/") and "." not in os.path.basename(f))]


def _docstringuri(arbore):
    ids = set()
    for n in ast.walk(arbore):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            b = n.body[0]
            if isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant) and isinstance(b.value.value, str):
                ids.add(id(b.value))
    return ids


def aparitii(rel, src):
    """[(linie, text)] — căile absolute spre checkout-ul publicat din codul executabil al unui fișier."""
    if rel.endswith(".py"):
        arbore = ast.parse(src, filename=rel)
        doc = _docstringuri(arbore)
        return sorted({(n.lineno, n.value[:120]) for n in ast.walk(arbore)
                       if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc and TIPAR.search(n.value)})
    gasite = []
    for nr, linie in enumerate(src.split("\n"), 1):
        s = linie.strip()
        if s.startswith(("#", "//", "*", "/*")):
            continue
        if TIPAR.search(linie):
            gasite.append((nr, s[:120]))
    return gasite


def test_nicio_cale_absoluta_spre_checkoutul_publicat_in_cod():
    fisiere = _fisiere_cod()
    assert len(fisiere) > 500, ("anti-vacuu: `git ls-files` a dat %d fișiere de cod" % len(fisiere))
    rele = []
    for rel in fisiere:
        src = open(os.path.join(_RAD, rel), encoding="utf-8", errors="replace").read()
        rele += ["%s:%d  %s" % (rel, nr, t) for nr, t in aparitii(rel, src)]
    assert rele == [], ("cale absolută spre checkout-ul publicat (C35) — din worktree ar judeca alt arbore decât commitul; calculeaz-o "
                        "din fișier (os.path.dirname(os.path.abspath(__file__)) / $(dirname \"$0\")):\n  " + "\n  ".join(rele))


def test_CALIBRARE_detectorul_vede_formele_si_sare_proza():
    """Direcția «scapă»: literalul, `expanduser`, f-string, shell, JS. Direcția «acuză pe nedrept»: docstring, comentariu."""
    # literalele de calibrare se compun din bucăți, ca fișierul acesta să nu se acuze singur
    a, t = "/home/costin" + "/iconta_nou", "~" + "/iconta_nou"
    py = ('"""Rulează pe server, din %(t)s."""\n'
          'import os\n'
          '# cd %(t)s\n'
          'A = "%(a)s/core"\n'
          'B = os.path.expanduser("%(t)s/static")\n'
          'C = f"%(a)s/{A}"\n'
          'def f():\n    """din %(t)s"""\n    return 1\n') % {"a": a, "t": t}
    assert [nr for nr, _ in aparitii("x.py", py)] == [4, 5, 6]
    assert [nr for nr, _ in aparitii("x.sh", "# cd %s\nRAD=%s\ncd %s\n" % (t, t, a))] == [2, 3]
    assert [nr for nr, _ in aparitii("x.mjs", '// %s\nconst P = "%s/static";\n' % (t, a))] == [2]
    assert aparitii("x.py", 'import os\nRAD = os.path.dirname(os.path.abspath(__file__))\n') == []
