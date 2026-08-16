# -*- coding: utf-8 -*-
"""Teste gardian pentru solduri_parteneri_api (partea PURA).

Modulul n-a avut niciun test. Bugurile de mai jos au fost gasite prin migrare reala
(pachet cu greseli intentionate, incarcat prin interfata): nu exista NICIO validare
intre extrage() si importa(), iar ecranul afisa avertismente si salva oricum.
"""
import pytest
from core.solduri_parteneri_api import (valideaza_cui, verifica_randuri, importa,
                                        _gaseste_col, CONTURI_PARTENERI)


# ---------- CUI ----------
def test_cui_real_e_valid():
    for c in ("14399840", "4221306", "RO14837428", "RO427320", "15193236"):
        assert valideaza_cui(c)[0], c


def test_cui_cu_cifra_de_control_gresita_e_respins():
    ok, motiv = valideaza_cui("12345678")
    assert not ok and "control" in motiv


def test_cui_lipsa():
    assert valideaza_cui("")[0] is False
    assert valideaza_cui(None)[0] is False


def test_prefixul_RO_nu_deranjeaza():
    assert valideaza_cui("RO14399840") == valideaza_cui("14399840")


# ---------- randuri ----------
def _r(cont, cui, den="X", d=100, c=0):
    return {"cont": cont, "cui": cui, "denumire": den, "debit": d, "credit": c}


def test_randul_corect_trece():
    er, bune = verifica_randuri([_r("4111", "RO14399840", "DEDEMAN SRL")])
    assert not er and len(bune) == 1


def test_cont_care_nu_tine_parteneri_e_respins():
    """5121 (banca), 5311 (casa), 707 (venituri) nu au parteneri: un sold pe partener
    acolo e o eroare de export, nu o realitate contabila."""
    er, bune = verifica_randuri([_r("5121", "RO14399840", "BANCA")])
    assert len(er) == 1 and er[0]["motiv"] == "cont_nepartener"
    assert not bune


def test_partener_fara_cui_e_respins():
    """Soldurile pe parteneri intra in D394 si SAF-T - acolo CUI-ul e obligatoriu."""
    er, _ = verifica_randuri([_r("4111", "", "PARTENER FARA CUI")])
    assert len(er) == 1 and er[0]["motiv"] == "cui_invalid"
    assert "nu are CUI" in er[0]["mesaj"]


def test_analiticele_sunt_acceptate():
    """4111.01 e tot cont de clienti - radacina decide."""
    er, bune = verifica_randuri([_r("4111.01", "RO14399840", "DEDEMAN SRL")])
    assert not er and len(bune) == 1


def test_numarul_randului_e_cel_din_fisier():
    """Antetul e randul 1, deci primul rand de date e 2 - ca sa-l gaseasca omul."""
    er, _ = verifica_randuri([_r("5121", "RO14399840")])
    assert er[0]["rand"] == 2


def test_importa_REFUZA_randurile_invalide():
    """Refuzul e prima poarta: nimic nu se scrie dintr-un import cu randuri invalide.
    Regresie 15.07.2026: importa() scria orice, iar migrarea marca stratul 'gata' verde."""
    with pytest.raises(ValueError) as e:
        importa(None, [_r("4111", "RO14399840", "DEDEMAN SRL"),
                       _r("4111", "12345678", "FIRMA INVENTATA"),
                       _r("5121", "RO4221306", "BANCA")])
    m = str(e.value)
    assert "2 rânduri" in m
    assert "12345678" in m and "5121" in m
    assert "D394" in m or "SAF-T" in m      # spune DE CE conteaza


def test_conturile_de_parteneri_sunt_cele_din_omfp():
    assert "4111" in CONTURI_PARTENERI and "401" in CONTURI_PARTENERI
    assert "5121" not in CONTURI_PARTENERI


# ---------- maparea coloanelor ----------
def test_denumirea_nu_mai_e_cui_ul():
    """Antetul 'CUI partener' contine 'partener' -> era gasit inaintea coloanei
    'Denumire partener'. In baza ajungea denumire='RO14399840' in loc de 'DEDEMAN SRL'."""
    antet = ["Cont", "CUI partener", "Denumire partener", "Sold debitor", "Sold creditor"]
    i_cont = _gaseste_col(antet, "cont", "simbol")
    i_cui = _gaseste_col(antet, "cui", "cif", "cod fiscal")
    i_den = _gaseste_col(antet, "denumire", "nume", "partener", exclus=[i_cont, i_cui])
    assert (i_cont, i_cui, i_den) == (0, 1, 2)
