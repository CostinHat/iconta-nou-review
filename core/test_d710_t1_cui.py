# -*- coding: utf-8 -*-
"""GARD TURA 3 — D710 T1: checksum CUI al firmei validat PRE-DUK in erori_generare (sursa canonica
core.identitate.valideaza_cui). PE HEAD (8b74ccb) erori_generare verifica DOAR non-gol -> un CUI cu cifra
de control gresita / lungime / non-numeric era emis TACIT (il prindea doar DUK: 'cui: CUI invalid').
DUPA: erori_generare intoarce motivul exact. Gardul PICA pe HEAD (lista goala) si TRECE dupa fix."""
from core.d710 import erori_generare


def _prof(cui):
    return {"cui": cui, "nume": "TEST RECTIFICATIVA SRL", "adresa": "Str Test 1 Bucuresti"}


def test_cui_valid_nu_da_eroare():
    """CUI valid (acceptat de DUK) -> fara eroare de CUI."""
    er = erori_generare(_prof("456789123"))
    assert not any("CUI" in e and "invalid" in e for e in er), er


def test_cui_cifra_control_gresita_da_motiv():
    """D1/D2: CUI cu cifra de control gresita -> eroare cu motivul 'cifra de control'."""
    er = erori_generare(_prof("456789124"))
    assert any("invalid" in e and "456789124" in e for e in er), er
    assert any("cifra de control" in e for e in er), er


def test_cui_non_numeric_da_motiv():
    """I2: CUI non-numeric -> eroare (lipsa/lungime), nu emis tacit."""
    er = erori_generare(_prof("ABCDE"))
    assert any("CUI invalid" in e for e in er) or any("LIPS" in e for e in er), er


def test_cui_lungime_gresita_da_motiv():
    """CUI prea lung (peste 10 cifre) -> motiv 'lungime'."""
    er = erori_generare(_prof("12345678901234"))
    assert any("lungime" in e for e in er), er


def test_cui_lipsa_inca_semnalat():
    """Regresie: CUI gol raporteaza in continuare LIPSA (nu doar checksum)."""
    er = erori_generare(_prof(""))
    assert any("LIPS" in e and "CUI" in e for e in er), er
