# -*- coding: utf-8 -*-
"""Teste gardian pentru D390 — modulul n-avea niciunul.

Doua buguri gasite prin audit pe date reale (16.07.2026):
1. <rezumat> lipsea ca element separat (fix anterior gresit il pusese inline pe
   radacina, pe baza unui `strings` care n-a gasit clasa/tag "rezumat" - concluzie
   gresita: absenta dintr-un extras nu inseamna absenta).
2. pull() citea CUI-ul partenerului DOAR din clienti.cui (via client_id). Facturile
   fara fisa de client si TOATE facturile PRIMITE (care n-au niciodata client_id)
   aveau cui="" -> respinse tacit -> D390 genera mereu "0 operatiuni".
"""
import pytest
from core.d390 import calcul_d390, build_xml, valideaza


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
            "adresa": "Bd. Timisoara 26Z", "telefon": "0212345678"}


def test_operatiune_emisa_UE_intra_in_calcul():
    facturi = [{"cui": "IT00905811006", "nume": "AUCHAN ITALIA SPA",
                "directie": "emisa", "total": 5000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 6, facturi)
    assert res.nr_opi == 1
    assert res.rezumat["L"] == 5000


def test_operatiune_primita_UE_intra_in_calcul():
    """Regresie: facturile primite n-aveau niciodata client_id, deci CUI-ul lipsea."""
    facturi = [{"cui": "DE136695976", "nume": "BAUHAUS GMBH",
                "directie": "primita", "total": 2000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 6, facturi)
    assert res.nr_opi == 1
    assert res.rezumat["A"] == 2000


def test_rezumat_e_element_separat_in_xml():
    """<rezumat> exista ca element propriu, nu atribute pe radacina (dovedit pe
    structura oficiala ANAF, structura_D390_2020_180320.pdf: '<rezumat> 1 aparitie')."""
    res = calcul_d390(_prof(), 2026, 6, [
        {"cui": "IT00905811006", "nume": "X", "directie": "emisa", "total": 100, "tva": 0}])
    xml = build_xml(res)
    assert "<rezumat " in xml
    assert 'nrOPI="' not in xml.split("<rezumat")[0]  # nu e pe radacina


def test_factura_fara_cui_ue_valid_e_ignorata():
    facturi = [{"cui": "RO14399840", "nume": "FIRMA INTERNA",
                "directie": "emisa", "total": 1000, "tva": 210}]
    res = calcul_d390(_prof(), 2026, 6, facturi)
    assert res.nr_opi == 0
    assert "excluse" in " ".join(res.avertismente)
