# -*- coding: utf-8 -*-
"""UNEALTA MANUALA PERIODICA — detector de drift dus-intors al bifelor (NU test in suita).

Garda `test_agenda.py::test_verificarile_A_nu_sunt_in_urma_codului` compara doar CAPETELE: AST-ul functiei
de test la commitul de la √ vs la HEAD. Rateaza cazul in care capetele-s EGALE (garda verde) dar un commit
INTERMEDIAR a avut un AST diferit — functia a fost modificata dupa √, apoi readusa la forma de la √. O astfel
de schimbare dus-intors poate invalida tacit verificarea la sursa (√) fara ca garda sa semnaleze.

NU e in suita intentionat: reciteste istoricul git (zeci-sute de `git show`), prea scump per-commit. Se ruleaza
PERIODIC, la declansatori (vezi GARZI.md cat.9):
  (a) o bifa cu √ mai vechi de ~3 luni (ferestrele √->HEAD scurte n-au drift semnificativ);
  (b) repornirea unei campanii pe un cluster deja bifat (inainte de a te sprijini pe o bifa veche).

Rulare:  python3 -m core.agenda_drift
Iesire:  lista driftului dus-intors (cluster|modul, test, commitul intermediar); 0 = curat.
"""
import subprocess
import ast
import datetime
import pathlib

_RAD = pathlib.Path(__file__).resolve().parent.parent
_cache = {}


def _show(commit, path):
    k = (commit, path)
    if k not in _cache:
        _cache[k] = subprocess.run(["git", "-C", str(_RAD), "show", "%s:%s" % (commit, path)],
                                   capture_output=True, text=True).stdout
    return _cache[k]


def _ast_fn(src, nume):
    """ast.dump al functiei `nume` cu docstring scos; '<ABSENT>' daca lipseste; None la parse-fail.
    Aceeasi semantica ca _ast_functie din test_agenda.py (sursa de adevar a comparatiei bifelor)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == nume:
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
               and isinstance(b[0].value.value, str):
                node.body = b[1:]
            return ast.dump(node)
    return "<ABSENT>"


def _ast_multi(relpaths, commit, fn):
    pf = False
    for rp in relpaths:
        a = _ast_fn(_show(commit, rp), fn)
        if a is None:
            pf = True
        elif a != "<ABSENT>":
            return a
    return None if pf else "<ABSENT>"


def drift_dus_intors():
    """[(cluster, modul, functie, √-iso, commit_intermediar_scurt, e_stergere)] — functii cu capete
    EGALE (garda le vede verzi) dar cu cel putin un commit intermediar cu AST diferit."""
    from core import agenda
    azi = datetime.date.today()
    rows = agenda.stare_sesiune_a()["rows"]
    out = []
    for rand in rows:
        if not rand["verificat"] or "." not in rand["verificat"]:
            continue
        if not rand["fisiere"] or not rand.get("functie"):
            continue
        zi, luna = rand["verificat"].split(".")[:2]
        dv = datetime.date(azi.year, int(luna), int(zi))
        iso = dv.isoformat()
        relpaths = ["core/" + f for f in rand["fisiere"]]
        oc = subprocess.run(["git", "-C", str(_RAD), "log", "--until=%s 23:59:59" % iso, "-1",
                             "--format=%H", "--"] + relpaths, capture_output=True, text=True).stdout.strip()
        if not oc:
            continue
        inter = subprocess.run(["git", "-C", str(_RAD), "log", "%s..HEAD" % oc, "--format=%H",
                                "--"] + relpaths, capture_output=True, text=True).stdout.split()
        for fn in rand["functie"]:
            a_sqrt = _ast_multi(relpaths, oc, fn)
            a_head = _ast_multi(relpaths, "HEAD", fn)
            if a_sqrt != a_head:
                continue  # capete diferite -> deja prins de garda, nu e ascuns
            for c in inter:
                if _ast_multi(relpaths, c, fn) != a_sqrt:
                    out.append((rand["cluster"], rand["modul"], fn, iso, c[:9], a_sqrt == "<ABSENT>"))
                    break
    return out


def main():
    d = drift_dus_intors()
    print("=== DRIFT DUS-INTORS (capete egale, mijloc diferit) — ascuns de comparatia pe capete ===")
    for c, m, fn, dv, commit, absent in d:
        print("  [%s|%s] %s (√ %s): %s la commit %s"
              % (c, m, fn, dv, "STERS+READUS" if absent else "MODIFICAT+READUS", commit))
    print("  (niciun drift dus-intors)" if not d else "  TOTAL: %d — reverifica la sursa bifele de mai sus" % len(d))
    return 1 if d else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
