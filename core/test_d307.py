"""Teste D307 (ajustare/corectie/regularizare TVA).
Structura din validatorul oficial (D307Validator.jar, v0/namespace :v1) + semantica din anaf_surse
(structura_D307_2017_071117 + d307_20171205.xsd, OPANAF 793/2016). Proba pe DUKIntegrator -v D307."""
import os
import pytest
from core import d307
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D307Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self):
        return ("ZTEST SRL", "14399840", "Str Exemplu 1", "Bucuresti", "B", "POPESCU", "ION", "ADMIN",
                "021", "t@t.ro")


def _manual():
    return {"operatiuni": [
        {"tip": "A", "cod": "12345674", "den": "Cedent Active SRL", "tva": 1000},
        {"tip": "L", "cod": "45678918", "den": "Finantator SRL", "tva": 500},
        {"tip": "C", "cod": "14399840", "den": "Beneficiar SRL", "tva": -200}]}


def test_d307_sume_control():
    """tvaA/tvaL/tvaC = suma tva pe tip; totalPlata_A = suma tva (poate include valori <=0)."""
    c = d307.calcul_d307(_manual())
    assert c["tvaA"] == 1000 and c["tvaL"] == 500 and c["tvaC"] == -200
    assert c["totalPlata_A"] == 1300


def test_d307_erori():
    prof = {"cui": "14399840", "den": "F", "adresa": "A", "declarant_nume": "N",
            "declarant_prenume": "P", "declarant_functie": "F"}
    assert any("operațiune" in e for e in d307.erori_generare(prof, {"operatiuni": []}))
    bad = {"operatiuni": [{"tip": "X", "cod": "12345674", "den": "Y", "tva": 1}]}
    assert any("tip" in e for e in d307.erori_generare(prof, bad))
    # d_anulare=1 fara temei
    anul = {"d_anulare": "1", "operatiuni": [{"tip": "C", "cod": "14399840", "den": "Y", "tva": 1}]}
    assert any("temei" in e for e in d307.erori_generare(prof, anul))
    # [mesaj_contabil] Regula 14.4: niciun nume intern XSD in textul aratat contabilului
    prof_gol = {"cui": "14399840", "den": "F", "adresa": "A"}   # fara declarant -> mesaj declarant
    for pf, mc in ((prof, {"operatiuni": []}), (prof, anul), (prof_gol, {"operatiuni": [{"tip": "A", "cod": "1", "den": "Y", "tva": 1}]})):
        for e in d307.erori_generare(pf, mc):
            for intern in ("denO", "codO", "operatiuni[", "declarant_nume", "declarant_prenume", "d_anulare", "temei=", "%r"):
                assert intern not in e, "mesajul expune numele intern %r: %s" % (intern, e)


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D307 nu e instalat în DUK.")
def test_d307_valid_pe_validatorul_oficial():
    from core import duk
    xml, res = d307.genereaza(_P(), "s", Perioada(2026, luna=7), _manual())
    assert duk.valideaza(xml, "d307", an=2026, luna=7)["stare"] == "valid"
    # d_anulare=1 cu temei
    x2, _ = d307.genereaza(_P(), "s", Perioada(2026, luna=7),
                           {"d_anulare": "1", "temei": "1",
                            "operatiuni": [{"tip": "C", "cod": "14399840", "den": "Benef", "tva": 300}]})
    rez = duk.valideaza(x2, "d307", an=2026, luna=7)
    assert rez["stare"] == "valid", rez.get("erori")
