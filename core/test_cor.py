# -*- coding: utf-8 -*-
"""Teste gardian pentru F137 (nomenclator COR).

Apara normalizarea diacriticelor: cautarea COR e diacritic-insensitiva (numele oficiale contin
ă/î/ș/ț, utilizatorul tasteaza fara), comparata pe forma normalizata. O regresie aici = cautari
care nu mai gasesc ocupatia (ex. 'lacatus' nu mai gaseste 'lăcătuș'). Functie PURA.

Parserul (extrage_perechi) + validarea la incarcare (cor_incarca.main: refuza daca nu-s 4422 coduri
unice pe 6 cifre) sunt dovedite functional pe fisierul oficial; datele in DB = integrare.
"""
from core.cor_api import normalizeaza


def test_normalizeaza_diacritice_romanesti():
    assert normalizeaza("lăcătuș") == "lacatus"
    assert normalizeaza("Țesător") == "tesator"
    assert normalizeaza("Învățător") == "invatator"
    assert normalizeaza("șofer") == "sofer"


def test_normalizeaza_minuscule_si_spatii():
    assert normalizeaza("  ASISTENT   Social  ") == "asistent social"


def test_normalizeaza_ambele_forme_sedila():
    # ș/ț cu virgula (U+0219/U+021B) si cu sedila (U+015F/U+0163) -> aceeasi forma
    assert normalizeaza("ș") == "s" and normalizeaza("ş") == "s"
    assert normalizeaza("ț") == "t" and normalizeaza("ţ") == "t"


def test_normalizeaza_gol():
    assert normalizeaza("") == ""
    assert normalizeaza(None) == ""


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn(); print("OK", fn.__name__)
    print("\n%d teste PASS" % len(fns))
