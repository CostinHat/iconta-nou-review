# -*- coding: utf-8 -*-
"""Garda pe `main`: `refs/heads/main` (versiunea publicată) se mută numai la un SHA cu poarta VERDE a lotului.

ISTORIC. 14.10.2026 (comanda Costin, regim pilot, pct.2: „commit refuzat fără aprobare scrisă”): aprobarea scrisă `APROBARE_MAIN`,
consumată la reușită. 15.10.2026 (DECIZII „Poarta o dată pe lot”: „main acceptă un commit doar dacă jurnalul porții îl arată verde.”):
și `VERDE <sha>` în `<git-common-dir>/poarta_verdicte.log`. 23.10.2026 (CLAUDE.md §6: „După poarta verde, Code publică imediat, fără
să aștepte confirmare”; DECIZII 23.10.2026 „Comanda 12.1”): aprobarea scrisă RADIATĂ — verdictul VERDE (complet sau `compus:<X>`,
CLAUDE.md §5) e singura condiție; `APROBARE_MAIN` nu mai e citit, nici consumat.

Pe un depozit TEMPORAR, cu hook-ul adevărat `scripts/githooks/reference-transaction` (copiat într-un director de hook-uri numai cu el):
fără verdict VERDE pentru SHA-ul țintă (niciunul / ROȘU / VERDE-le altui commit) mutarea e refuzată și nu mută nimic, oricare ar fi o
aprobare scrisă rămasă pe disc; cu VERDE (complet sau compus) trece fără aprobare; ștergerea e refuzată; ramurile de lucru nu sunt
atinse. Plus oprirea rapidă din `pre-commit` (commit direct pe `main`).
MUTAȚIILE: hook-ul `exit 0` la început -> ROȘU; ramura `elif ! grep -q "^VERDE $NOU "` scoasă -> ROȘU; refuzul ștergerii scos -> ROȘU;
aprobarea scrisă cerută înapoi (`elif ! grep -q "^sha: $NOU" "$COMUN/APROBARE_MAIN"; then … COD=1`) -> ROȘU."""
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


def _verdict(d, sha, v="VERDE", sufix=""):
    with open(d / ".git" / "poarta_verdicte.log", "a", encoding="utf-8") as f:
        f.write("%s %s lucru 2026-10-15T20:00:00+03:00%s\n" % (v, sha, sufix))


def test_fara_aprobare_main_nu_se_muta(depozit):
    """„Aprobarea” lui `main` e, din 23.10.2026, verdictul VERDE: fără el (jurnalul porții lipsește) -> refuzat, nimic nu se mută."""
    d, sha = depozit
    inainte = _main(d)
    r = _git(d, "merge", "--ff-only", "-q", "lucru", ok=False)
    assert r.returncode != 0 and "[garda main] REFUZAT" in r.stderr and "fără poarta VERDE a lotului" in r.stderr, r.stderr
    assert _main(d) == inainte


def test_aprobarea_altui_sha_nu_ajunge(depozit):
    """VERDE-le ALTUI commit (aici, al bazei) nu mută `main` pe SHA-ul lotului."""
    d, sha = depozit
    inainte = _main(d)
    _verdict(d, inainte)
    assert _git(d, "update-ref", "refs/heads/main", sha, ok=False).returncode != 0
    assert _main(d) == inainte


@pytest.mark.parametrize("sufix", ["", " compus:%s" % ("a" * 40)])
def test_cu_poarta_verde_main_se_muta_fara_aprobare_scrisa(depozit, sufix):
    """[23.10.2026, CLAUDE.md §6] VERDE pentru SHA-ul țintă — al rulării complete sau compus (`… compus:<X>`) — ajunge: `main` se
    mută fără niciun `APROBARE_MAIN`; un `APROBARE_MAIN` rămas pe disc (al altui SHA) nu e citit și nu e mutat. Al doilea commit, fără
    verdictul lui, e refuzat: verdictul e al unui SHA, nu al ramurii. MUTAȚIE: aprobarea scrisă cerută înapoi în hook -> pică."""
    d, sha = depozit
    vechi = d / ".git" / "APROBARE_MAIN"
    vechi.write_text("sha: %s\naprobat: aprobare rămasă de dinainte de 23.10\n" % ("0" * 39 + "1"))
    _verdict(d, sha, sufix=sufix)
    _git(d, "merge", "--ff-only", "-q", "lucru")
    assert _main(d) == sha
    assert vechi.read_text().startswith("sha: " + "0" * 39 + "1") and not list((d / ".git").glob("APROBARE_MAIN.folosita-*"))
    _git(d, "checkout", "-q", "lucru")
    _git(d, "commit", "-q", "--allow-empty", "-m", "al doilea")
    al_doilea = _git(d, "rev-parse", "HEAD").stdout.strip()
    assert _git(d, "update-ref", "refs/heads/main", al_doilea, ok=False).returncode != 0
    assert _main(d) == sha


@pytest.mark.parametrize("verdict", [None, "ROSU", "ROSU-compus", "VERDE-altul"])
def test_aprobarea_fara_poarta_verde_a_sha_ului_nu_ajunge(depozit, verdict):
    """O aprobare scrisă pentru SHA-ul țintă (forma de dinainte de 23.10), dar fără poarta VERDE a lui (nicio rulare / o rulare roșie,
    completă sau compusă / verdele altui commit) -> refuzat, nimic nu se mută, fișierul nu e atins."""
    d, sha = depozit
    inainte = _main(d)
    apr = "sha: %s\naprobat: Publică lotul (proba garzii)\n" % sha
    (d / ".git" / "APROBARE_MAIN").write_text(apr)
    if verdict == "ROSU":
        _verdict(d, sha, "ROSU")
    elif verdict == "ROSU-compus":
        _verdict(d, sha, "ROSU", " compus:%s" % inainte)
    elif verdict == "VERDE-altul":
        _verdict(d, inainte)
    r = _git(d, "merge", "--ff-only", "-q", "lucru", ok=False)
    assert r.returncode != 0 and "fără poarta VERDE a lotului" in r.stderr, r.stderr
    assert _main(d) == inainte and (d / ".git" / "APROBARE_MAIN").read_text() == apr


def test_stergerea_lui_main_e_refuzata_iar_ramurile_de_lucru_nu_sunt_atinse(depozit):
    """Ștergerea lui `main` e refuzată și cu un VERDE în jurnal (al SHA-ului lui `main`); o ramură de lucru se mută liber.
    MUTAȚIE: ramura `if [ "$NOU" = "$ZERO" ]` scoasă -> ștergerea trece -> pică."""
    d, sha = depozit
    inainte = _main(d)
    _verdict(d, inainte)
    _verdict(d, "0" * 40)
    _git(d, "checkout", "-q", "lucru")
    r = _git(d, "branch", "-D", "main", ok=False)
    assert r.returncode != 0 and "REFUZAT: ștergerea lui refs/heads/main" in r.stderr, r.stderr
    assert _main(d) == inainte
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
