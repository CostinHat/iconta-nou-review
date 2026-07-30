# -*- coding: utf-8 -*-
"""Garda anti-stale a agendei: pica daca TESTE.md a ramas in urma codului. Diferenta fata de DE_FACUT.md
(care a murit necitit): agenda e scrisa de mana DAR pazita mecanic - docul in urma codului pica suita."""
import os
import re
import subprocess
import datetime
import pathlib

from core import agenda

_RAD = pathlib.Path(__file__).resolve().parent.parent


def _git_at(cale):
    """Timestamp Unix al ultimului commit care a atins `cale` (NU mtime - se schimba la checkout)."""
    r = subprocess.run(["git", "-C", str(_RAD), "log", "-1", "--format=%at", "--", str(cale)],
                       capture_output=True, text=True)
    t = r.stdout.strip()
    return int(t) if t else None


def test_fiecare_modul_A_are_fisier_de_test():
    a = agenda.stare_sesiune_a()
    assert a is not None, "Inventarul sesiunii A lipseste din TESTE.md"
    lipsa = []
    for rand in a[2]:
        if not rand["fisiere"]:
            lipsa.append(rand["modul"] + " (niciun fisier numit)")
            continue
        for f in rand["fisiere"]:
            if not (_RAD / "core" / f).exists():
                lipsa.append("%s -> %s (inexistent)" % (rand["modul"], f))
    assert not lipsa, "module A fara fisier de test in repo (contopeste sau adauga fisierul): %s" % lipsa


def test_verificarile_A_nu_sunt_in_urma_codului():
    """Un modul marcat √ DD.MM e STALE daca fisierul lui a fost comis DUPA acea data -> reverifica."""
    a = agenda.stare_sesiune_a()
    assert a is not None
    azi = datetime.date.today()
    stale = []
    for rand in a[2]:
        if not rand["verificat"] or "." not in rand["verificat"]:
            continue
        zi, luna = rand["verificat"].split(".")[:2]
        data_verif = datetime.date(azi.year, int(luna), int(zi))
        for f in rand["fisiere"]:
            at = _git_at(_RAD / "core" / f)
            if at is None:
                continue
            data_fisier = datetime.datetime.fromtimestamp(at, datetime.timezone.utc).date()
            if data_fisier > data_verif:
                stale.append("%s: %s comis %s > verificat %s -> reverifica la sursa si actualizeaza randul in TESTE.md"
                             % (rand["modul"], f, data_fisier.isoformat(), data_verif.isoformat()))
    assert not stale, "AGENDA STALE (docul in urma codului):\n" + "\n".join(stale)


def test_fiecare_xfail_apare_in_raport():
    d = agenda.datorii_deschise()
    assert d, "nicio datorie xfail citita din test_datorie.py"
    rap = agenda.raport(tehnic=False)
    lipsa = [n for n, _ in d if n not in rap]
    assert not lipsa, "datorii care nu apar in raportul agendei: %s" % lipsa


def test_agenda_ruleaza_fara_eroare():
    rap = agenda.raport(tehnic=False)
    assert "AGENDA iConta" in rap and "URMATORUL PAS" in rap and "DESCHIS ACUM" in rap


def test_stare_tehnica_numara_toata_suita():
    """STARE TEHNICA trebuie sa numere suita de la RADACINA (core/ + radacina), nu un subset.
    Bug 30.07.2026: agenda rula `pytest core/` (colecta doar un subset), dar suita reala e cea
    de la radacina -> STARE TEHNICA afisa un numar mai mic decat realitatea. Compara SCOPE-ul
    colectat (--collect-only), nu ruleaza suita de doua ori. (Fara literal cu numar+passed in
    text, ca traceback-ul la esec sa nu otraveasca regexul din stare_tehnica.)"""
    py = str(_RAD / "venv" / "bin" / "python3")
    if not os.path.exists(py):
        py = "python3"

    def _colectate(scope):
        # UN singur -q: dublu -q schimba formatul --collect-only si dispare 'N tests collected'
        args = ["--collect-only", "-q"] + [x for x in scope if x != "-q"]
        r = subprocess.run([py, "-m", "pytest"] + args,
                           cwd=str(_RAD), capture_output=True, text=True, timeout=120)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        return int(m.group(1)) if m else None

    n_agenda = _colectate(agenda.PYTEST_ARGS)   # scope-ul REAL folosit de stare_tehnica
    n_radacina = _colectate([])                 # radacina, fara niciun filtru
    assert n_agenda is not None and n_radacina is not None, \
        "nu s-a putut parsa 'N tests collected' din pytest --collect-only"
    assert n_agenda == n_radacina, \
        "STARE TEHNICA numara %d, radacina are %d -> agenda ar afisa un numar fals" % (n_agenda, n_radacina)
