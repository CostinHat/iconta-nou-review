"""Teste D311 (TVA in situatii speciale dupa anularea codului de TVA).
Structura + calcule din SURSA OFICIALA: anaf_surse/d311_20210129.xsd +
structura_D311_2021_290121.pdf. Proba pe validatorul OFICIAL ANAF (DUKIntegrator -v D311)."""
import os
import pytest
from core import d311

_JAR_D311 = "/home/costin/duk/dist/lib/D311Validator.jar"


def _prof():
    return {"den": "TEST SRL", "nume": "TEST SRL", "cui": "14399840",
            "adresa": "Str Test 1 Bucuresti", "declarant_nume": "POPESCU",
            "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR",
            "telefon": "0211234567", "email": "test@test.ro"}


def _manual():
    # schema IV (dupa anulare): 3 randuri de intrare -> subtotale + total calculate
    return {"schema": 1, "Data_A": "2026-03-15", "d_anul1": 1, "d_anul2": 0,
            "d_rec": 0, "d_anulare": 0, "temei": 1,
            "OB_11": 1000, "OB_12": 210, "OB_21": 500, "OB_22": 105,
            "OB_41": 200, "OB_42": 42}


def test_d311_calcul_din_structura():
    """Calcule din structura D311 (rd.03/05/19): OB_31=OB_11+OB_21, OB_32=OB_12+OB_22,
    OB_51=OB_31+OB_41, OB_52=OB_32+OB_42; totalPlata_A=OB_51+OB_52+OB_61+OB_62."""
    ob, total = d311.calcul_d311(_manual())
    assert (ob["OB_31"], ob["OB_32"]) == (1500, 315)   # 1000+500 / 210+105
    assert (ob["OB_51"], ob["OB_52"]) == (1700, 357)   # 1500+200 / 315+42
    assert total == 2057                                # 1700+357+0+0


def test_d311_build_xml_conform_xsd():
    m = _manual()
    ob, total = d311.calcul_d311(m)
    xml = d311.build_xml(_prof(), 2026, 6, m, ob, total)
    assert 'xmlns="mfp:anaf:dgti:d311:declaratie:v1"' in xml
    assert 'totalPlata_A="2057"' in xml
    assert 'OB_51="1700"' in xml and 'OB_52="357"' in xml
    assert 'Data_A="15.03.2026"' in xml          # DateSType ZZ.LL.AAAA
    assert 'cui="14399840"' in xml               # CifSType: fara prefix RO
    assert 'd_anul1="1"' in xml and 'd_anul2="0"' in xml


def test_d311_erori_schema():
    prof = _prof()
    m = _manual(); m.pop("Data_A")
    assert any("Data_A" in e for e in d311.erori_generare(prof, m)), "lipsa Data_A trebuie prinsa"
    m = _manual(); m["d_anul1"] = 1; m["d_anul2"] = 1
    assert any("d_anul" in e for e in d311.erori_generare(prof, m)), "ambele bife trebuie respinse"
    m = {"schema": 1, "Data_A": "2026-03-15", "d_anul1": 1, "d_anul2": 0}
    assert any("OB_51+OB_52" in e for e in d311.erori_generare(prof, m)), "zero pe schema IV respins"


@pytest.mark.skipif(not os.path.exists(_JAR_D311), reason="Validatorul D311 nu e instalat in DUK.")
def test_d311_valid_pe_validatorul_oficial():
    """Proba pe validatorul OFICIAL ANAF (DUKIntegrator -v D311) - date reale, nu doar structura."""
    from core import duk
    m = _manual()
    ob, total = d311.calcul_d311(m)
    xml = d311.build_xml(_prof(), 2026, 6, m, ob, total)
    rez = duk.valideaza(xml, "d311", an=2026, luna=6)
    assert rez["stare"] == "valid", rez.get("erori")
