"""Teste D177 (redirectionare impozit pe profit catre entitati nonprofit).
Structura din validatorul oficial (D177Validator.jar, v1) + semantica din anaf_surse (OPANAF_3562_2024_D177
+ structura_D177_2026). Proba pe DUKIntegrator -v D177."""
import os
import pytest
from core import d177

_JAR = "/home/costin/duk/dist/lib/D177Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self):
        return ("14399840", "TEST SRL", "Str Test 1 Bucuresti", "0211234567", "t@t.ro")


def _manual(**ov):
    m = {"tip_platitor": 1, "data_inceput": "2025-01-01", "data_sfarsit": "2025-12-31",
         "suma_max": 10000, "suma_ant": 0, "suma_rest": 10000,
         "beneficiari": [{"tip": "2", "cui": "14399840", "den": "Asociatia Binele",
                          "iban": "RO49AAAA1B31007593840000", "contract": "12/2025", "suma": 10000, "acord": "1"}]}
    m.update(ov)
    return m


def test_d177_control_sum():
    """totalPlata_A = 0 (D177 informativa; validator J2.0.3/v1). Vechea formula round(sumaRest/100)
    era fals-confirmata pe validatorul vechi care crapa tacit."""
    assert d177.calcul_d177({"suma_rest": 10000})["totalPlata_A"] == "0"
    assert d177.calcul_d177({"suma_rest": 1250})["totalPlata_A"] == "0"


def test_d177_build_xml():
    c = d177.calcul_d177(_manual())
    xml = d177.build_xml({"cui": "14399840", "den": "F"}, 2025, 12, _manual(), c)
    assert 'xmlns="mfp:anaf:dgti:d177:declaratie:v1"' in xml
    assert 'tipPlatitor="1"' in xml and 'tipB="2"' in xml
    assert 'sumaRest="10000"' in xml and 'totalPlata_A="0"' in xml
    assert '<D177 ' in xml and '</D177>' in xml


def test_d177_reguli():
    prof = {"cui": "14399840", "den": "F"}
    assert any("sumaMax" in e for e in d177.erori_generare(prof, _manual(suma_max=5000)))       # max < ant+rest
    b = _manual(); b["beneficiari"][0]["tip"] = "4"
    assert any("tipB" in e for e in d177.erori_generare(prof, b))                                # 4 nepermis
    b = _manual(); b["beneficiari"][0]["contract"] = ""
    assert any("contractB" in e for e in d177.erori_generare(prof, b))                           # tipB<5 -> contract
    b = _manual(); b["beneficiari"][0]["suma"] = 20000
    assert any("depaseste sumaRest" in e for e in d177.erori_generare(prof, b))                  # Σsuma>rest


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D177 nu e instalat in DUK.")
def test_d177_valid_pe_validatorul_oficial():
    from core import duk
    from core.common import Perioada
    xml, res = d177.genereaza(_P(), "s", Perioada(2025, luna=12), _manual())
    rez = duk.valideaza(xml, "d177", an=2025, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
