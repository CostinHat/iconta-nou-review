# -*- coding: utf-8 -*-
"""[lotul 11, C100] Auditul de preluare spune soldul cu felul lui („balanță creditor 500,00 lei”), ca refuzul importului aceluiași cont —
nu „balanță -500,00 lei” (semnul calculului ajungea la contabil ca un sold negativ pe 401). O singură formă: `pdf_util.sold`. MUTAȚIE:
`_lei` repus în `constatare_parteneri` -> pică."""
from decimal import Decimal as D

from core import audit_preluare as ap
from core import pdf_util


def test_soldul_se_spune_debitor_sau_creditor():
    assert [pdf_util.sold(v) for v in (D("1234.56"), D("-500"), 0)] == ["debitor 1.234,56 lei", "creditor 500,00 lei", "0,00 lei"]


def test_auditul_spune_soldul_creditor_al_furnizorilor_cu_felul_lui():
    (c,) = ap.constatare_parteneri([{"cont": "401", "suma_parteneri": D("0"), "sold_balanta": D("-500"), "diferenta": D("500"),
                                     "coincide": False}])
    assert c["motiv"] == "Contul 401: parteneri 0,00 lei vs balanță creditor 500,00 lei (diferență 500,00 lei).", c
