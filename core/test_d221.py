"""Teste D221 (venituri din activitati agricole impuse pe norme de venit - persoane fizice/asocieri).
Structura din validatorul oficial (D221Validator.jar, v0/namespace :v1) + semantica din anaf_surse
(structura_D221_2017_050118 + d221_20170303.xsd, OPANAF 3622/2015). Proba pe DUKIntegrator -v D221."""
import os
import pytest
from core import d221
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D221Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self): return ("POPESCU", "ION", "TITULAR")


def _individual():
    return {"cif": "1850715400015", "nume_a": "Popescu Ion", "adresa_a": "Comuna Test, jud. Cluj",
            "forma_org": "1", "activitati": [{"judet": "12", "localitate": "Comuna Test", "optiune": "0",
                "produse": [{"codp": "101", "prod1": 12.5}, {"codp": "201", "prod1": 8}]}]}


def _asociere():
    return {"cif": "1850715400015", "nume_a": "Asocierea Agricola", "adresa_a": "Comuna Test",
            "forma_org": "2", "nr_contr": "AS-01/2025", "data_contr": "15.01.2025",
            "activitati": [{"judet": "12", "localitate": "Comuna Test", "optiune": "0",
                            "produse": [{"codp": "101", "prod1": 20}]}],
            "asociati": [{"nume_d": "Ionescu Maria", "cif_d": "2850312400073", "dom_d": "Comuna Test", "cota_d": 60},
                         {"nume_d": "Georgescu Vasile", "cif_d": "1800101400016", "dom_d": "Comuna Test", "cota_d": 40}]}


def test_d221_structura_fixa():
    """totalPlata_A=0 mereu; aj_soc=0; luna=12; activitati INAINTE de asociati (ordine XSD)."""
    xml = d221.build_xml({}, 2025, _asociere())
    assert 'totalPlata_A="0"' in xml and 'aj_soc="0"' in xml and 'luna="12"' in xml
    assert xml.index("<activitati") < xml.index("<asociati")     # ordine XSD


def test_d221_erori():
    prof = {"declarant_nume": "P", "declarant_prenume": "I", "declarant_functie": "T"}
    # forma_org=2 fara asociati
    m = dict(_asociere(), asociati=[])
    assert any("2 asociati" in e or "asociat" in e for e in d221.erori_generare(prof, 2025, m))
    # cote != 100
    m2 = dict(_asociere())
    m2 = {**m2, "asociati": [{"nume_d": "A", "cif_d": "2850312400073", "dom_d": "X", "cota_d": 60},
                             {"nume_d": "B", "cif_d": "1800101400016", "dom_d": "Y", "cota_d": 30}]}
    assert any("100" in e for e in d221.erori_generare(prof, 2025, m2))
    # cif_d nu are 13 cifre
    m3 = {**_asociere(), "asociati": [{"nume_d": "A", "cif_d": "123", "dom_d": "X", "cota_d": 50},
                                      {"nume_d": "B", "cif_d": "1800101400016", "dom_d": "Y", "cota_d": 50}]}
    assert any("13 cifre" in e for e in d221.erori_generare(prof, 2025, m3))
    # individual cu asociati
    m4 = dict(_individual(), asociati=[{"nume_d": "A", "cif_d": "2850312400073", "dom_d": "X", "cota_d": 100}])
    assert any("individual" in e for e in d221.erori_generare(prof, 2025, m4))
    # fara activitati
    assert any("activitate" in e for e in d221.erori_generare(prof, 2025, dict(_individual(), activitati=[])))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D221 nu e instalat in DUK.")
def test_d221_valid_pe_validatorul_oficial():
    from core import duk
    x1, _ = d221.genereaza(_P(), "s", Perioada(2025), _individual())
    assert duk.valideaza(x1, "d221", an=2025, luna=12)["stare"] == "valid"
    x2, _ = d221.genereaza(_P(), "s", Perioada(2025), _asociere())
    rez = duk.valideaza(x2, "d221", an=2025, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
