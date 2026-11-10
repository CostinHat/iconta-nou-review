# -*- coding: utf-8 -*-
"""scripts/teste_locuri_schimbate.py — testele care citesc locurile schimbate de un lot (17.5-U, U.6; cauza: 17.5-C, trei teste din plasă cereau luna de azi, iar lotul schimba luna afișată).
Nu rulează niciun test: citește `git diff <bază> <commit>` pe fișierele din static/ și pe cele din core/ care nu sunt teste (core/test_*.py), scoate locurile schimbate (funcții, id-uri de
elemente, chei, texte afișate între ghilimele, nume de fișiere; cel puțin 6 caractere; hash-urile «?v=<hex>» nu sunt locuri) și listează, pe nume de fișier, testele din core/test_*.py și
frontend_test/e2e/e2e_*.py (de pe <commit>) care conțin literal cel puțin un loc, cu locul care l-a prins. «în plasă» = fișierul e în scripts/plasa_16_2.manifest (le rulează poarta), «în afara
plasei» = restul. Separat: testele care citesc data de azi sau luna curentă fără ceasul înghețat din core/ceas_proba.py, când diff-ul atinge fișiere care afișează date sau luni.

Uz:
  teste_locuri_schimbate.py <bază> <commit> [--depozit=<director git>]
  Ieșire 0 cu lista și numărul fișierelor; 1 cu motivul când diff-ul e gol sau un commit lipsește."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argumente_script  # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN = 6
_HASH = re.compile(r"\?v=[0-9a-fA-F]+")
_TEXT = re.compile(r"""(["'`])((?:\\.|(?!\1).){%d,})\1""" % MIN)
_FUNCTII = re.compile(r"(?:\bfunction\s+|\bdef\s+|\b(?:const|let|var)\s+)([A-Za-z_$][\w$]{%d,})" % (MIN - 1))
_CHEI = re.compile(r"\b([A-Za-z_$][\w$]{%d,})\s*:" % (MIN - 1))
_IDURI = re.compile(r"""\bid\s*=\s*["']([^"']{%d,})["']|#([A-Za-z][\w-]{%d,})|getElementById\(["']([^"']{%d,})["']\)""" % (MIN, MIN - 1, MIN))
_FISIERE = re.compile(r"[\w./-]{2,}\.(?:js|css|html|py|json|csv)\b")
_DATE = re.compile(r"date\.today|datetime\.now|datetime\.datetime\.now|new Date|Date\.now|luna curent|luna_curent", re.I)
_AFISEAZA_DATE = re.compile(r"new Date|toLocale|\bluna\b|\bluni\b|month|strftime|\.date\b|data_|_data\b", re.I)


def _git(depozit, *a):
    r = subprocess.run(["git", *a], cwd=depozit, capture_output=True, text=True)
    return r.returncode, r.stdout


def _normal(linie):
    return _HASH.sub("?v=", linie).strip()


def locuri_din_linie(linie):
    """Locurile unei linii de cod (fără hash-urile «?v=»): șiruri între ghilimele, nume de funcții / variabile, chei, id-uri, nume de fișiere; cel puțin MIN caractere."""
    linie = _HASH.sub("", linie)
    gasite = [m.group(2) for m in _TEXT.finditer(linie)]
    gasite += _FUNCTII.findall(linie) + _CHEI.findall(linie) + _FISIERE.findall(linie)
    for m in _IDURI.finditer(linie):
        gasite.append(next(g for g in m.groups() if g))
    return [g.strip() for g in gasite if len(g.strip()) >= MIN]


def locuri_schimbate(diff):
    """Locurile din liniile schimbate (+/-) ale unui diff unificat; o pereche -/+ identică după normalizarea hash-ului «?v=» nu produce locuri. -> {loc: fișier}."""
    iesire, fisier, minus, plus = {}, None, [], []

    def inchide():
        n_plus = {_normal(x) for x in plus}
        n_minus = {_normal(x) for x in minus}
        for x in minus + plus:
            if _normal(x) in n_plus & n_minus:
                continue
            for loc in locuri_din_linie(x):
                iesire.setdefault(loc, fisier)
        minus.clear()
        plus.clear()

    for ln in diff.splitlines():
        if ln.startswith("diff --git"):
            inchide()
            fisier = ln.split(" b/", 1)[-1]
        elif ln.startswith(("+++", "---")):
            continue
        elif ln.startswith("@@"):
            inchide()
        elif ln.startswith("-"):
            minus.append(ln[1:])
        elif ln.startswith("+"):
            plus.append(ln[1:])
    inchide()
    return iesire


def _fisier_de_cod(c):
    return c.startswith("static/") or (c.startswith("core/") and not re.match(r"core/(.*/)?test_[^/]*\.py$", c))


def main(argv):
    a = argumente_script.citeste(argv, __doc__, cu_valoare=("--depozit=",), pozitionale=2, prefix="[teste_locuri_schimbate]")
    poz = [x for x in a if not x.startswith("-")]
    depozit = next((x.split("=", 1)[1] for x in a if x.startswith("--depozit=")), RAD)
    if len(poz) != 2:
        print("[teste_locuri_schimbate] trebuie <bază> și <commit>.\n" + __doc__[__doc__.index("Uz:"):], file=sys.stderr)
        return 2
    baza, commit = poz
    for c in (baza, commit):
        if _git(depozit, "rev-parse", "--verify", "--quiet", c + "^{commit}")[0]:
            print("[teste_locuri_schimbate] commit lipsă: %s" % c)
            return 1
    nume = [x for x in _git(depozit, "diff", "--name-only", "--no-renames", baza, commit)[1].splitlines() if _fisier_de_cod(x)]
    if not nume:
        print("[teste_locuri_schimbate] diff-ul %s..%s nu atinge fișiere din static/ sau din core/ (în afara testelor)." % (baza[:8], commit[:8]))
        return 1
    locuri = locuri_schimbate(_git(depozit, "diff", "--no-renames", "-U0", baza, commit, "--", *nume)[1])
    toate = _git(depozit, "ls-tree", "-r", "--name-only", commit)[1].splitlines()
    teste = [c for c in toate if re.fullmatch(r"core/test_[^/]*\.py|frontend_test/e2e/e2e_[^/]*\.py", c)]
    manifest = {ln.split("\t")[0] for ln in _git(depozit, "show", "%s:scripts/plasa_16_2.manifest" % commit)[1].splitlines() if ln.strip() and not ln.startswith("#")}
    afiseaza_date = any(_AFISEAZA_DATE.search(_git(depozit, "show", "%s:%s" % (commit, c))[1]) for c in nume if _git(depozit, "cat-file", "-e", "%s:%s" % (commit, c))[0] == 0)
    gasite, date_azi = [], []
    for t in teste:
        text = _git(depozit, "show", "%s:%s" % (commit, t))[1]
        prinse = [l for l in sorted(locuri, key=len, reverse=True) if l in text]
        if prinse:
            gasite.append((t, prinse[0], locuri[prinse[0]], len(prinse)))
        if afiseaza_date and _DATE.search(text) and "ceas_proba" not in text:
            date_azi.append(t)
    print("locuri schimbate: %d, în %d fișiere din static/ și core/ (%s..%s)" % (len(locuri), len(nume), baza[:8], commit[:8]))
    for t, loc, din, n in sorted(gasite, key=lambda g: (-g[3], g[0])):
        print("  %-60s %-15s %2d locuri, cel mai lung: %r (din %s)" % (t, "în plasă" if t in manifest else "în afara plasei", n, loc[:60], din))
    print("teste care citesc locurile schimbate: %d fișiere (în plasă: %d, în afara plasei: %d)" % (
        len(gasite), sum(1 for g in gasite if g[0] in manifest), sum(1 for g in gasite if g[0] not in manifest)))
    print("teste care citesc data de azi sau luna curentă fără ceasul înghețat din core/ceas_proba.py (diff-ul atinge fișiere care afișează date sau luni: %s): %d" % (
        "da" if afiseaza_date else "nu", len(date_azi)))
    for t in date_azi:
        print("  %-60s %s" % (t, "în plasă" if t in manifest else "în afara plasei"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
