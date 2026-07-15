# -*- coding: utf-8 -*-
"""Teste gardian pentru salarii_contare (partea pura)."""
from decimal import Decimal
from core.salarii_contare import document_ref, _nr_salariati_xml, _d


def test_document_ref_e_idempotent_si_stabil():
    assert document_ref(2026, 6) == "SAL 06/2026"
    assert document_ref(2026, 12) == "SAL 12/2026"


def test_nr_salariati_din_xml():
    xml = '<angajatorB B_cnp="3" B_sanatate="3" B_pensie="3" B_brutSalarii="15000" B_sal="3"/>'
    assert _nr_salariati_xml(xml) == 3


def test_nr_salariati_lipsa_da_zero_nu_crapa():
    assert _nr_salariati_xml("<declaratieUnica/>") == 0


def test_d_trateaza_none_ca_zero():
    assert _d(None) == Decimal("0")
