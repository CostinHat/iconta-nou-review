# -*- coding: utf-8 -*-
"""Garda anti-stale a agendei: pica daca TESTE.md a ramas in urma codului. Diferenta fata de DE_FACUT.md
(care a murit necitit): agenda e scrisa de mana DAR pazita mecanic - docul in urma codului pica suita."""
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
