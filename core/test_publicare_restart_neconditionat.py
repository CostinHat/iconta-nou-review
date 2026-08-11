# -*- coding: utf-8 -*-
"""Gard: pasul de restart din ritualul de publicare (scripts/githooks/post-commit) e NECONDITIONAT de continut.

DE CE (11.08.2026): publicarea decidea singura daca restarteaza dupa TIPUL commitului -> un commit de DOCS a
lasat procesul viu pe commitul anterior => RUNNING != HEAD (divergenta prinsa: RUNNING b0ccc40 vs HEAD f504f00).
CLAUDE.md §2.3 pct.10 cere ca dupa ORICE publicare din lant procesul viu sa preia HEAD - fara exceptii, fara
liste de tipuri. Rescrierea PREDARE descria comportamentul, nu-l schimba; clasa ramanea deschisa. Acest gard
CADE daca:
  (a) dispare restartul lui iconta-nou din hook (procesul viu n-ar mai prelua HEAD), SAU
  (b) reapare orice inspectie a CONTINUTULUI commitului in hook (git diff / --name-only / extensii de fisier),
      adica orice mecanism care ar putea conditiona publicarea/restartul pe tipul a ceea ce s-a schimbat.
"""
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(_RAD, "scripts", "githooks", "post-commit")


def _text():
    with open(HOOK, encoding="utf-8") as f:
        return f.read()


def test_hook_publicare_exista():
    assert os.path.exists(HOOK), "scripts/githooks/post-commit lipseste (ritualul de publicare)"


def test_restartul_exista_si_tinteste_iconta_nou():
    t = _text()
    assert re.search(r"systemctl\s+restart\s+iconta-nou\b", t), (
        "post-commit nu restarteaza iconta-nou: procesul viu nu preia HEAD dupa publicare (§2.3 pct.10)")


def test_restartul_e_neconditionat_de_tipul_continutului():
    """Niciun tipar care ar INSPECTA ce s-a schimbat, ca sa decida publicarea/restartul. Se prind mecanismele
    reale de conditionare pe continut, NU simpla mentionare a unui nume de fisier intr-un comentariu:
      - liste de fisiere schimbate: git diff/show --name-only/--stat, diff-tree/diff-index;
      - comparatie cu commitul anterior: HEAD~ / HEAD^;
      - potrivire pe extensie: glob (*.py) sau regex ancorat (\\.py$).
    Reaparitia oricaruia = clasa veche revenita (restart pe tipul commitului)."""
    t = _text()
    INTERZIS = [
        r"--name-only", r"--stat",
        r"\bgit\s+diff\b", r"\bgit\s+show\b", r"diff-tree", r"diff-index",
        r"HEAD~", r"HEAD\^",
        r"\*\.[A-Za-z]",           # glob de extensie: *.py, *.md, *.csv
        r"\\\.[A-Za-z]{2,4}\$",    # regex de extensie ancorat: \.py$ , \.md$
    ]
    gasite = [p for p in INTERZIS if re.search(p, t)]
    assert not gasite, (
        "post-commit inspecteaza tipul continutului ca sa decida publicarea/restartul "
        "(conditionare interzisa pe tip de commit, §2.3 pct.10): %s" % gasite)
