# -*- coding: utf-8 -*-
"""Poarta bazei nule (A, 31.07.2026): FIECARE generator de declaratie are erori_generare() si un
profil GOL o declanseaza. Patru declaratii depuse la ANAF (d112/d390/d394/d406) + bilant puteau
iesi cu profil incomplet -> XML respins/gresit fara semnal. Inventar pe CRITERIU COMPORTAMENTAL
(def genereaza(conn, schema)), nu pe nume dNNN - altfel bilant (S1003/S1005) era ratat (clasa E)."""
import pytest

from core import (d100, d101, d112, d205, d300, d301, d390, d394, d406, d710, bilant_api)

TOATE = [d100, d101, d112, d205, d300, d301, d390, d394, d406, d710, bilant_api]


@pytest.mark.parametrize("mod", TOATE, ids=lambda m: m.__name__)
def test_generatorul_are_poarta_baza_nula(mod):
    assert hasattr(mod, "erori_generare"), "%s NU are erori_generare (poarta bazei nule)" % mod.__name__
    assert mod.erori_generare({}), "%s: profil GOL nu e semnalat" % mod.__name__


@pytest.mark.parametrize("mod, kcui", [
    (d112, "cui"), (d390, "cui"), (d394, "cui"), (d406, "cui"), (bilant_api, "cui_numeric")],
    ids=["d112", "d390", "d394", "d406", "bilant"])
def test_poarta_minima_cui_nume_trece(mod, kcui):
    """Cele 5 nou-adaugate au poarta minima cui+nume; un profil cu ambele trece."""
    assert not mod.erori_generare({kcui: "14399840", "nume": "PROBA SRL"}), (
        "%s: profil cu cui+nume respins gresit" % mod.__name__)
