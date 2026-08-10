# -*- coding: utf-8 -*-
"""Gard D205: campurile OBLIGATORII pe beneficiar (cifR, den1) nu pot fi emise vide.

Confruntare cu structura ANAF (anaf_surse/d205_struct_anaf.txt):
  - rand 34: cifR "4.CNP/NIF din Romania" N(13) DA -> "ERR - campul '4.CNP/NIF
    din Romania' necompletat".
  - rand 31: den1 "1.Nume si prenume / Denumire" C(100) DA -> "ERR - campul
    '1.Nume' beneficiar necompletat".

Defect probat pe validatorul OFICIAL DUK (10.08.2026, tenant_013 cu asociat fara CNP):
  DUK -> erori: "E: benef (1)  eroare atribut: cifR: atribut prezent dar vid nepermis".
Generatorul, pentru un asociat cu cota>0 si dividende dar FARA CNP (asociati.cnp NULL),
emitea tacut cifR="" -> declaratie respinsa de ANAF, nu refuzata la generare.

Fix: build_xml refuza (ValueError) cand un beneficiar cu valori are cifR/den1 vid,
in loc sa emita un XML invalid.
"""
import pytest
from core.d205 import calcul_d205, build_xml


def _prof():
    return {"cui": "14399840", "nume": "TEST SRL", "adresa": "X"}


def test_cifR_gol_refuzat_nu_emis_invalid():
    """HEAD (pre-fix): build_xml emite cifR='' (DUK respinge) -> test PICA.
    Post-fix: build_xml ridica ValueError care numeste beneficiarul."""
    res = calcul_d205(_prof(), 2026, [
        {"categ": "1.a", "nume": "POPESCU ION", "cif": "",
         "baza": 10000, "imp": 1600, "castig": 10000}])
    assert len(res.beneficiari) == 1, "beneficiarul (baza>0) e pastrat"
    with pytest.raises(ValueError):
        build_xml(res)


def test_den1_gol_refuzat():
    """den1 obligatoriu (C(100) DA): nume vid -> refuz, nu emitere vida."""
    res = calcul_d205(_prof(), 2026, [
        {"categ": "1.a", "nume": "   ", "cif": "1850101450013",
         "baza": 10000, "imp": 1600, "castig": 10000}])
    assert len(res.beneficiari) == 1
    with pytest.raises(ValueError):
        build_xml(res)


def test_beneficiar_valid_nu_e_afectat():
    """Regresie: un beneficiar cu cifR/den1 valide nu e blocat."""
    res = calcul_d205(_prof(), 2026, [
        {"categ": "1.a", "nume": "POPESCU ION", "cif": "1850101450013",
         "baza": 10000, "imp": 1600, "castig": 10000}])
    xml = build_xml(res)
    assert 'cifR="1850101450013"' in xml
    assert 'den1="POPESCU ION"' in xml
