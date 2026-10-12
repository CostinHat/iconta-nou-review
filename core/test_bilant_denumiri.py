# -*- coding: utf-8 -*-
"""GARD — deficiența 227 (comanda Costin 12.10.2026, verbatim în DECIZII): „la completarea manuală a coloanei «An precedent» din bilanț,
fiecare rând arată denumirea de pe formular, nu doar «rândul 41».”

SURSA denumirilor: documentul de STRUCTURĂ ANAF al formularelor de bilanț 2025 (`anaf_surse/structura_SC_1225_270126.pdf`, „Structura”
de pe pagina S1002-S1003-S1004-S1005 / 2025, static.anaf.ro), extras de `scripts/extrage_denumiri_bilant.py` în `core/bilant_denumiri.py`.
Codul câmpului `F10_0081` = rândul 08, coloana 1 („IV. CASA ȘI CONTURI LA BĂNCI”). Nimic scris de mână: modulul generat = extragerea."""
import os
import sys

from core import bilant as _b, bilant_api as ba
from core.bilant_denumiri import NOMENCLATOR_DENUMIRI

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import extrage_denumiri_bilant as ex  # noqa: E402


def test_modulul_generat_e_extragerea_din_structura_anaf():
    """MUTAȚIE: o denumire schimbată de mână în `core/bilant_denumiri.py` -> pică (regenerează cu `--scrie`)."""
    assert NOMENCLATOR_DENUMIRI == ex.extrage(), "core/bilant_denumiri.py diferă de extragere — ./venv/bin/python scripts/extrage_denumiri_bilant.py --scrie"


def test_fiecare_rand_de_completat_are_denumirea_lui():
    """Toate rândurile pe care le cere completarea manuală (`randuri_formular`) au o denumire; nicio denumire nu poartă formula de conturi,
    codul altui câmp sau un număr de pagină (resturi ale extragerii). MUTAȚIE: continuarea denumirii luată și din coloana formulei ->
    „F20_0061” în denumirea rândului 01 -> pică."""
    for tip in ("s1005", "s1003"):
        d = ba.denumiri_formular(tip)
        for s, rr in ba.randuri_formular(tip).items():
            assert sorted(d[s]) == rr, (tip, s)
            for r in rr:
                den = d[s][r]
                assert den and "ct." not in den and "F10_" not in den and "F20_" not in den and not den.rstrip().split()[-1].isdigit(), \
                    (tip, s, r, den)


def test_denumirile_sunt_cele_de_pe_formular():
    """Câteva rânduri, fixate pe textul structurii ANAF (citit în `anaf_surse/structura_SC_1225_270126.txt`)."""
    assert NOMENCLATOR_DENUMIRI["s1005"]["F10"][8] == "IV. CASA ȘI CONTURI LA BĂNCI"                        # F10_0081 (rd.08)
    assert NOMENCLATOR_DENUMIRI["s1005"]["F10"][41] == "V. PROFITUL SAU PIERDEREA EXERCITIULUI REPORTAT(A) — SOLD C"   # F10_0411, sub grupa ei
    assert NOMENCLATOR_DENUMIRI["s1005"]["F20"][1] == "1.Cifra de afaceri netă"                             # F20_micro, F20_0011
    assert NOMENCLATOR_DENUMIRI["s1003"]["F20"][4] == "Reduceri comerciale acordate"                        # F20 (rd.1-70), F20_0041
    # [C10] S1003 F20 = denumirile FORMULARULUI (soft A 2025); rd.33 în structură era o copie a lui 11.6
    assert NOMENCLATOR_DENUMIRI["s1003"]["F20"][33] == "11.2. Cheltuieli cu redevențele, locațiile de gestiune și chiriile"
    assert NOMENCLATOR_DENUMIRI["s1003"]["F20"][8] == "2. Venituri aferente costului producției în curs de execuție — Sold D"
    assert NOMENCLATOR_DENUMIRI["s1003"]["F10"] == NOMENCLATOR_DENUMIRI["s1005"]["F10"]                                 # F10_BS e comun S1003 / S1005


def test_randurile_validate_poarta_denumirea_dupa_formular():
    """Tabelul „Ce se depune” (188) arată și denumirea, după formularul din rădăcina XML-ului. MUTAȚIE: denumirea scoasă din
    `randuri_din_xml` -> pică."""
    x5 = '<Bilant1005><F10 F10_0081="7" F10_0082="9"/><F20 F20_0042="3"/></Bilant1005>'
    r = {(x["formular"], x["rand"]): x["denumire"] for x in _b.randuri_din_xml(x5)}
    assert r == {("F10", 8): "IV. CASA ȘI CONTURI LA BĂNCI", ("F20", 4): "4.Cheltuieli cu personalul"}, r
    x3 = x5.replace("Bilant1005", "Bilant1003")
    assert {(x["formular"], x["rand"]): x["denumire"] for x in _b.randuri_din_xml(x3)}[("F20", 4)] == "Reduceri comerciale acordate"


def test_datele_informative_scrise_au_denumire():
    """[C11, 12.10.2026] Rândurile F30 pe care le scrie generatorul (datele informative, cap.I) au denumirea lor din structura ANAF;
    tabelul „Ce se depune” le arată separat de „An precedent” / „An curent”. MUTAȚIE: F30 scos din extragere -> pică."""
    import re
    x = _b.xml_s1005({"cui_numeric": 14399840, "nume": "P"}, 2025, {}, {8: 5}, {}, {8: 5})
    randuri = sorted({int(r) for r in re.findall(r'\bF30_(\d{3})[12]="', x)})
    assert randuri == [1, 2, 3] and all(NOMENCLATOR_DENUMIRI[t]["F30"].get(r) for t in ("s1005", "s1003") for r in randuri), randuri
    assert NOMENCLATOR_DENUMIRI["s1005"]["F30"][1] == "Unităti care au inregistrat profit"
