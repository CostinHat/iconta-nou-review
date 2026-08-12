"""Teste D220 (venit estimat / norma de venit - persoane fizice).
Structura din validatorul oficial (D220Validator.jar, v1/namespace :v2, in vigoare 2017-01) + semantica din
anaf_surse (structura_D220_2017_09012018 + d220_20180108.xsd, OPANAF 3622/2015). Proba pe DUKIntegrator -v D220.
NOTA: D220 e superseata de D212 (Declaratia Unica) pentru depuneri curente; se pastreaza pt cazuri retro-2017."""
import os
import pytest
from core import d220
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D220Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self): return ("POPESCU", "ION", "TITULAR")


def _manual():
    return {"cif": "1850615400011", "nume": "POPESCU ION",
            "activitate": {"categ_venit": "1", "det_venit": "1", "forma_org": "1",
                           "venit_brut": 10000, "cheltuieli": 4000}}


def test_d220_totaluri_si_drec():
    """net3=venit3-chelt3 (>=0); totalPlata_A=venit3+chelt3+net3; d_rec=1 daca d_rec1>0 sau d_rec2=1."""
    c = d220.calcul_d220(_manual())
    assert c["net3"] == 6000 and c["totalPlata_A"] == 20000 and c["d_rec"] == 0
    # venit < chelt -> net3 = 0
    c2 = d220.calcul_d220({"activitate": {"venit_brut": 3000, "cheltuieli": 5000}})
    assert c2["net3"] == 0 and c2["totalPlata_A"] == 8000
    # d_rec derivat
    assert d220.calcul_d220(dict(_manual(), d_rec2=1))["d_rec"] == 1
    assert d220.calcul_d220(dict(_manual(), d_rec1=2))["d_rec"] == 1


def test_d220_stat_pensie_omis():
    """stat_pensie NU trebuie sa apara pt categ_venit 1..7 (validatorul il respinge)."""
    xml, _ = d220.genereaza(_P(), "s", Perioada(2018), _manual())
    assert "stat_pensie" not in xml


def test_d220_erori():
    prof = {"declarant_nume": "P", "declarant_prenume": "I"}
    assert any("CNP" in e for e in d220.erori_generare(prof, {"nume": "X", "activitate": {
        "categ_venit": "1", "det_venit": "1", "forma_org": "1"}}))
    assert any("categ_venit" in e for e in d220.erori_generare(prof, {"cif": "1850615400011", "nume": "X",
        "activitate": {"categ_venit": "9", "det_venit": "1", "forma_org": "1"}}))
    # cazare turistica fara fisa
    caz = {"cif": "1850615400011", "nume": "X", "activitate": {
        "categ_venit": "7", "contracte": "3", "det_venit": "3", "forma_org": "1"}}
    assert any("fisa" in e for e in d220.erori_generare(prof, caz))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D220 nu e instalat in DUK.")
def test_d220_valid_pe_validatorul_oficial():
    from core import duk
    xml, _ = d220.genereaza(_P(), "s", Perioada(2018), _manual())
    assert duk.valideaza(xml, "d220", an=2018, luna=12)["stare"] == "valid"
    # cazare turistica cu fisa + camere
    caz = {"cif": "1850615400011", "nume": "POPESCU ION", "activitate": {
        "categ_venit": "7", "contracte": "3", "nr_camere": "2", "det_venit": "3", "forma_org": "1",
        "venit_brut": 0, "cheltuieli": 0, "judet": "12", "localitate": "Cluj"},
        "fisa": {"localitate": "Cluj", "judet": "12", "adr_imobil": "Str X 1", "mediu_imobil": "1",
                 "acces_imobil": "1", "camere": [{"supraf": 25.5, "nrloc": 2}, {"supraf": 30, "nrloc": 3}]}}
    x2, _ = d220.genereaza(_P(), "s", Perioada(2018), caz)
    rez = duk.valideaza(x2, "d220", an=2018, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
