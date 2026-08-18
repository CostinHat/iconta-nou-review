# -*- coding: utf-8 -*-
"""[Regula 6 + Regula 14.4] GARD: intrarile ignorate la validarea CUI (strat firme) ajung VIZIBIL pe ecran.

Backend: /migrare/valideaza intoarce 'ignorate' (calculate cu separa_cui). Frontend: migrare.js le
consuma si le RANDEAZA intr-un banner vizibil (nu title-only, nu variabila nefolosita). Ratchet pe sursa
(fara browser) impotriva revenirii la drop tacut.
"""
import os
import pytest


def _f(p):
    if not os.path.exists(p):
        pytest.skip(p + " absent")
    return open(p, encoding="utf-8").read()


def test_ruta_intoarce_ignorate():
    s = _f("main.py")
    assert "separa_cui" in s, "ruta nu mai calculeaza intrarile ignorate"
    assert '"ignorate": ignorate' in s, "ruta /migrare/valideaza nu mai intoarce 'ignorate'"


def test_frontend_consuma_ignorate():
    s = _f("static/js/ecrane/migrare.js")
    assert "raspuns.ignorate" in s, "frontend nu mai citeste 'ignorate' din raspuns"


def test_frontend_randeaza_ignorate_vizibil():
    """Motivul e VIZIBIL in innerHTML (banner injectat), nu inghitit intr-o variabila nefolosita."""
    s = _f("static/js/ecrane/migrare.js")
    assert "bannerIgnorate" in s, "bannerul de ignorate a disparut"
    assert "${bannerIgnorate}" in s, "bannerul nu e injectat in innerHTML (invizibil)"
    assert "pasRezultate(corp, nav, rez, ignorate)" in s, "ignorate nu mai e pasat la randare"
