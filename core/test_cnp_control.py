# -*- coding: utf-8 -*-
"""GARD DEFECT-2 (07.08.2026): CNP la orice cale de intrare DIRECTA valideaza cifra de control,
nu doar formatul. Reutilizeaza valideaza_cnp (cheia 279146358279), la fel ca import + cnp_ingrijit.

Instanta: un CNP cu 13 cifre dar cifra de control gresita era acceptat tacut pe adaugarea/editarea
directa a salariatului si ajungea in D112 -> respins de DUK (cnpAsig invalid). Vezi E1E12_GASITE DEFECT-2.
"""
import re
import pytest
from core.salariati_api import valideaza_salariat, creeaza_salariat, actualizeaza_salariat
from core.salariati_import_api import valideaza_cnp

CNP_OK = "6010101123457"          # format + data + judet + control CORECTE
CNP_CTRL_GRESIT = "6010101123458"  # 13 cifre, format ok, dar CIFRA DE CONTROL gresita


def test_vectori_de_test_sunt_corecti():
    assert valideaza_cnp(CNP_OK) == (True, "ok")
    assert valideaza_cnp(CNP_CTRL_GRESIT)[0] is False
    assert valideaza_cnp(CNP_CTRL_GRESIT)[1] == "cifra de control"


def test_valideaza_salariat_refuza_control_gresit():
    er = valideaza_salariat({"nume": "X", "cnp": CNP_CTRL_GRESIT})
    assert any("CNP invalid" in e for e in er), er


def test_valideaza_salariat_accepta_control_corect():
    er = valideaza_salariat({"nume": "X", "cnp": CNP_OK})
    assert not any("CNP" in e for e in er), er


def test_creeaza_salariat_refuza_control_gresit_inainte_de_DB():
    # creeaza_salariat valideaza INAINTE de a atinge conn -> ridica ValueError cu conn=None
    with pytest.raises(ValueError) as ei:
        creeaza_salariat(None, nume="X", cnp=CNP_CTRL_GRESIT)
    assert "CNP invalid" in str(ei.value)


def test_actualizeaza_salariat_refuza_control_gresit_inainte_de_DB():
    with pytest.raises(ValueError) as ei:
        actualizeaza_salariat(None, 1, cnp=CNP_CTRL_GRESIT)
    assert "CNP invalid" in str(ei.value)


def test_toate_caile_CNP_refuza_control_gresit():
    """Harta clasei: fiecare validator de CNP (cale de intrare) refuza controlul gresit."""
    # (a) import salariati + (b) cnp_ingrijit folosesc acelasi valideaza_cnp
    assert valideaza_cnp(CNP_CTRL_GRESIT)[0] is False
    # (c) asociati import
    from core.asociati_import_api import verifica_randuri
    er = verifica_randuri([{"nume": "A", "cnp": CNP_CTRL_GRESIT, "cota": 100, "tip": "fizica"}])
    assert any(x.get("motiv") == "cnp_invalid" for x in er), er
    # (d) salariat direct (creare/editare) -> prin valideaza_salariat
    assert any("CNP invalid" in e for e in valideaza_salariat({"nume": "X", "cnp": CNP_CTRL_GRESIT}))


def test_nicio_cale_de_insert_CNP_fara_validare_de_control():
    """GARD anti-regresie / cale-noua: orice modul care INSERT-eaza o coloana CNP in DB trebuie sa
    refere valideaza_cnp. O cale noua de inserare fara validare de control PICA testul.
    (salariati_api valideaza prin valideaza_salariat->valideaza_cnp; asociati_import prin verifica.)"""
    import os, glob
    INSERT_CNP = re.compile(r"INSERT\s+INTO\s+(salariati|asociati|concedii_medicale)\b[^;]*\bcnp",
                            re.IGNORECASE | re.DOTALL)
    vinovati = []
    for cale in glob.glob("core/*.py"):
        base = os.path.basename(cale)
        if base.startswith("test_"):
            continue
        src = open(cale, encoding="utf-8").read()
        if INSERT_CNP.search(src) and "valideaza_cnp" not in src:
            vinovati.append(base)
    assert not vinovati, ("module care INSERT-eaza CNP fara a referi valideaza_cnp "
                          "(cale noua fara validare de control?): %s" % vinovati)


def test_valideaza_salariat_nu_regreseaza_la_format_only():
    """Blocare de regresie pe INSTANTA reparata: valideaza_salariat trebuie sa cheme valideaza_cnp,
    nu doar _CNP.match. Daca cineva revine la format-only, testul pica."""
    import inspect
    src = inspect.getsource(valideaza_salariat)
    assert "valideaza_cnp" in src, "valideaza_salariat nu mai foloseste valideaza_cnp (regresie la format-only!)"
