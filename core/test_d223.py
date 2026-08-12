"""Teste D223 (venituri estimate pentru asocieri fara personalitate juridica / transparenta fiscala).
Structura din validatorul oficial (D223Validator.jar, v0/namespace :v1) + semantica din anaf_surse
(structura_D223_2016_050116_13012016 + d223_20160113.xsd, OPANAF 184/2013). Proba pe DUKIntegrator -v D223."""
import os
import pytest
from core import d223
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D223Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self):
        return ("ASOC X", "14399840", "Str A 1", "Otopeni", "IF", "POPESCU", "ION", "ADMIN", "021", "a@b.ro")


def _manual():
    return {"asociere": {"nume": "ASOCIEREA EXEMPLU", "cif": "14399840", "adresa": "Str Exemplu 1 Otopeni"},
            "responsabil": {"den_r": "Popescu Ion", "cif_r": "12345674", "adresa_r": "Str Exemplu 1"},
            "activitate": {"categ_venit": "1", "forma_org": "2", "det_venit": "1", "caen": "4711",
                           "judet": "23", "localitate": "Otopeni", "sediu": "Str Exemplu 1",
                           "nr_contr": "1", "data_contr": "01.01.2020", "venit_brut": 100000, "cheltuieli": 40000},
            "asociati": [{"nume_d": "Popescu Ion", "cif_d": "1800101412340", "dom_d": "Str X", "cota_d": 60},
                         {"nume_d": "Ionescu Maria", "cif_d": "2850312400073", "dom_d": "Str Y", "cota_d": 40}]}


def test_d223_distributie_si_totaluri():
    """net3=venit3-chelt3; totalPlata_A=venit3+chelt3+net3; venit_d distribuit dupa cota_d, suma=net3."""
    c = d223.calcul_d223(_manual())
    assert c["net3"] == 60000 and c["totalPlata_A"] == 200000
    assert sum(s["venit_d"] for s in c["asociati"]) == 60000     # suma distribuita = net3
    assert c["asociati"][0]["venit_d"] == 36000                  # 60% din 60000
    assert c["nr_asoc"] == 2


def test_d223_norma_venit_d_zero():
    """det_venit=3 (norma): venit_d = 0 pentru toti asociatii."""
    m = dict(_manual())
    m["activitate"] = dict(m["activitate"], det_venit="3")
    c = d223.calcul_d223(m)
    assert all(s["venit_d"] == 0 for s in c["asociati"])


def test_d223_erori():
    prof = {"declarant_nume": "N", "declarant_prenume": "P", "declarant_functie": "F"}
    m = _manual()
    # cota nu insumeaza 100
    bad = dict(m, asociati=[{"nume_d": "A", "cif_d": "1800101412340", "dom_d": "X", "cota_d": 60},
                            {"nume_d": "B", "cif_d": "2850312400073", "dom_d": "Y", "cota_d": 30}])
    assert any("100" in e for e in d223.erori_generare(prof, bad))
    # lipsa responsabil
    m2 = dict(m); m2 = {k: v for k, v in m.items() if k != "responsabil"}
    assert any("responsabil" in e for e in d223.erori_generare(prof, m2))
    # fara asociati
    m3 = dict(m, asociati=[])
    assert any("asociat" in e for e in d223.erori_generare(prof, m3))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D223 nu e instalat in DUK.")
def test_d223_valid_pe_validatorul_oficial():
    from core import duk
    xml, res = d223.genereaza(_P(), "s", Perioada(2024), _manual())
    rez = duk.valideaza(xml, "d223", an=2024, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
