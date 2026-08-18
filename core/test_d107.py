"""Teste D107 (informativa beneficiari sponsorizari / mecenat / burse private).
Structura din validatorul oficial (D107Validator.jar, v1 in vigoare pentru an sfarsit exercitiu >=2024) +
semantica din anaf_surse (structura_D107_2024_010726 + D107_XML_2024_010726, OPANAF 355/2024).
Proba pe DUKIntegrator -v D107."""
import os
import pytest
from core import d107

_JAR = "/home/costin/duk/dist/lib/D107Validator.jar"


class _P:
    """firma_profil WHERE id=1 -> (nume, cui, adresa, oras, judet, regim_fiscal, decl_nume, decl_prenume,
    decl_functie, telefon, email)."""
    _row = ("SPONSOR SRL", "14399840", "Str Test 1", "Bucuresti", "B", "profit",
            "POPESCU", "ION", "ADMINISTRATOR", "0211234567", "t@t.ro")

    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self): return self._row


class _Pmicro(_P):
    _row = ("MICRO SRL", "14399840", "Str M 1", "Cluj", "CJ", "micro",
            "ION", "GHEORGHE", "ADMINISTRATOR", None, None)


def _manual():
    return {"beneficiari": [
        {"den": "Asociatia Alfa", "cif": "12345674", "adresa": "Str ONG 2 Cluj", "val1": 5000, "val2": 2000, "val3": 3000},
        {"den": "Fundatia Beta", "cif": "45678918", "adresa": "Str ONG 3 Iasi", "val1": 3000, "val2": 0, "val3": 3000}]}


def test_d107_totaluri_si_control():
    """TVal1=sum(Val1); TVal2=sum(Val2)+Val2_NI; TVal3=sum(Val3)+Val3_NI; totalPlata_A=TVal1+TVal2+TVal3 (rd.38-44)."""
    m = dict(_manual(), val2_ni=1500, val3_ni=500)
    c = d107.calcul_d107(m)
    assert c["TVal1"] == 8000            # 5000 + 3000
    assert c["TVal2"] == 2000 + 1500     # sum(val2) + Val2_NI
    assert c["TVal3"] == 6000 + 500      # sum(val3) + Val3_NI
    assert c["totalPlata_A"] == c["TVal1"] + c["TVal2"] + c["TVal3"] == 18000


def test_d107_micro_are_d_PM_2():
    """cod_oblig=121 (micro) -> d_PM=2; profit -> d_PM=1 (impus de validator)."""
    xml_m, _ = d107.genereaza(_Pmicro(), "s", _perioada(2024),
                              {"beneficiari": [{"den": "X", "cif": "45678918", "adresa": "A", "val1": 1000}]})
    assert 'cod_oblig="121"' in xml_m and 'd_PM="2"' in xml_m
    xml_p, _ = d107.genereaza(_P(), "s", _perioada(2024), _manual())
    assert 'cod_oblig="103"' in xml_p and 'd_PM="1"' in xml_p


def test_d107_entit1_legata_de_val2ni():
    """Anexa entit1 (neindividualizati) exista DACA SI NUMAI DACA Val2_NI>0 (struct rd.55)."""
    prof = {"cui": "14399840", "den": "F", "adresa": "A", "declarant_nume": "A", "declarant_prenume": "B"}
    # Val2_NI>0 fara entit1 -> eroare
    m1 = {"beneficiari": [{"den": "X", "cif": "45678918", "adresa": "A", "val1": 1}], "val2_ni": 100}
    assert any("neindividualiza" in e.lower() and "reportat" in e.lower()
               for e in d107.erori_generare(prof, m1))
    # entit1 fara Val2_NI -> eroare
    m2 = {"beneficiari": [{"den": "X", "cif": "45678918", "adresa": "A", "val1": 1}],
          "neindividualizati": [{"den": "Y", "cif": "12345674", "adresa": "A"}]}
    assert any("neindividualiza" in e.lower() for e in d107.erori_generare(prof, m2))


def test_d107_erori():
    prof = {"cui": "14399840", "den": "F", "adresa": "A", "declarant_nume": "A", "declarant_prenume": "B"}
    assert any("un beneficiar" in e for e in d107.erori_generare(prof, {"beneficiari": []}))
    bad = {"beneficiari": [{"den": "X", "cif": "45678918", "adresa": "A", "val1": 1}], "cod_oblig": "999"}
    assert any(("obligați" in e.lower() or "regimul" in e.lower())
               for e in d107.erori_generare(prof, bad))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D107 nu e instalat in DUK.")
def test_d107_valid_pe_validatorul_oficial():
    from core import duk
    m = dict(_manual(), val2_ni=1500, val3_ni=500,
             neindividualizati=[{"den": "Beneficiari colectivi", "cif": "45678918", "adresa": "Diverse"}])
    xml, res = d107.genereaza(_P(), "s", _perioada(2024), m)
    rez = duk.valideaza(xml, "d107", an=2024, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")


def _perioada(an):
    from core.common import Perioada
    return Perioada(an)


def test_d107_erori_fara_nume_interne():
    """Mesajele de eroare sunt in limba contabilului - fara atribute XML / campuri interne."""
    prof = {"cui": "14399840", "den": "F", "adresa": "A", "declarant_nume": "A", "declarant_prenume": "B"}
    interne = ("denE", "cifE", "adrE", "entit1", "Val1", "Val2", "Val3", "Val2_NI", "Val3_NI",
               "TVal1", "cod_oblig", "cod_bug", "d_PM", "totalPlata_A")
    cazuri = [
        {"beneficiari": []},
        {"beneficiari": [{"den": "", "cif": "", "adresa": ""}]},
        {"beneficiari": [{"den": "X", "cif": "45678918", "adresa": "A", "val1": 1}], "val2_ni": 100},
        {"beneficiari": [{"den": "X", "cif": "45678918", "adresa": "A", "val1": 1}], "cod_oblig": "999"},
    ]
    for m in cazuri:
        for e in d107.erori_generare(prof, m):
            for intern in interne:
                assert intern not in e, "mesaj cu nume intern %r: %s" % (intern, e)
