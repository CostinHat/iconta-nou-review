"""Teste D110 (regularizare/restituire impozit pe venit retinut la sursa).
Structura din validatorul oficial (D110Validator.jar, v0/namespace :v1) + semantica din anaf_surse
(structura_D110_2026_240326 + d110_20260330.xsd). nr_evid: control = suma primelor 21 cifre % 100
(CONFIRMAT empiric pe DUKIntegrator). Proba pe DUKIntegrator -v D110."""
import os
import pytest
from core import d110
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D110Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self):
        return ("TEST SRL", "14399840", "Str Exemplu 1", "Bucuresti", "B", "POPESCU", "ION", "ADMIN",
                "021", "t@t.ro", "RO49AAAA1B31007593840000", "Banca Test")


def test_d110_dif_si_total():
    """dif_plata=suma_dat-suma_rest daca >=0 (altfel dif_rest); totalPlata_A=sum(dif_plata+dif_rest)."""
    c = d110.calcul_d110(6, 2025, {"obligatii": [
        {"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1},        # plata: dif_plata=999
        {"cod_oblig": "605", "suma_dat": 200, "suma_rest": 500}]})     # restituire: dif_rest=300
    o1, o2 = c["obligatii"]
    assert o1["dif_plata"] == 999 and o1["dif_rest"] == 0
    assert o2["dif_plata"] == 0 and o2["dif_rest"] == 300
    assert c["totalPlata_A"] == 999 + 300 and c["sigma_dif_rest"] == 300


def test_d110_nr_evid_control_si_cod_bugetar():
    """nr_evid 23 caractere, control = suma primelor 21 cifre % 100; cod_bugetar 5503XXXXXX (629 -> 20A031800X)."""
    c = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1}]})
    ne = c["obligatii"][0]["nr_evid"]
    assert len(ne) == 23
    assert int(ne[-2:]) == sum(int(x) for x in ne[:21]) % 100
    assert c["obligatii"][0]["cod_bugetar"] == "5503XXXXXX"
    c629 = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "629", "suma_dat": 100, "suma_rest": 1}]})
    assert c629["obligatii"][0]["cod_bugetar"] == "20A031800X"


def test_d110_erori():
    prof = {"cui": "14399840", "den": "F", "adresa": "A", "declarant_nume": "N",
            "declarant_prenume": "P", "declarant_functie": "F"}
    # suma_rest <= 0
    c = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "604", "suma_dat": 100, "suma_rest": 0}]})
    assert any("suma_rest" in e for e in d110.erori_generare(prof, {"obligatii": [
        {"cod_oblig": "604", "suma_dat": 100, "suma_rest": 0}]}, c))
    # cod_oblig invalid
    c2 = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "999", "suma_dat": 100, "suma_rest": 1}]})
    assert any("nomenclator" in e for e in d110.erori_generare(prof, {"obligatii": [
        {"cod_oblig": "999", "suma_dat": 100, "suma_rest": 1}]}, c2))
    # d_temei=1 fara IBAN
    prof_no_iban = dict(prof)
    m = {"d_temei": 1, "obligatii": [{"cod_oblig": "605", "suma_dat": 100, "suma_rest": 500}]}
    c3 = d110.calcul_d110(6, 2025, m)
    assert any("IBAN" in e for e in d110.erori_generare(prof_no_iban, m, c3))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D110 nu e instalat in DUK.")
def test_d110_valid_pe_validatorul_oficial():
    from core import duk
    x0, _ = d110.genereaza(_P(), "s", Perioada(2025, luna=6),
                           {"obligatii": [{"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1}]})
    assert duk.valideaza(x0, "d110", an=2025, luna=6)["stare"] == "valid"
    x1, _ = d110.genereaza(_P(), "s", Perioada(2025, luna=6),
                           {"d_temei": 1, "obligatii": [{"cod_oblig": "605", "suma_dat": 200, "suma_rest": 500}]})
    rez = duk.valideaza(x1, "d110", an=2025, luna=6)
    assert rez["stare"] == "valid", rez.get("erori")
