# -*- coding: utf-8 -*-
"""Teste gardian pentru D100 - modulul a fost REFACUT complet 16.07.2026.

D100 e diferita structural de celelalte declaratii: nu are un set fix de campuri,
ci raporteaza o LISTA de obligatii fiscale (element repetabil <obligatie>), fiecare
din Nomenclatorul ANAF (https://static.anaf.ro/.../NomBugetStat.htm), cu propriul
cod_oblig, cod_bugetar, suma si nr_evid (numar de evidenta a platii, 23 caractere
cu structura fixa si cifra de control).

Atributele reale au fost extrase din D100Validator.jar (constant pool), apoi
verificate/corectate iterativ pe validatorul oficial: cui/luna/tip_oblig NU
apartin sectiunii <obligatie> (desi apar in constant pool, sunt uz intern);
nr_evid are 23 pozitii cu formula exacta de control; totalPlata_A = suma pe
toate campurile (suma_dat+suma_ded+suma_plata+suma_rest), nu doar suma_dat.
"""
import pytest
from core.d100 import calcul_d100, build_xml, _nr_evid, COD_BUGETAR


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA", "adresa": "X"}


def test_nr_evid_are_23_caractere():
    n = _nr_evid("103", 6, 2026, 25, 7, 2026)
    assert len(n) == 23
    assert n.isdigit()


def test_nr_evid_incepe_cu_10_si_cod_oblig():
    """Poz.1-2 = '10' fix, poz.3-5 = cod_oblig (3 cifre)."""
    n = _nr_evid("103", 6, 2026, 25, 7, 2026)
    assert n[:2] == "10"
    assert n[2:5] == "103"
    assert n[5:7] == "01"


def test_nr_evid_cifra_de_control():
    """Poz.22-23 = ultimele 2 cifre din suma primelor 21 pozitii."""
    n = _nr_evid("103", 6, 2026, 25, 7, 2026)
    suma = sum(int(c) for c in n[:21])
    assert n[21:23] == "%02d" % (suma % 100)


def test_calcul_micro():
    # cod_oblig micro = 121 (codul din nomenclator), NU pozitia "5" (respinsa de
    # validator: "valoarea '5' nu se afla in lista"). cont unic 20470101.
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000, "cota": "1"}])
    assert res.obligatii[0].cod_oblig == "121"
    assert res.obligatii[0].cod_bugetar == COD_BUGETAR["121"] == "20470101"


def test_micro_are_cota_1_pe_obligatie():
    """Reguli R17 + Rcota: cod_oblig 121 CERE cota="1" pe <obligatie>; profitul (103)
    NU are cota. Fara ea, validatorul respinge micro-ul."""
    xm = build_xml(calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000, "cota": "1"}]))
    lin_m = [l for l in xm.split("\n") if "<obligatie" in l][0]
    assert 'cota="1"' in lin_m
    xp = build_xml(calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 2400}]))
    lin_p = [l for l in xp.split("\n") if "<obligatie" in l][0]
    assert 'cota=' not in lin_p


def test_calcul_profit():
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 2400}])
    assert res.obligatii[0].cod_oblig == "103"
    assert res.obligatii[0].cod_bugetar == "20470101"


def test_obligatie_cu_suma_zero_nu_intra():
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 0}])
    assert res.obligatii == []


def test_luna_invalida_e_respinsa():
    """D100 trimestrial: luna trebuie sa fie 3, 6, 9 sau 12."""
    with pytest.raises(ValueError):
        calcul_d100(_prof(), 2026, 5, [{"cod_oblig": "103", "suma_dat": 100}])


def test_xml_nu_are_cui_luna_tip_oblig_pe_obligatie():
    """Regresie: aceste atribute apar in constant pool-ul clasei Obligatie, dar
    validatorul le respinge ca 'atribut necunoscut' - nu se scriu in XML."""
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 100}])
    xml = build_xml(res)
    linie_obligatie = [l for l in xml.split("\n") if "<obligatie" in l][0]
    assert 'cui=' not in linie_obligatie
    assert 'luna=' not in linie_obligatie
    assert 'tip_oblig=' not in linie_obligatie


def test_totalPlata_A_e_suma_dat_plus_suma_plata():
    """DUK regula R11b: totalPlata_A = suma_dat + suma_ded + suma_plata + suma_rest.
    Cu suma_plata = suma_dat si ded/rest = 0, e 2x suma_dat."""
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 2400}])
    xml = build_xml(res)
    assert 'totalPlata_A="4800"' in xml
