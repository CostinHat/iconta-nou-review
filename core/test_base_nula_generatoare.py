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
    (d112, "cui"), (d390, "cui"), (d394, "cui"), (d406, "cui")],
    ids=["d112", "d390", "d394", "d406"])
def test_poarta_minima_cui_nume_trece(mod, kcui):
    """Cele 4 au poarta minima cui+nume; un profil cu ambele trece. (bilant cere si reg_com - test separat.)"""
    assert not mod.erori_generare({kcui: "14399840", "nume": "PROBA SRL"}), (
        "%s: profil cu cui+nume respins gresit" % mod.__name__)


def test_bilant_poarta_cere_si_reg_com():
    """Bilant (S1005/S1003) cere reg_com PESTE cui+nume: regCom e obligatoriu in XSD, verificat la sursa
    (DUKIntegrator -v S1005: 'regCom: atributul trebuie sa existe', reguli 2026.1). cui+nume singur e respins
    pe reg_com; cu +reg_com trece. Refuzul end-to-end e in core/test_bilant_regcom_poarta.py."""
    assert bilant_api.erori_generare({"cui_numeric": "14399840", "nume": "PROBA SRL"}), (
        "bilant: profil fara reg_com ar trebui respins (regCom obligatoriu S1005/S1003)")
    assert not bilant_api.erori_generare(
        {"cui_numeric": "14399840", "nume": "PROBA SRL", "reg_com": "J40/1234/2020"}), (
        "bilant: profil cu cui+nume+reg_com respins gresit")
