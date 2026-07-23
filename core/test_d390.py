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
import datetime
import pytest
from core import d390
from core.d390 import calcul_d390, build_xml, valideaza, operatiuni_auto


def test_d390_are_operatiuni_luna_deschisa_none_fara_db():
    """Poarta perioadei DESCHISE: luna curenta/viitoare -> None INAINTE de orice interogare (conn nefolosit).
    D390 nu e obligatie lunara fixa; luna deschisa nu se poate decide inca (exigibilitatea nu s-a nascut)."""
    AZI = datetime.date(2026, 7, 23)
    assert d390.d390_are_operatiuni(None, "x", 2026, 7, azi=AZI) is None    # luna curenta, inca deschisa
    assert d390.d390_are_operatiuni(None, "x", 2026, 12, azi=AZI) is None   # viitoare
    assert d390.d390_are_operatiuni(None, "x", 2099, 1, azi=AZI) is None    # mult in viitor


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


# ---------- F125: clasificare manuala (reclasificare + adaugare) ----------
_FACT_IC = [{"cui": "IT00905811006", "nume": "AUCHAN ITALIA SPA", "directie": "emisa", "total": 5000, "tva": 0}]


def test_reclasificare_muta_tipul_fara_dubla_numarare():
    """Auto pune emisa->L (bunuri). Reclasificat L->P (serviciu prestat) -> valoarea trece
    din L in P, NU se adauga (fara dubla numarare). nr_opi ramane 1."""
    recl = {("emisa", "IT", "00905811006"): "P"}
    res = calcul_d390(_prof(), 2026, 6, _FACT_IC, reclasificari=recl)
    assert res.rezumat["L"] == 0
    assert res.rezumat["P"] == 5000
    assert res.nr_opi == 1


def test_reclasificare_ignora_tip_invalid():
    """Un tip care nu e in nomenclator -> revine la default (nu strica calculul)."""
    res = calcul_d390(_prof(), 2026, 6, _FACT_IC, reclasificari={("emisa", "IT", "00905811006"): "Z"})
    assert res.rezumat["L"] == 5000


def test_linie_manuala_se_adauga():
    man = [{"tip": "S", "tara": "DE", "cod": "136695976", "den": "SERVICE", "baza": 1000}]
    res = calcul_d390(_prof(), 2026, 6, [], manual=man)
    assert res.rezumat["S"] == 1000
    assert res.nr_opi == 1


def test_operatiuni_auto_arata_tipul_curent():
    """Pt UI: operatiunea auto arata tip_default si tip_curent (reclasificat)."""
    recl = {("emisa", "IT", "00905811006"): "P"}
    ops = operatiuni_auto(_FACT_IC, recl)
    assert len(ops) == 1
    assert ops[0]["tip_default"] == "L" and ops[0]["tip_curent"] == "P"
    assert ops[0]["baza"] == 5000
