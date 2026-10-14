# -*- coding: utf-8 -*-
"""Suita nu moștenește variabilele GIT_* pe care git le dă hook-ului (15.10.2026, regim pilot: lucrul într-un worktree).

Într-un worktree, git exportă hook-ului `commit-msg` — din care rulează poarta — `GIT_DIR` și `GIT_INDEX_FILE` cu cale absolută.
Moștenite, un `git` rulat de un test într-un depozit temporar lucra pe indexul REAL al commitului (prima poartă a lotului 1: 6 teste
ale hook-ului de mesaj respinse de „38 fisiere NOI”, fișierele lotului). `conftest.py` le scoate înainte de colectare.
MUTAȚIA: bucla din `conftest.py` scoasă + suita rulată cu `GIT_DIR` / `GIT_INDEX_FILE` exportate -> ROȘU."""
import os
import subprocess
import tempfile

from conftest import VARIABILE_GIT_DE_HOOK


def test_mediul_suitei_nu_are_variabilele_git_ale_hookului():
    ramase = [v for v in VARIABILE_GIT_DE_HOOK if v in os.environ]
    assert ramase == [], ramase


def test_un_depozit_temporar_isi_vede_propriul_index():
    """Efectul, nu doar lista: în depozitul gol al unui test, `git diff --cached` e gol — nu indexul commitului care rulează poarta."""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", "."], cwd=d, check=True, capture_output=True)
        r = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=d, capture_output=True, text=True, check=True)
        assert r.stdout.splitlines() == []
