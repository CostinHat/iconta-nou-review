# -*- coding: utf-8 -*-
"""Contul de cabinet al probelor din browser — citit din `~/.iconta/fe_test.env` (600, în afara git).

[comanda Costin 05.10.2026] Parola stătea în `f1_helper.py`, într-un depozit cu oglindă publică. Acum nicio credențială
de probă nu stă în cod: fișierul de mediu e singura sursă, iar lipsa lui (sau a unei chei) e refuz numit — nu o valoare
implicită, care ar repune parola în git la prima „reparație rapidă”. Gard: `core/test_fara_secrete_in_git.py`.
"""
import os

CALE = os.path.expanduser("~/.iconta/fe_test.env")
CHEI = ("FE_TEST_EMAIL", "FE_TEST_PAROLA", "FE_TEST_BAZA")


def citeste(cale=CALE):
    """{FE_TEST_EMAIL, FE_TEST_PAROLA, FE_TEST_BAZA} din fișierul de mediu; SystemExit cu motivul dacă lipsește ceva."""
    if not os.path.isfile(cale):
        raise SystemExit("contul de probă lipsește: %s nu există (FE_TEST_EMAIL / FE_TEST_PAROLA / FE_TEST_BAZA)" % cale)
    cfg = {}
    for ln in open(cale, encoding="utf-8"):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            cfg[k.strip()] = v.strip()
    lipsa = [k for k in CHEI if not cfg.get(k)]
    if lipsa:
        raise SystemExit("contul de probă e incomplet în %s: lipsesc %s" % (cale, ", ".join(lipsa)))
    return cfg
