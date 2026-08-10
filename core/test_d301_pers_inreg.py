"""Gard pers_inreg (D301) — neconformitate: pers_inreg era hardcodat literal "1".

Sursa oficiala: anaf_surse/d301_struct_anaf.txt poz.15 "pers_inreg:=(1,2)":
  1 = persoana NEinregistrata in scopuri de TVA;
  2 = persoana inregistrata conform art. 317 CF (fost 153^1) NUMAI pentru achizitii IC.

Pe HEAD (6cd0054) build_xml emitea INTOTDEAUNA pers_inreg="1" (literal in format string),
deci calea pers_inreg="2" (art. 317) era imposibila -> test_art317 PICA pe HEAD.
Dupa fix, pers_inreg e CALCULAT din profil (_pers_inreg): marcajul explicit inreg_art317
-> "2", altfel default documentat "1".
"""
import re
from core import d301


def _prof_ok(**extra):
    prof = {"cui": "RO12345678", "nume": "BETA TEST SRL", "banca": "BANCA X",
            "iban": "RO49AAAA1B31007593840000", "adresa": "Str. Test 1",
            "oras": "Bucuresti", "judet": "B"}
    prof.update(extra)
    return prof


def _xml(prof):
    res = d301.calcul_d301(prof, type("P", (), {"an": 2026, "luna": 8})(), [])
    return d301.build_xml(res)


def _pers(xml):
    m = re.search(r'pers_inreg="([^"]*)"', xml)
    assert m, "atribut pers_inreg absent din XML"
    return m.group(1)


def test_neinregistrat_ramane_1():
    # cazul standard: profil fara marcaj art.317 -> "1"
    assert _pers(_xml(_prof_ok())) == "1"


def test_art317_da_2():
    # PICA pe HEAD (pers_inreg era literal "1"); TRECE dupa fix.
    assert _pers(_xml(_prof_ok(inreg_art317=True))) == "2"


def test_valoare_in_nomenclator():
    # N(1) valori admise (1,2) — nicio alta valoare emisa
    assert _pers(_xml(_prof_ok(inreg_art317=True))) in ("1", "2")
    assert _pers(_xml(_prof_ok(inreg_art317=False))) in ("1", "2")
