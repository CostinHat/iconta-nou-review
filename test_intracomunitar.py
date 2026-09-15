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

def test_lic_ok():
    ok, ment = m.valideaza_lic("DE123456789", True, True)
    assert ok and "294" in ment

def test_lic_cod_invalid():
    with pytest.raises(ValueError, match="INVALID in VIES"):
        m.valideaza_lic("DE123456789", False, True)

def test_lic_fara_transport():
    with pytest.raises(ValueError, match="transport"):
        m.valideaza_lic("DE123456789", True, False)

def test_lic_client_ro():
    with pytest.raises(ValueError, match="din RO"):
        m.valideaza_lic("RO34142700", True, True)

def test_prestare_ok():
    ok, ment = m.valideaza_prestare_ic("FR12345678901", True)
    assert ok and "278" in ment

def test_prestare_cod_invalid():
    with pytest.raises(ValueError, match="B2C"):
        m.valideaza_prestare_ic("FR12345678901", False)
