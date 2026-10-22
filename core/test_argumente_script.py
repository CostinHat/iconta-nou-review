# -*- coding: utf-8 -*-
"""GARD — scripturile de lucru citesc argumentele ÎNAINTE de orice efect (decizia Costin 12.10.2026, verbatim în DECIZII: „--help la
e2e_poarta.py: repară-l în acest lot.”). Înainte: `e2e_poarta.py --help` pornea plasa întreagă (o plasă oprită la jumătate a lăsat firma
sintetică „E2E Probă …” în baza de test, iar `test_predare_cifre` a ieșit roșu); clasa, în aceleași scripturi: `publica_static.py --help`
publica staticul, `cifre_referinta.py -h` scria `-h.json` / `-h.md`. Mecanismul unic: `scripts/argumente_script.py`.

Rulat ca proces, cu limită de timp și cu mediul tăiat (E2E_TEMP / baza de neatins): dacă un script ar porni totuși lucrul, pică pe timp
sau pe cod, nu trece. LIMITĂ: privește scripturile de mai jos (lotul 11: și `ciorne_depasite.py`); un script nou cu argumente citite de mână intră în SCRIPTURI."""
import os
import re
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import argumente_script as a  # noqa: E402

SCRIPTURI = ("e2e_poarta.py", "publica_static.py", "cifre_referinta.py", "ciorne_depasite.py")


def _ruleaza(script, *argv):
    env = dict(os.environ, E2E_TEMP="/nonexistent/e2e_argumente", DATABASE_URL="postgresql://nimeni@127.0.0.1:1/nimic")
    return subprocess.run([sys.executable, os.path.join(RAD, "scripts", script), *argv], cwd="/tmp", capture_output=True, text=True,
                          timeout=30, env=env)


@pytest.mark.parametrize("script", SCRIPTURI)
@pytest.mark.parametrize("cerere", ["--help", "-h"])
def test_uzul_se_tipareste_si_nimic_nu_porneste(script, cerere):
    """MUTAȚIE: ramura uzului scoasă din `argumente_script.citeste` -> `--help` devine argument necunoscut (cod 2) -> pică; apelul
    `citeste` scos dintr-un script -> scriptul pornește lucrul -> pică."""
    r = _ruleaza(script, cerere)
    assert r.returncode == 0 and "Uz:" in r.stdout, (script, r.returncode, r.stdout[-300:], r.stderr[-300:])
    assert not os.path.exists("/tmp/-h.json") and "[e2e] aplicația" not in r.stdout + r.stderr


@pytest.mark.parametrize("script", SCRIPTURI)
def test_argumentul_necunoscut_e_refuzat_inainte_de_lucru(script):
    """MUTAȚIE: refuzul flagurilor necunoscute scos -> scriptul pornește -> pică."""
    r = _ruleaza(script, "--ajutor")
    # primul rând al refuzului: „[<script>] argument necunoscut: --ajutor — nimic nu pornește.” (rândul întreg, nu fragmente)
    prim = (r.stderr.splitlines() or [""])[0]
    assert r.returncode == 2 and re.fullmatch(r"\[[^\]]+\] argument necunoscut: --ajutor — nimic nu pornește\.", prim), \
        (script, r.returncode, r.stderr[-300:])


def test_formele_folosite_raman_valide():
    """Formele din poartă și din hook-uri trec: `e2e_poarta.py <dir>` / `--arbore --doar= --mutatie=`, `publica_static.py` (fără
    argumente) / `--din-arbore` / `--stare`, `cifre_referinta.py --productie --verifica` / `--productie <iesire>`."""
    e2e = dict(flaguri=("--arbore",), cu_valoare=("--doar=", "--mutatie="), pozitionale=1)
    assert a.motiv(["/tmp/e2e_poarta_capturi"], **e2e) is None
    assert a.motiv(["--arbore", "--doar=e2e_x.py", "--mutatie=m.json", "out"], **e2e) is None
    assert a.motiv(["--doar="], **e2e) == "argument fără valoare: --doar="
    assert a.motiv(["x", "y"], **e2e) == "cel mult 1 argument fără „--”"
    assert a.motiv([], flaguri=("--stare", "--din-arbore")) is None and a.motiv(["--din-arbore"], flaguri=("--stare", "--din-arbore")) is None
    cif = dict(flaguri=("--productie", "--verifica", "--scrie-referinta"), pozitionale=1)
    assert a.motiv(["--productie", "--verifica"], **cif) is None and a.motiv(["--productie", "/tmp/x"], **cif) is None
