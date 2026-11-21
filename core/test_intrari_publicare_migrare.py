"""Probe la intrările existente. Doar Git temporar și dubluri locale. Fără DB, rețea sau servicii."""
from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import sys

import unittest

import pytest
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch


def radacina():
    if os.environ.get("ICONTA_SURSE_PROBA"):
        return Path(os.environ["ICONTA_SURSE_PROBA"]).resolve(strict=True)
    return Path(__file__).resolve().parents[1]


def git(cwd,*args):
    return subprocess.check_output(["git","-C",str(cwd),"-c","core.hooksPath=/dev/null",*args],text=True).strip()


def test_rulatorul_public_refuza_inainte_de_acces_db(tmp_path,stack):
    path=radacina()/"core/migrari_registru.py"
    spec=importlib.util.spec_from_file_location("migrari_in_proba",path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    git(tmp_path,"init","-q","-b","main")
    git(tmp_path,"config","user.name","Proba"); git(tmp_path,"config","user.email","proba@example.invalid")
    git(tmp_path,"commit","-q","--allow-empty","-m","baza")
    sha=git(tmp_path,"rev-parse","HEAD")
    git(tmp_path,"update-ref","refs/remotes/origin/main",sha)
    log=tmp_path/".git/publica_verdicte.log"
    log.write_text(f"PASS {sha} 17.5-N4 proba C={sha} fisiere=-\n")
    stack.enter_context(patch.object(mod,"RAD",str(tmp_path))); stack.enter_context(patch.object(mod,"PASS_LOG",str(log)))
    vechi=os.getcwd(); stack.callback(os.chdir,vechi); os.chdir(tmp_path)
    def acces_nepermis(*args,**kwargs):
        raise AssertionError("A ajuns la mediul bazei inainte sa verifice versiunea migrarii")
    for name in ("_env_productie","_cu_registrul","_conexiune_productie"):
        stack.enter_context(patch.object(mod,name,acces_nepermis))
    # Cerere sintetica fara fisier autorizat in acest commit. Nu cream sau executam o migrare.
    try:
        rc=mod.main(["ruleaza","--productie","core/migrare_exemplu.py"])
    except SystemExit as exc:
        rc=exc.code
    assert rc not in (0,None)


def test_publica_lot_separa_asteptarea_de_esec(tmp_path,rc,asteptare):
    # Prima intrare prin scriptul oficial. Inlocuim numai dependentele externe ale shell-ului.
    src=radacina()
    principal=tmp_path/"repo"; principal.mkdir()
    git(principal,"init","-q","-b","main")
    git(principal,"config","user.name","Proba"); git(principal,"config","user.email","proba@example.invalid")
    scripts=principal/"scripts"; (scripts/"githooks").mkdir(parents=True)
    shutil.copy2(src/"scripts/publica_lot.sh",scripts/"publica_lot.sh")
    if (src/"scripts/reguli_publicare_migrare.py").exists():
        shutil.copy2(src/"scripts/reguli_publicare_migrare.py",scripts)
    if (src/"scripts/canal_migrare.py").is_file():
        shutil.copy2(src/"scripts/canal_migrare.py",scripts)
    journal=tmp_path/"evenimente"; journal.touch()
    (scripts/"jurnal_lot.py").write_text("import os,sys\nwith open(os.environ['EV'],'a') as f: print(' '.join(sys.argv[1:]),file=f)\nprint('17.5-P' if sys.argv[1]=='lot-curent' else '1234-1000')\n")
    (scripts/"publica_lot.py").write_text("import os,subprocess\ne=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()\nc=subprocess.check_output(['git','rev-parse','HEAD^'],text=True).strip()\ng=subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],text=True).strip()\nwith open(g+'/publica_verdicte.log','a') as f: print('PASS',e,'17.5-P','test','C='+c,'fisiere=-',file=f)\nprint('PASS',e)\n")
    (scripts/"githooks/post-commit").write_text("""set -eu
git push -q origin HEAD:refs/heads/main
git update-ref refs/remotes/origin/main HEAD
if [ "$#" -eq 3 ]; then
    bk=refs/heads/backup/lant-2026-11-21
    python3 scripts/canal_migrare.py retine-ref "$2" "$3" "$bk"
    git push -q origin "HEAD:$bk"
    python3 scripts/canal_migrare.py confirma-ref "$2" "$3" >/dev/null
fi
""")
    (scripts/"publica_prod.sh").write_text('echo CHEMAT_RESTART >> "$EV"\nexit '+str(rc)+'\n')
    (scripts/"incheie_lot.sh").write_text('echo "TERMINAL $*" >> "$EV"\n')
    git(principal,"add","."); git(principal,"commit","-qm","baza")
    origin=tmp_path/"origin.git"
    subprocess.run(["git","init","--bare","-q",str(origin)],check=True)
    git(principal,"remote","add","origin",str(origin))
    git(principal,"push","-q","origin","main")
    wt=tmp_path/"lot"; git(principal,"worktree","add","-qb","lucru/lot17-5p",str(wt))
    git(wt,"commit","-q","--allow-empty","-m","C")
    git(wt,"commit","-q","--allow-empty","-m","E"); e=git(wt,"rev-parse","HEAD")
    # Dublura publica_prod trebuie sa produca signalul semantic complet, daca E il cere.
    # Contract de schimb: returul rezervat 75 si recipisa oficiala descrisa in specificatie.
    import json
    import hashlib
    path="core/migrare_exemplu.py"
    if asteptare:
        (wt/"core").mkdir(); (wt/path).write_text("if __name__ == '__main__':\n    pass\n")
        declaratie=wt/"docs/dovezi/17_5_P/migrare_asteptata.json"
        declaratie.parent.mkdir(parents=True)
        declaratie.write_text(json.dumps(dict(lot="17.5-P",fisier=path,digest=hashlib.sha256((wt/path).read_bytes()).hexdigest(),
                                              tabel="bonuri",coloana="cui_cumparator")))
        git(wt,"add",path,str(declaratie.relative_to(wt))); git(wt,"commit","-qm","cod")
        c=git(wt,"rev-parse","HEAD"); git(wt,"commit","-q","--allow-empty","-m","dovezi"); e=git(wt,"rev-parse","HEAD")
        data=dict(lot="17.5-P",c=c,e=e,baza=git(principal,"rev-parse","main"),fisier=path,
                  digest=hashlib.sha256((wt/path).read_bytes()).hexdigest(),tabel="bonuri",coloana="cui_cumparator")
        (principal/".git"/"migrare_asteptata.json").write_text(json.dumps(data))
    home=tmp_path/"home"; home.mkdir()
    env=dict(os.environ, HOME=str(home),EV=str(journal),GIT_CONFIG_NOSYSTEM="1",GIT_CONFIG_GLOBAL="/dev/null",PYTHONPATH=str(wt))
    run=subprocess.run(["sh","scripts/publica_lot.sh"],cwd=wt,env=env,capture_output=True,text=True,timeout=15)
    rows=journal.read_text().splitlines()
    assert "CHEMAT_RESTART" in rows
    if asteptare:
        assert run.returncode==75, (run.stdout,run.stderr,rows)
        assert not any("TERMINAL " in row or row.endswith(" esec_restart") or row.endswith(" publicat") for row in rows)
        assert any("asteapta_migrare" in row for row in rows)
    else:
        assert run.returncode not in (0,75)
        assert any("TERMINAL 17.5-P nepublicat" in row for row in rows)
        assert any("esec_restart" in row for row in rows)


@pytest.fixture
def stack():
    with ExitStack() as s:
        yield s


# [17.5-P0] Aceleași cazuri ca înregistrarea dinamică din exemplarul livrat (ascunsă contorului static al porții), ca parametri pytest.
test_publica_lot_separa_asteptarea_de_esec = pytest.mark.parametrize("rc,asteptare", [(75, True), (1, False)])(
    test_publica_lot_separa_asteptarea_de_esec)

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
