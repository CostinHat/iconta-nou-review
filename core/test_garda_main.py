# -*- coding: utf-8 -*-
"""Garda pe `main` (comanda Costin 14.10.2026, regim pilot, pct.2: „commit refuzat fără aprobare scrisă”, verbatim în DECIZII).

Pe un depozit TEMPORAR, cu hook-ul adevărat `scripts/githooks/reference-transaction` (copiat într-un director de hook-uri numai cu el):
mutarea lui `main` fără aprobare, cu aprobarea altui SHA sau spre ștergere e refuzată și nu mută nimic; cu aprobarea SHA-ului țintă
trece, iar aprobarea se consumă; ramurile de lucru nu sunt atinse. Plus oprirea rapidă din `pre-commit` (commit direct pe `main`).
[15.10.2026, comanda Costin, verbatim în DECIZII „Poarta o dată pe lot”: „main acceptă un commit doar dacă jurnalul porții îl arată
verde.”] Aprobarea singură nu ajunge: SHA-ul țintă cere `VERDE <sha>` în `<git-common-dir>/poarta_verdicte.log` (`scripts/poarta_lot.sh`).
MUTAȚIILE: hook-ul `exit 0` la început -> ROȘU; ramura `elif ! grep -q "^VERDE $NOU "` scoasă -> ROȘU."""
import os
import shutil
import subprocess

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(RAD, "scripts", "githooks", "reference-transaction")


def _git(d, *a, ok=True):
    r = subprocess.run(("git",) + a, cwd=d, capture_output=True, text=True,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                GIT_COMMITTER_EMAIL="t@t"))
    if ok:
        assert r.returncode == 0, r.stderr
    return r


@pytest.fixture()
def depozit(tmp_path):
    d = tmp_path / "r"
    d.mkdir()
    _git(d, "init", "-q", "-b", "main")
    _git(d, "commit", "-q", "--allow-empty", "-m", "baza")
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    shutil.copy(HOOK, hooks / "reference-transaction")
    os.chmod(hooks / "reference-transaction", 0o755)
    _git(d, "config", "core.hooksPath", str(hooks))
    _git(d, "checkout", "-q", "-b", "lucru")
    _git(d, "commit", "-q", "--allow-empty", "-m", "lot")
    sha = _git(d, "rev-parse", "HEAD").stdout.strip()
    _git(d, "checkout", "-q", "main")
    return d, sha


def _main(d):
    return _git(d, "rev-parse", "main").stdout.strip()


def test_fara_aprobare_main_nu_se_muta(depozit):
    d, sha = depozit
    inainte = _main(d)
    r = _git(d, "merge", "--ff-only", "-q", "lucru", ok=False)
    assert r.returncode != 0 and "[garda main] REFUZAT" in r.stderr, r.stderr
    assert _main(d) == inainte


def test_aprobarea_altui_sha_nu_ajunge(depozit):
    d, sha = depozit
    inainte = _main(d)
    (d / ".git" / "APROBARE_MAIN").write_text("sha: %s\naprobat: altceva\n" % ("0" * 39 + "1"))
    assert _git(d, "update-ref", "refs/heads/main", sha, ok=False).returncode != 0
    assert _main(d) == inainte


def _verdict(d, sha, v="VERDE"):
    with open(d / ".git" / "poarta_verdicte.log", "a", encoding="utf-8") as f:
        f.write("%s %s lucru 2026-10-15T20:00:00+03:00\n" % (v, sha))


def test_cu_aprobarea_sha_ului_trece_si_se_consuma(depozit):
    d, sha = depozit
    (d / ".git" / "APROBARE_MAIN").write_text("sha: %s\naprobat: Publică lotul (proba garzii)\n" % sha)
    _verdict(d, sha)
    _git(d, "merge", "--ff-only", "-q", "lucru")
    assert _main(d) == sha
    assert not (d / ".git" / "APROBARE_MAIN").exists() and (d / ".git" / ("APROBARE_MAIN.folosita-%s" % sha)).exists()
    _git(d, "checkout", "-q", "lucru")
    _git(d, "commit", "-q", "--allow-empty", "-m", "al doilea")
    al_doilea = _git(d, "rev-parse", "HEAD").stdout.strip()
    _verdict(d, al_doilea)
    assert _git(d, "update-ref", "refs/heads/main", al_doilea, ok=False).returncode != 0   # aprobarea s-a consumat
    assert _main(d) == sha


@pytest.mark.parametrize("verdict", [None, "ROSU", "VERDE-altul"])
def test_aprobarea_fara_poarta_verde_a_sha_ului_nu_ajunge(depozit, verdict):
    """Aprobarea scrisă e bună, dar SHA-ul n-are poarta VERDE (nicio rulare / o rulare roșie / verdele altui commit) -> refuzat,
    nimic nu se mută, aprobarea rămâne neconsumată."""
    d, sha = depozit
    inainte = _main(d)
    (d / ".git" / "APROBARE_MAIN").write_text("sha: %s\naprobat: Publică lotul (proba garzii)\n" % sha)
    if verdict == "ROSU":
        _verdict(d, sha, "ROSU")
    elif verdict == "VERDE-altul":
        _verdict(d, inainte)
    r = _git(d, "merge", "--ff-only", "-q", "lucru", ok=False)
    assert r.returncode != 0 and "fără poarta VERDE a lotului" in r.stderr, r.stderr
    assert _main(d) == inainte and (d / ".git" / "APROBARE_MAIN").exists()


def test_aprobarea_fara_text_nu_ajunge(depozit):
    d, sha = depozit
    (d / ".git" / "APROBARE_MAIN").write_text("sha: %s\n" % sha)
    assert _git(d, "update-ref", "refs/heads/main", sha, ok=False).returncode != 0


def test_stergerea_lui_main_e_refuzata_iar_ramurile_de_lucru_nu_sunt_atinse(depozit):
    d, sha = depozit
    _git(d, "checkout", "-q", "lucru")
    assert _git(d, "branch", "-D", "main", ok=False).returncode != 0
    _git(d, "commit", "-q", "--allow-empty", "-m", "pe ramura")              # o ramură de lucru se mută liber


def test_pre_commit_refuza_commitul_direct_pe_main(tmp_path):
    """Oprirea rapidă: textul din `pre-commit` vine înaintea porții (ruff, pytest)."""
    src = open(os.path.join(RAD, "scripts", "githooks", "pre-commit"), encoding="utf-8").read()
    i_garda = src.index('if [ "$(git symbolic-ref --short HEAD 2>/dev/null)" = "main" ]')
    i_ruff = src.index("RUFF=")
    assert i_garda < i_ruff
    d = tmp_path / "r"
    d.mkdir()
    _git(d, "init", "-q", "-b", "main")
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    with open(hooks / "pre-commit", "w", encoding="utf-8") as f:   # numai blocul gărzii, fără poarta din restul fișierului
        f.write("#!/bin/sh\n" + src[src.index('ROOT=$(git rev-parse'):src.index("PY=./venv/bin/python")])
    os.chmod(hooks / "pre-commit", 0o755)
    _git(d, "config", "core.hooksPath", str(hooks))
    r = _git(d, "commit", "-q", "--allow-empty", "-m", "direct", ok=False)
    assert r.returncode != 0 and "REFUZAT: commit direct pe main" in r.stdout + r.stderr
