# -*- coding: utf-8 -*-
"""GARD: nota de taxare inversa pentru achizitia intracomunitara e CONSTIENTA de platitor.
(22.09.2026, DECIZII 65 — constatare Sesiunea B F3)

Platitor de TVA (art.316) -> 4426 = 4427 (deductibil). NEplatitor art.317 -> TVA nedeductibila
in COSTUL achizitiei (contul principalului + 446), NU 4426=4427 (ar deduce un TVA nedeductibil,
CF art.297 — cifra valid-dar-falsa in nota si in D100/D406).

Aserteaza pe STRUCTURA (liniile-tuplu ale notei), nu pe textul mentiunii (METODA §23).
MUTATIA care il face rosu (confirmata la scriere): helperul intoarce mereu `[baza, (4426,4427,tva)]`
ignorand `beneficiar_platitor` -> test_neplatitor_* pica (gaseste 4426=4427, nu costul)."""
from decimal import Decimal

from core import intracomunitar as _ic


def _linii(cont, val, tva, platitor):
    linii, _ment = _ic.note_taxare_inversa(cont, val, tva, platitor)
    return linii


def test_platitor_deduce_4426_4427():
    linii = _linii("371", 5000, 1050, True)
    assert ("4426", "4427", Decimal("1050")) in linii
    assert ("371", "446", Decimal("1050")) not in linii


def test_neplatitor_tva_in_costul_achizitiei_nu_deduce():
    linii = _linii("371", 5000, 1050, False)
    assert ("371", "446", Decimal("1050")) in linii            # TVA in costul achizitiei (cont+446)
    assert ("4426", "4427", Decimal("1050")) not in linii      # NU se deduce


def test_baza_pe_cont_401_indiferent_de_platitor():
    for platitor in (True, False):
        assert ("628", "401", Decimal("2500")) in _linii("628", 2500, 525, platitor)
