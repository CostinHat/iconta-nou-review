# -*- coding: utf-8 -*-
"""GARDĂ pentru interdicția 60 — elementul care implementează o normă îi poartă articolul?

Planul numește 60 *„cea mai mare din fază, și cea mai valoroasă"*, și spune că partea grea e
**numitorul**: nu „câte au temei", ci *câte elemente care implementează o normă există*.

CALIBRAT PE CELE TREI LEGĂTURI PE CARE PLANUL LE NUMEȘTE CUNOSCUTE. Dacă scanul nu le clasifică așa,
e rupt — și a fost: prima formă căuta `Temei` doar **în corpul funcției** și rata tiparul de versionare
al proiectului, în care temeiul stă în registrul de variante (`_VARIANTE_X = [(dată, funcție,
Temei(...))]`). Adică rata chiar cazul de calibrare — deducerea personală ↔ art. 77 alin. (4).
`graf_temei` a avut de tratat special același tipar; nu e o excepție, e convenția casei.
"""
import pytest

from core import scan_norma_implementare as sn


@pytest.fixture(scope="module")
def harta():
    return {(f, n): tr for f, _c, n, tr in sn.inventar()}


def test_deducerea_personala_e_structurat(harta):
    """CAZ CUNOSCUT 1: formula deducerii ↔ art. 77 alin. (4), prin registrul de variante."""
    assert harta.get(("salarizare.py", "_deducere_personala_2018")) == "STRUCTURAT", (
        "temeiul atașat prin `_VARIANTE_*` nu e văzut — scanul s-a întors la a-l căuta doar în corp")


def test_calculul_salariului_e_structurat(harta):
    """CAZ CUNOSCUT 2: podeaua part-time ↔ art. 146(5^6) / 168(6^1), tot prin registru."""
    assert harta.get(("salarizare.py", "_calcul_salariu_2018")) == "STRUCTURAT"


def test_nomenclatorul_codurilor_e_proza(harta):
    """CAZ CUNOSCUT 3: nomenclatorul indemnizațiilor ↔ documentul de structură — legătura există, dar
    ca PROZĂ (rândul 98 din `d112_struct_anaf.txt`), nu ca obiect. Treapta trebuie să spună asta."""
    assert harta.get(("nomenclator_cm.py", "CODURI")) == "PROZA", (
        "dacă iese STRUCTURAT, scanul confundă proza cu obiectul; dacă iese NIMIC, nu vede citarea")


def test_cele_trei_trepte_sunt_toate_populate(harta):
    """ANTI-VACUU pe fiecare treaptă. O treaptă goală înseamnă că discriminatorul s-a rupt, iar
    procentele de mai jos ar deveni o afirmație despre nimic."""
    import collections
    c = collections.Counter(harta.values())
    for tr in ("STRUCTURAT", "PROZA", "NIMIC"):
        assert c[tr] > 0, "treapta %s e goală — clasificarea s-a rupt" % tr
    assert sum(c.values()) >= 300, "numitorul a căzut la %d — categoriile nu mai prind" % sum(c.values())


def test_categoriile_declarate_produc_toate_elemente():
    """Fiecare categorie din numitor trebuie să prindă ceva. Una goală = proxy greșit, nu lume goală."""
    import collections
    per = collections.Counter(c for _f, c, _n, _t in sn.inventar())
    for cat in ("formula", "structura", "nomenclator", "termen", "validare"):
        assert per[cat] > 0, "categoria %s nu prinde niciun element — proxy-ul ei e greșit" % cat


def test_clichet_pe_legatura_structurata(harta):
    """Numărul de legături verificabile MECANIC nu are voie să scadă tăcut.

    Măsurat 23.08.2026: 17 din 470. E o cifră mică — 4% — și tocmai de aceea se pinează: o legătură
    structurată rescrisă în proză ar trece neobservată."""
    n = sum(1 for v in harta.values() if v == "STRUCTURAT")
    assert n >= 17, "legături structurate: %d, sub clichetul de 17 măsurat pe 23.08" % n
