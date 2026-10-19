# -*- coding: utf-8 -*-
"""GARD — funcțiunea contabilă a conturilor (A / P / A/P) vine din OMFP 1802/2014, nu din ghicit (deficiența 369, comanda Costin 8.2).

`core/plan_functiune.py` e GENERAT de `scripts/plan_functiune.py` din `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`; garda cere
ca fișierul din depozit să fie exact regenerarea (o editare de mână sau o sursă schimbată fără regenerare -> ROȘU).
"""
import subprocess
import sys
import os

from core.plan_functiune import ETICHETA, FUNCTIUNE, functiune

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_fisierul_e_regenerarea_din_omfp():
    """MUTAȚIA: „"1012": "P"” schimbat de mână în „"A/P"” -> ROȘU (`--verifica` iese 1)."""
    r = subprocess.run([sys.executable, os.path.join(RAD, "scripts", "plan_functiune.py"), "--verifica"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_functiunea_pe_conturile_din_deficienta():
    # OMFP 1802/2014 pct.594: „1012. Capital subscris vărsat (P)”
    assert functiune("1012") == "P"
    # OMFP 1802/2014 pct.594: „4111. Clienți (A)”
    assert functiune("4111") == "A"
    # OMFP 1802/2014 pct.594: „401. Furnizori (P)”
    assert functiune("401") == "P"
    # OMFP 1802/2014 pct.594: „117. Rezultatul reportat (A/P)”
    assert functiune("117") == "A/P"
    # OMFP 1802/2014 pct.593 alin.(2): cheltuielile sunt de activ, iar cifra terminală 9 (609) e de sens contrar
    assert functiune("601") == "A" and functiune("609") == "P"
    # OMFP 1802/2014 pct.593 alin.(2): veniturile sunt de pasiv; 709 de sens contrar
    assert functiune("704") == "P" and functiune("709") == "A"
    # analiticul moștenește de la sintetic; clasa 8 nu are funcțiune de bilanț (pct.593 alin.(3))
    assert functiune("401.00012") == "P" and functiune("4111.1") == "A"
    assert functiune("801") is None and functiune("999") is None


def test_eticheta_are_diacritice_si_acopera_toate_valorile():
    assert ETICHETA["A/P"] == "Bifuncțional"
    assert set(FUNCTIUNE.values()) <= set(ETICHETA)
    assert len(FUNCTIUNE) > 400, "anti-vacuu: %d conturi" % len(FUNCTIUNE)
