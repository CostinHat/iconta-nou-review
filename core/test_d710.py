# -*- coding: utf-8 -*-
"""Teste gardian pentru D710 (Declaratie rectificativa - corectie D100).

Structura si regulile au fost extrase din D710Validator.jar (parameters v10,
versiuni.xml D710_56) si verificate/corectate iterativ pe validatorul oficial DUK
(20.07.2026). Fiecare test apara o regula dovedita pe validator - vezi core/d710.py.

Esenta: fiecare suma are pereche Initial (_I) / Corectat (_C). Motorul acopera
rectificarea sumei DATORATE (suma_plata = suma_dat); deducerile/reducerile (model 8#)
sunt LIMITA documentata, la caz real.
"""
import pytest
from core.d710 import calcul_d710, build_xml, NS, _scadenta_d710
from core.d100 import COD_BUGETAR
import core.duk as duk


def _prof():
    return {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL",
            "adresa": "Str. Test nr.1 Bucuresti Sector 1"}


def _obl(cod="121", i=100, c=150, cota="1"):
    return [{"cod_oblig": cod, "suma_dat_i": i, "suma_dat_c": c, "cota": cota}]


# ---- structura / calcul (pur, fara java) ----

def test_namespace_e_d710_nu_d100():
    """Namespace propriu - NU se reutilizeaza structura D100 (verificat la sursa)."""
    assert NS == "mfp:anaf:dgti:d710:declaratie:v2"
    xml = build_xml(calcul_d710(_prof(), 2025, 3, _obl()))
    assert "declaratie710" in xml and NS in xml
    assert "declaratie100" not in xml


def test_suma_plata_egala_suma_dat_pe_ambele_laturi():
    """Rectificare suma datorata: suma_plata = suma_dat (initial si corectat)."""
    o = calcul_d710(_prof(), 2025, 3, _obl(i=100, c=150)).obligatii[0]
    assert o.suma_plata_i == o.suma_dat_i == 100
    assert o.suma_plata_c == o.suma_dat_c == 150


def test_xml_are_perechea_initial_corectat():
    xml = build_xml(calcul_d710(_prof(), 2025, 3, _obl(i=100, c=150)))
    lin = [l for l in xml.split("\n") if "<obligatie" in l][0]
    assert 'suma_dat_I="100"' in lin and 'suma_dat_C="150"' in lin
    assert 'suma_plata_I="100"' in lin and 'suma_plata_C="150"' in lin


def test_totalPlata_A_suma_dat_plus_plata_ambele_laturi():
    """R11b: totalPlata_A = dat_I + plata_I + dat_C + plata_C = 100+100+150+150 = 500."""
    res = calcul_d710(_prof(), 2025, 3, _obl(i=100, c=150))
    assert res.total_plata_a == 500
    assert 'totalPlata_A="500"' in build_xml(res)


def test_d_recN_doar_de_la_perioada_12_2025():
    """d_recN apare DOAR de la perioada de raportare 12.2025 (regula validator);
    pentru perioade anterioare NU se pune (validatorul il respinge)."""
    xml_vechi = build_xml(calcul_d710(_prof(), 2025, 3, _obl()))   # 03.2025
    assert "d_recN" not in xml_vechi
    xml_nou = build_xml(calcul_d710(_prof(), 2025, 12, _obl()))    # 12.2025
    assert 'd_recN="1"' in xml_nou
    xml_2026 = build_xml(calcul_d710(_prof(), 2026, 3, _obl()))    # 03.2026
    assert 'd_recN="1"' in xml_2026


def test_scadenta_micro_trim4_e_25_iunie_an_urmator():
    """Cod 121 (micro) trim4 (luna 12): scadenta 25.06 an urmator, nu 25.01 (R15)."""
    assert _scadenta_d710("121", 2025, 12) == (25, 6, 2026)
    # celelalte trimestre: 25 a lunii urmatoare
    assert _scadenta_d710("121", 2025, 3) == (25, 4, 2025)
    assert _scadenta_d710("103", 2025, 12) == (25, 1, 2026)


def test_cota_doar_la_cod_121():
    xm = build_xml(calcul_d710(_prof(), 2025, 3, _obl(cod="121", cota="1")))
    assert 'cota="1"' in [l for l in xm.split("\n") if "<obligatie" in l][0]
    xp = build_xml(calcul_d710(_prof(), 2025, 6, [{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400}]))
    assert 'cota=' not in [l for l in xp.split("\n") if "<obligatie" in l][0]


def test_cod_bugetar_din_nomenclator():
    o = calcul_d710(_prof(), 2025, 3, _obl(cod="121")).obligatii[0]
    assert o.cod_bugetar == COD_BUGETAR["121"] == "20470101"


def test_nr_evid_23_caractere_poz_3_5_cod_oblig():
    o = calcul_d710(_prof(), 2025, 3, _obl(cod="121")).obligatii[0]
    assert len(o.nr_evid) == 23 and o.nr_evid.isdigit()
    assert o.nr_evid[2:5] == "121"


def test_luna_invalida_respinsa():
    with pytest.raises(ValueError):
        calcul_d710(_prof(), 2025, 5, _obl())


def test_obligatie_ambele_zero_nu_intra():
    res = calcul_d710(_prof(), 2025, 3, [{"cod_oblig": "121", "suma_dat_i": 0, "suma_dat_c": 0, "cota": "1"}])
    assert res.obligatii == []


# ---- validare pe DUK (judecatorul final ANAF) - gated ----
_DUK = duk.poate_valida("d710")


@pytest.mark.skipif(not _DUK, reason="validatorul D710 nu e instalat in pachetul DUK")
@pytest.mark.parametrize("an,luna,obl", [
    (2025, 3,  _obl(cod="121", i=100, c=150)),            # micro simplu
    (2025, 12, _obl(cod="121", i=100, c=150)),            # micro trim4 (scadenta speciala + d_recN)
    (2026, 3,  _obl(cod="121", i=100, c=150)),            # micro cu d_recN
    (2025, 6,  [{"cod_oblig": "103", "suma_dat_i": 1000, "suma_dat_c": 1600}]),  # profit
    (2025, 6,  _obl(cod="121", i=150, c=100)),            # corectie in scadere
])
def test_valid_pe_duk_fara_erori(an, luna, obl):
    xml = build_xml(calcul_d710(_prof(), an, luna, obl))
    r = duk.valideaza(xml, "d710")
    assert r["stare"] == "valid", "DUK a gasit erori: %s" % r["erori"]


@pytest.mark.skipif(not _DUK, reason="validatorul D710 nu e instalat in pachetul DUK")
def test_duk_respinge_gunoi():
    """Un validator care nu poate spune NU nu e validator."""
    gunoi = '<?xml version="1.0"?><aiurea xmlns="mfp:anaf:dgti:inventat:v99" x="1"/>'
    assert duk.valideaza(gunoi, "d710")["stare"] != "valid"
