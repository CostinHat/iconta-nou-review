# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import intracomunitar as m

def test_desparte():
    assert m.desparte_cod_tva("DE 123 456 789") == ("DE", "123456789")
    assert m.desparte_cod_tva("gr123") == ("EL", "123")

def test_desparte_non_ue():
    with pytest.raises(ValueError, match="stat membru"):
        m.desparte_cod_tva("US123456")

def test_desparte_gol():
    # [15.09.2026] Proba cerea cuvantul „lipsa" din vechiul mesaj („numar TVA lipsa dupa codul de
    # tara"). Mesajul s-a rescris — R185 l-a facut PUBLICAT, iar clichetul de diacritice cere ca un
    # text afisat sa fie in romana intreaga. Proba se muta pe ce CONTEAZA, nu pe un cuvant: refuzul
    # trebuie sa numeasca prefixul primit si sa arate forma asteptata. *Un test ancorat pe un cuvant
    # apara formularea, nu comportamentul.*
    with pytest.raises(ValueError) as e:
        m.desparte_cod_tva("DE")
    mesaj = str(e.value)
    assert "DE" in mesaj, "refuzul nu spune ce prefix a primit"
    assert "DE123456789" in mesaj, "refuzul nu arata forma unui cod complet"

def test_tva_ti():
    assert m.tva_taxare_inversa(10000, cota=21) == Decimal("2100.00")
    with pytest.raises(ValueError):
        m.tva_taxare_inversa(-1, cota=21)

# [lotul 12, C84, decizia Costin 12.3 pct.7] `valideaza_lic` s-a scos (fără apelant de la C84 (b): livrarea de bunuri se emite din
# „Emite factură”), odată cu refuzul „fără dovada transportului”, care devine avertisment la emitere. Testele ei (cod VIES invalid, client
# din RO, fără transport) au plecat cu ea; livrarea din „Emite factură” e păzită de core/test_lot12_fisc3_c84_dovada_transport.py, iar
# clientul din RO de core/test_274b_categorii_tva.py (livrare_ic -> CATEGORIE_TVA_TARA).
def test_lic_fara_dovada_e_avertisment_care_spune_ce_lipseste():
    assert not hasattr(m, "valideaza_lic")
    assert m.INTREBARE_DOVADA_TRANSPORT == ("Ai dovada transportului bunurilor în alt stat membru? Scutirea livrării intracomunitare se "
                                            "aplică numai dacă o poți justifica cu documentele de transport.")

def test_prestare_ok():
    ok, ment = m.valideaza_prestare_ic("FR12345678901", True)
    assert ok and "278" in ment

def test_prestare_cod_invalid():
    with pytest.raises(ValueError, match="art. 278 alin.\\(3\\)"):
        m.valideaza_prestare_ic("FR12345678901", False)
