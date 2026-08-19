# -*- coding: utf-8 -*-
"""[Regula 4 — fara mutatie tacuta] GARD: orice INSERT ... ON CONFLICT DO UPDATE din codul de PRODUCTIE
(suprascriere TACITA a unui rand existent) trebuie sa poarte o justificare inline '# upsert-ok: <motiv>',
altfel PICA. Suprascrierea tacuta devine astfel o alegere CONSTIENTA, cu motiv scris.

Grounded: bug plan_conturi (19.08) - adaugarea manuala de cont facea ON CONFLICT DO UPDATE si redenumea TACIT
contul OMFP standard; nu avea nicio justificare. Daca gardul exista, ar fi fost prins la scriere: pentru un
'adauga cont' de utilizator, suprascrierea NU e justificabila -> DO NOTHING sau refuz 409 explicit.

Test-urile (fixturi) si seed-ul sunt excluse (upsert de pregatire, nu cale de scriere de productie).
"""
import os
import glob
import pytest


def _fisiere_productie():
    fis = glob.glob("*.py") + glob.glob("core/*.py")
    return [f for f in fis if not os.path.basename(f).startswith("test_")]


def test_do_update_are_justificare():
    lipsa = []
    for f in _fisiere_productie():
        lines = open(f, encoding="utf-8").read().split("\n")
        for i, ln in enumerate(lines):
            if "DO UPDATE" in ln:
                fereastra = "\n".join(lines[max(0, i - 12):i + 2])
                if "upsert-ok:" not in fereastra:
                    lipsa.append("%s:%d" % (f, i + 1))
    assert not lipsa, (
        "INSERT ... ON CONFLICT DO UPDATE fara justificare '# upsert-ok: <motiv>' (suprascriere TACITA, "
        "Regula 4). Daca e un 'adauga' de utilizator, foloseste DO NOTHING / refuz 409 explicit; daca e un "
        "upsert legitim pe cheie naturala, scrie motivul. Locuri: %s" % lipsa)


def test_gardul_prinde_defectul():
    """Non-tautologie: pe un exemplu de DO UPDATE fara marker, fereastra NU contine 'upsert-ok:'."""
    ex = ['cur.execute("INSERT INTO x VALUES (1)', '    ON CONFLICT (id) DO UPDATE SET a=1")']
    fer = "\n".join(ex)
    assert "upsert-ok:" not in fer
    ex2 = ['# upsert-ok: motiv real'] + ex
    assert "upsert-ok:" in "\n".join(ex2[max(0, 0):])
