"""Teste D104 (distribuire intre asociati a veniturilor/cheltuielilor - asocieri fara personalitate juridica).
Structura din validatorul oficial (D104Validator.jar, v0/namespace :v1) + semantica din anaf_surse
(structura_D104_2012_v100_030613 + d104.xsd, OPANAF 1950/2012). Proba pe DUKIntegrator -v D104."""
import os
import pytest
from core import d104
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D104Validator.jar"


class _P:
    _row = ("ASOCIEREA TEST", "14399840", "Str Exemplu 1", "Bucuresti", "B",
            "POPESCU", "ION", "ADMINISTRATOR", "0212345678", "test@ex.ro")

    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self): return self._row


def _manual():
    return {"profit_pierd": 40000, "asociati": [
        {"den": "Asociat Unu SRL", "cif": "12345674", "adresa": "Bucuresti", "cota": 60,
         "venit": 60000, "chelt": 36000, "imp_datorat": 3840, "imp_declarat": 3000},
        {"den": "Asociat Doi", "cif": "45678918", "adresa": "Cluj", "cota": 40,
         "venit": 40000, "chelt": 24000, "imp_datorat": 2560, "imp_declarat": 2000}]}


def test_d104_totaluri_definitivare():
    """luna=12: Tven=Σventit; TimpD=ΣimpD; difPR=impD-impR; totalPlata_A=profit_pierd+TimpD+TimpR+TdifP+TdifR."""
    c = d104.calcul_d104(12, _manual())
    assert c["Tven"] == 100000 and c["Tchelt"] == 60000
    assert c["TimpD"] == 6400 and c["TimpR"] == 5000
    assert c["TdifP"] == 1400 and c["TdifR"] == 0          # 840 + 560
    assert c["SB"][0]["difPR"] == 840                       # impD-impR la luna 12
    assert c["totalPlata_A"] == 40000 + 6400 + 5000 + 1400 + 0 == 52800


def test_d104_trimestru_impR_si_difpr_zero():
    """luna in {3,6,9}: impR=0 si difPR=0 (R32_2/R33_2), oricat ar da manualul."""
    c = d104.calcul_d104(3, _manual())
    assert all(s["impR"] == 0 for s in c["SB"])
    assert all(s["difPR"] == 0 for s in c["SB"])
    assert c["TimpR"] == 0 and c["TdifP"] == 0 and c["TdifR"] == 0


def test_d104_erori():
    prof = {"cui": "14399840", "den": "A", "adresa": "X", "declarant_nume": "N",
            "declarant_prenume": "P", "declarant_functie": "F"}
    # fara asociati + fara profit_pierd
    assert any("un asociat" in e for e in d104.erori_generare(prof, 12, {"profit_pierd": 0}))
    assert any("profit_pierd" in e for e in d104.erori_generare(prof, 12, {"asociati": [
        {"den": "X", "cif": "12345674", "cota": 100}]}))
    # cota invalida
    assert any("cota" in e for e in d104.erori_generare(prof, 12, {"profit_pierd": 0, "asociati": [
        {"den": "X", "cif": "12345674", "cota": 150}]}))
    # cif duplicat
    dup = {"profit_pierd": 0, "asociati": [
        {"den": "A", "cif": "12345674", "cota": 50}, {"den": "B", "cif": "12345674", "cota": 50}]}
    assert any("duplicat" in e for e in d104.erori_generare(prof, 12, dup))
    # luna invalida
    assert any("luna" in e for e in d104.erori_generare(prof, 5, _manual()))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D104 nu e instalat in DUK.")
def test_d104_valid_pe_validatorul_oficial():
    from core import duk
    xml, res = d104.genereaza(_P(), "s", Perioada(2024, trim=4), _manual())
    rez = duk.valideaza(xml, "d104", an=2024, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
    x2, _ = d104.genereaza(_P(), "s", Perioada(2024, trim=1),
                           {"profit_pierd": 10000, "asociati": [
                               {"den": "A", "cif": "12345674", "adresa": "B", "cota": 100,
                                "venit": 30000, "chelt": 20000, "imp_datorat": 1600, "imp_declarat": 999}]})
    rez2 = duk.valideaza(x2, "d104", an=2024, luna=3)
    assert rez2["stare"] == "valid", rez2.get("erori")
