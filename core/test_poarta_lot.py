# -*- coding: utf-8 -*-
"""GARDA lansatorului porții de lot `scripts/poarta_lot.sh` (15.10.2026, comanda Costin, verbatim în DECIZII „Poarta o dată pe lot”:
„Poarta completă: o singură dată pe lot, la închiderea lotului, înainte de publicarea pe producție. [...] main acceptă un commit doar
dacă jurnalul porții îl arată verde. [...] Maximum două rulări complete pe lot; dacă a doua pică, te oprești și raportezi.”).

Pe un depozit TEMPORAR, cu lansatorul adevărat și o `poarta-suita` de probă (iese cu codul din `PROBA_RC`; adevărata ar rula ~70 de
minute): verdictul se scrie în `<git-common-dir>/poarta_verdicte.log` (`VERDE|ROSU <sha> <ramura> <data>`), iar lansatorul REFUZĂ —
fără să pornească poarta — pe `main`, pe arbore murdar, pe un SHA deja VERDE și la a treia rulare pe aceeași ramură.
MUTAȚIILE: fiecare din cele patru refuzuri scos din `poarta_lot.sh` -> testul lui pică."""
import os
import shutil
import subprocess

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANSATOR = os.path.join(RAD, "scripts", "poarta_lot.sh")
PROBA = '#!/bin/sh\necho "[proba] poarta-suita"\nexit "${PROBA_RC:-0}"\n'


def _git(d, *a):
    r = subprocess.run(("git",) + a, cwd=d, capture_output=True, text=True,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                GIT_COMMITTER_EMAIL="t@t"))
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.fixture()
def depozit(tmp_path):
    d = tmp_path / "r"
    (d / "scripts" / "githooks").mkdir(parents=True)
    shutil.copy(LANSATOR, d / "scripts" / "poarta_lot.sh")
    (d / "scripts" / "githooks" / "poarta-suita").write_text(PROBA)
    _git(d, "init", "-q", "-b", "main")
    _git(d, "add", "scripts")
    _git(d, "commit", "-q", "-m", "baza")
    _git(d, "checkout", "-q", "-b", "lucru/lot9")
    return d


def _lanseaza(d, rc=0):
    r = subprocess.run(["sh", "scripts/poarta_lot.sh"], cwd=d, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, PROBA_RC=str(rc)))
    return r.returncode, r.stdout + r.stderr


def _verdicte(d):
    p = d / ".git" / "poarta_verdicte.log"
    return [x.split()[:3] for x in p.read_text().splitlines()] if p.exists() else []


def test_verde_scrie_verdictul_commitului(depozit):
    d = depozit
    sha = _git(d, "rev-parse", "HEAD")
    cod, iesire = _lanseaza(d, 0)
    assert (cod, iesire.count("[proba] poarta-suita")) == (0, 1), iesire
    assert _verdicte(d) == [["VERDE", sha, "lucru/lot9"]]


def test_acelasi_sha_verde_nu_se_mai_ruleaza(depozit):
    d = depozit
    assert _lanseaza(d, 0)[0] == 0
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0 and iesire.count("are deja poarta VERDE") == 1, iesire
    assert len(_verdicte(d)) == 1


def test_maximum_doua_rulari_pe_lot(depozit):
    """Prima roșie, reparație, a doua roșie -> a treia e refuzată fără să pornească (oprire și raport)."""
    d = depozit
    assert _lanseaza(d, 1)[0] == 1
    _git(d, "commit", "-q", "--allow-empty", "-m", "reparatia")
    assert _lanseaza(d, 1)[0] == 1
    _git(d, "commit", "-q", "--allow-empty", "-m", "a doua reparatie")
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0 and iesire.count("maximum doua pe lot") == 1, iesire
    assert [v[0] for v in _verdicte(d)] == ["ROSU", "ROSU"]


def test_arborele_murdar_e_refuzat(depozit):
    d = depozit
    (d / "nou.py").write_text("x = 1\n")
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0 and iesire.count("    ?? nou.py") == 1, iesire
    assert _verdicte(d) == []


def test_pe_main_e_refuzat(depozit):
    d = depozit
    _git(d, "checkout", "-q", "main")
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0, iesire
    assert _verdicte(d) == []
