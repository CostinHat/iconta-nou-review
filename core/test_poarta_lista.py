# -*- coding: utf-8 -*-
"""R11 (15.1-E4): modul „listează” al porții — plafonul de 20, „toate ecranele” la stil.css / navigator.js / api.js / cadru.js, zona neacoperită refuzată."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import poarta_selectie as P  # noqa: E402


def test_toate_ecranele_ia_plafonul_intreg():
    for f in P.TOATE_ECRANELE:
        r = P.lista([f])
        assert r["toate_ecranele"] is True
        assert len(r["lista"]) == P.PLAFON_LISTA, f
        assert r["neacoperite"] == [], f


def test_un_ecran_atinge_doar_fluxurile_lui_si_nu_depaseste_plafonul():
    r = P.lista(["static/js/ecrane/control.js"])
    assert r["toate_ecranele"] is False
    assert 0 < len(r["lista"]) <= P.PLAFON_LISTA


def test_zona_neacoperita_e_semnalata():
    r = P.lista(["static/js/ecrane/ecran_inexistent_in_harta.js"])
    assert r["neacoperite"] == ["static/js/ecrane/ecran_inexistent_in_harta.js"]


def test_fisier_din_afara_static_nu_cere_teste_de_browser():
    r = P.lista(["core/ceva.py"])
    assert not [f for f in r["lista"] if f.startswith("core/")]
