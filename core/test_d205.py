# -*- coding: utf-8 -*-
"""Teste gardian pentru D205 - modulul a fost REFACUT complet 16.07.2026.

Structura reala (structura_D205_2025_120226.pdf, 461 linii, citite integral):
  <declaratie205 ...>
    <sect_II tip_venit="25" nrben="N" Tcastig=".." Tpierd=".." T_VB=".." T_GAR=".."
             Tbaza=".." Timp=".."/>    <!-- element GOL, doar atribute -->
    <benef categ="1.a" nume1=".." cif=".." baza1=".." imp1=".."/>   <!-- 1-n, FRATE
                                                                          cu sect_II -->
    <benef .../>
  </declaratie205>

Regresie: prima incercare pusese <benef> IN INTERIORUL lui <sect_II> (structura
gresita, citind doar primele ~180 din 461 linii ale documentului). Validatorul:
"sectiunea benef este gresit pozitionata" - sect_II si benef sunt FRATI, copii
directi ai radacinii, nu parinte-copil.
"""
import pytest
from core.d205 import calcul_d205, build_xml


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA", "adresa": "X"}


def test_beneficiar_dividende_simplu():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "POPESCU Ion", "cif": "1850101450019",
         "baza": 10000, "imp": 1000, "castig": 10000}])
    assert res.beneficiari[0].nume1 == "POPESCU Ion"
    assert res.beneficiari[0].imp1 == 1000
    assert res.total_plata_a == 1000


def test_beneficiar_fara_suma_nu_intra():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1", "baza": 0, "imp": 0}])
    assert res.beneficiari == []


def test_fara_beneficiari_refuza_generarea():
    """D205 fara continut nu se genereaza."""
    res = calcul_d205(_prof(), 2025, [])
    with pytest.raises(ValueError):
        build_xml(res)


def test_sect_II_si_benef_sunt_frati_nu_parinte_copil():
    """Regresie: benef NU e in interiorul lui sect_II. sect_II se inchide singur
    (element gol, doar atribute), benef vine dupa, la acelasi nivel."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1", "baza": 100, "imp": 10, "castig": 100}])
    xml = build_xml(res)
    assert '<sect_II tip_venit="25"' in xml
    assert xml.count("<sect_II") == 1
    # sect_II e element gol (self-closing cu /) - nu are inchidere separata </sect_II>
    assert "</sect_II>" not in xml
    # benef apare DUPA sect_II, nu inainte de inchiderea lui (pt ca nu exista inchidere)
    poz_sect = xml.index("<sect_II")
    poz_benef = xml.index("<benef")
    assert poz_benef > poz_sect


def test_totalurile_se_calculeaza_din_beneficiari():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "A", "cif": "1", "baza": 1000, "imp": 100, "castig": 1000},
        {"categ": "1.a", "nume": "B", "cif": "2", "baza": 2000, "imp": 200, "castig": 2000},
    ])
    xml = build_xml(res)
    assert 'nrben="2"' in xml
    assert 'Tcastig="3000"' in xml
    assert 'Timp="300"' in xml
