# -*- coding: utf-8 -*-
"""GARD — poarta rulează probele de prospețime ÎNAINTEA suitei (decizia Costin 15.10.2026, pct.1, verbatim în DECIZII „Lotul 3 — C35”:
„Plus gard mecanic: poarta rulează probele de prospețime (pytest -k proaspat) înainte de suită.”).

DE CE. Poarta lotului 3 (15.10.2026, 06:10) a fost respinsă după 50 de minute de două artefacte de probă din browser rămase pe UI-ul
vechi (`proba_pagina_principala.json`, `proba_decl50.json`, `ui_hash` 21b26b8f față de 46442d75). Hamul vizual nu le regenerează, iar
subsetul de dinaintea porții nu le cuprindea. Verdictul lor costă ~10 secunde.

CE FACE IMPOSIBIL:
  * ca un test care compară un artefact cu arborele (`ui_hash()` / `instrument_hash()`) să scape selecției `-k proaspat` — numele lui
    (sau al fișierului) trebuie să poarte „proaspat”;
  * ca pasul să dispară din poartă sau să ajungă după suită (structural);
  * ca un artefact vechi să mai pornească suita (funcțional, pe hook-ul adevărat, într-un depozit de probă: respins în secunde, fără
    „[poarta] pytest (suita”).
MUTAȚII: blocul scos din `poarta-suita` -> pică structural și funcțional; `test_scanul_e_proaspat_fata_de_ui` redenumit înapoi ->
pică primul test."""
import ast
import glob
import os
import shlex
import subprocess
import tempfile

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_POARTA = os.path.join(_RAD, "scripts", "githooks", "poarta-suita")
_HASHURI = {"ui_hash", "instrument_hash"}


def _compara_hash(fn):
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            nume = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if nume in _HASHURI:
                return True
    return False


def _teste_care_compara_un_hash():
    gasite = []
    for p in sorted(glob.glob(os.path.join(_RAD, "core", "test_*.py"))):
        arbore = ast.parse(open(p, encoding="utf-8").read(), filename=p)
        gasite += ["core/%s::%s" % (os.path.basename(p), fn.name) for fn in ast.walk(arbore)
                   if isinstance(fn, ast.FunctionDef) and fn.name.startswith("test") and _compara_hash(fn)]
    return gasite


def test_testele_de_prospetime_le_prinde_selectia_portii():
    """Selecția porții, așa cum o face pytest: nodurile colectate de `pytest --collect-only -k proaspat core/` cuprind fiecare test
    care compară un artefact cu arborele (fără parametri, numele nodului = numele funcției)."""
    compara = _teste_care_compara_un_hash()
    r = subprocess.run([os.path.join(_RAD, "venv", "bin", "python"), "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider",
                        "-k", "proaspat", "core/"], cwd=_RAD, capture_output=True, text=True, timeout=600)
    selectate = {l.split("[")[0] for l in r.stdout.splitlines() if l.startswith("core/")}
    scapate = sorted(set(compara) - selectate)
    assert scapate == [], ("test care compară un artefact cu arborele și pe care selecția porții (`pytest -k proaspat`, înaintea "
                           "suitei) nu-l prinde — pune „proaspat” în numele lui:\n  " + "\n  ".join(scapate))
    assert len(compara) >= 5, ("anti-vacuu: %d teste de prospețime găsite" % len(compara), compara)


def _cuvinte_cod():
    """Liniile de cod ale porții (fără comentarii), ca liste de cuvinte (`shlex`), cu indicele lor."""
    out = []
    for i, linie in enumerate(open(_POARTA, encoding="utf-8")):
        try:
            t = shlex.split(linie, comments=True)
        except ValueError:
            continue
        if t:
            out.append((i, t))
    return out


def test_poarta_ruleaza_prospetimea_inaintea_suitei_si_respinge():
    cod = _cuvinte_cod()
    pas = [i for i, t in cod if t[:7] == ["$PY", "-m", "pytest", "-q", "-k", "proaspat", "core/"]]
    suita = [i for i, t in cod if t[:5] == ["$PY", "-m", "pytest", "-q", "-n"]]
    assert (len(pas), len(suita)) == (1, 1), (pas, suita)
    assert pas[0] < suita[0], "probele de prospețime rulează după suită"
    intre = [t for i, t in cod if pas[0] < i < suita[0]]
    assert sum(1 for t in intre if t[:5] == ["if", "[", "$RC_PROASPAT", "-ne", "0"]) == 1, intre
    # [23.10.2026, CLAUDE.md §5 — DECIZII „Comanda 12.1”] poarta nu mai iese la prima parte roșie: partea roșie se consemnează (`rosu`)
    # și poarta rulează și restul, ca să se știe toate testele căzute; ieșirea nenulă o dă `incheie`, la final
    assert sum(1 for t in intre if t[:3] == ["rosu", "probe de prospetime", "$RC_PROASPAT"]) == 1, intre


def test_artefactul_vechi_e_respins_inainte_de_suita():
    """Pe hook-ul adevărat, într-un depozit de probă cu un singur test de prospețime roșu, cu jurnalele într-un director al lui:
    poarta iese roșie, iar PRIMA respingere consemnată e a probelor de prospețime (rulate înaintea suitei) și numește testul picat.
    [23.10.2026, CLAUDE.md §5] Suita rulează și ea după prospețimea roșie (poarta nu se mai oprește la prima parte roșie)."""
    with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as jurnale:
        subprocess.run(["git", "init", "-q", "."], cwd=d, check=True, capture_output=True)
        os.makedirs(os.path.join(d, "core"))
        os.symlink(os.path.join(_RAD, "venv"), os.path.join(d, "venv"))
        with open(os.path.join(d, ".gitignore"), "w") as f:
            f.write("venv\n.poarta_jurnal.log\n")
        with open(os.path.join(d, "core", "test_artefact.py"), "w") as f:
            f.write("def test_artefactul_e_proaspat():\n    assert 1 == 2\n")
        subprocess.run(["git", "add", "-A"], cwd=d, check=True, capture_output=True)
        r = subprocess.run(["sh", _POARTA], cwd=d, capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, POARTA_JURNALE=jurnale))
        assert r.returncode == 1, r.stdout + r.stderr
        # [15.10.2026] fără `precommit_curatenie.log`: ocolirea de curățenie a ieșit din poartă (DECIZII „Poarta o dată pe lot”)
        assert "precommit_proaspat.log" in os.listdir(jurnale), os.listdir(jurnale)
        blocuri = open(os.path.join(d, ".poarta_jurnal.log"), encoding="utf-8").read().split("=== ")[1:]
        assert blocuri and "RESPINS probe de prospetime exit 1" in blocuri[0].splitlines()[0], blocuri[:1]
        consemnate = [l.split()[1] for l in blocuri[0].splitlines() if l.startswith("    FAILED ")]
        assert consemnate == ["core/test_artefact.py::test_artefactul_e_proaspat"], consemnate
