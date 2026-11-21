"""Rulează pe copia livrată sau, după integrare, din core/ pe modulul oficial."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import subprocess
import sys

import unittest

import pytest
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch

if __package__:
    from scripts import reguli_publicare_migrare as r
else:
    if (Path(__file__).resolve().parent.parent / "scripts/reguli_publicare_migrare.py").is_file():
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import reguli_publicare_migrare as r

cale = "core/migrare_exemplu.py"
p = r.Plan("17.5-P", "a"*40, "b"*40, cale, "c"*64, "bonuri", "cui_cumparator")
lipsa = [(cale, p.digest)]
drift = dict(tabele_lipsa=[], tip_dif=[], nullable_dif=[], triggere_lipsa=[],
             coloane_lipsa={"bonuri": ["cui_cumparator"]})
backup = r.Backup(p.e, "iconta_v2", "iconta-backup.service", "id-operatie-test", True, 103, "f"*64)
aprobare = (p.lot,p.e,cale,p.digest)
rand = (cale,p.digest,"rulata",p.e)


def test_pentru_restart_normal():
    assert r.situatie(None, [], {}) == "pregatit"


def test_migrare_asteptata(d):
    assert r.situatie(p, lipsa, d) == "asteapta_migrare"


def test_drift_neacoperit(cheie):
    with unittest.TestCase().assertRaises(r.Refuz):
        r.situatie(p, lipsa, {"tenant_001": dict(drift, **{cheie: ["abatere"]})})


def test_migrare_nedeclarata_sau_necunoscuta(plan,lista,d):
    with unittest.TestCase().assertRaises(r.Refuz):
        r.situatie(plan,lista,d)


def test_acord_backup_si_confirmare():
    r.permite_ddl(p,aprobare,backup,100,104)
    assert r.confirma(p,rand,"pregatit",0,[p.e]*4,True,False) == "publicat"


def test_backup_invalid(schimb):
    with unittest.TestCase().assertRaises(r.Refuz):
        r.permite_ddl(p,aprobare,replace(backup,**schimb),100,104)


def test_acord_strain(index):
    a=list(aprobare); a[index]="alta valoare"
    with unittest.TestCase().assertRaises(r.Refuz):
        r.permite_ddl(p,tuple(a),backup,100,104)


def test_publicarea_refuzata(d):
    args=dict(rand_registru=rand,verificare="pregatit",restart_rc=0,brate=[p.e]*4,toate_procesele=True,sentinela=False)
    with unittest.TestCase().assertRaises(r.Refuz):
        r.confirma(p,**(args | d))


def _depozit(tmp_path):
    def git(*args):
        return subprocess.check_output(["git","-C",str(tmp_path),*args],text=True).strip()
    git("init","-q","-b","main"); git("config","user.name","Proba"); git("config","user.email","proba@example.invalid")
    git("-c","core.hooksPath=/dev/null","commit","-q","--allow-empty","-m","baza")
    baza=git("rev-parse","HEAD")
    src=tmp_path / cale; src.parent.mkdir(); src.write_text("# martor inert\n")
    git("add",cale); git("-c","core.hooksPath=/dev/null","commit","-qm","C")
    c=git("rev-parse","HEAD")
    git("-c","core.hooksPath=/dev/null","commit","-q","--allow-empty","-m","E")
    e=git("rev-parse","HEAD"); git("update-ref","refs/remotes/origin/main",e)
    pl=replace(p,c=c,e=e,digest=sha256(src.read_bytes()).hexdigest())
    log=tmp_path / ".git/publica_verdicte.log"
    log.write_text(f"PASS {e} {p.lot} 2026-11-21T09:00:00+02:00 C={c} fisiere=-\n")
    return git,tmp_path,pl,baza,log


def test_pass_pe_checkout_real(depozit):
    _,root,pl,baza,_=depozit
    assert r.verifica_git(root,pl,baza) is None


def test_identitate_git(depozit,defect):
    git,root,pl,baza,log=depozit
    if defect in ("lot","c","e"):
        token={"lot":pl.lot,"c":pl.c,"e":pl.e}[defect]
        log.write_text(log.read_text().replace(token,"x"*len(token)))
    if defect=="fara_pass": log.unlink()
    if defect=="origin": git("update-ref","refs/remotes/origin/main",baza)
    if defect=="ramura": git("switch","-qc","lucru/proba")
    if defect in ("fisier","index"):
        (root/cale).write_text("# alta versiune\n")
        if defect=="index": git("add",cale)
    if defect=="necunoscut": (root/"core/martor.py").write_text("# inert\n")
    if defect=="digest": pl=replace(pl,digest="f"*64)
    if defect=="baza": baza=pl.c
    with unittest.TestCase().assertRaises((r.Refuz,OSError,subprocess.CalledProcessError)):
        r.verifica_git(root,pl,baza)


@pytest.fixture
def depozit(tmp_path):
    return _depozit(tmp_path)


# [17.5-P0] Înregistrarea dinamică din exemplarul livrat (setattr pe clasa Probe) ascundea testele de contorul static al porții
# (scripts/poarta_lib.py::asertiuni), care le clasifica „test nou fără aserțiuni”. Aceleași cazuri, în aceeași ordine, ca parametri pytest.
PARAMETRI = {
    "test_migrare_asteptata": ("d", [{}, {"tenant_001": drift}]),
    "test_drift_neacoperit": ("cheie", ["tabele_lipsa","tip_dif","nullable_dif","triggere_lipsa","coloane_lipsa"]),
    "test_migrare_nedeclarata_sau_necunoscuta": ("plan,lista,d", [(None,lipsa,{}),(p,[],{"tenant_001":drift}),
        (p,[("alta.py",p.digest)],{}),(p,[(cale,"0"*64)],{}),(p,lipsa+lipsa,{}),
        (p,None,{}),(p,lipsa,None),(p,lipsa,{"public":drift})]),
    "test_backup_invalid": ("schimb", [dict(e=p.c),dict(baza="iconta_test"),dict(serviciu="alt"),
        dict(invocatie=""),dict(reusit=False),dict(incheiat_ns=99),dict(incheiat_ns=105),dict(digest="scurt")]),
    "test_acord_strain": ("index", list(range(4))),
    "test_publicarea_refuzata": ("d", [dict(rand_registru=None),dict(rand_registru=(cale,p.digest,"marcata",p.e)),
        dict(rand_registru=(cale,p.digest,"baza",p.e)),dict(rand_registru=(cale,"f"*64,"rulata",p.e)),
        dict(rand_registru=(cale,p.digest,"rulata",p.c)),dict(verificare="necunoscuta"),dict(restart_rc=1),
        dict(sentinela=True),dict(toate_procesele=False)]+[dict(brate=[p.c if i==k else p.e for i in range(4)]) for k in range(4)]),
    "test_identitate_git": ("defect", ["lot","c","e","fara_pass","origin","ramura","fisier","index","necunoscut","digest","baza"]),
}
for _nume, (_arg, _cazuri) in PARAMETRI.items():
    globals()[_nume] = pytest.mark.parametrize(_arg, _cazuri)(globals()[_nume])

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
