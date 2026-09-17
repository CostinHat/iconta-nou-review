# -*- coding: utf-8 -*-
"""[A1, 17.09.2026] Conversia in lei — probe PURE, de la cifra in jos.

Constatarea auditului (A1): facturile in valuta intrau in D300/D394/D390/D406 si in nota (4426/4427)
cu sumele IN VALUTA, fiindca generatoarele citeau `cantitate x pret_unitar` si `total/tva`, nu
`total_lei/curs_bnr`. Masurat: o factura de 1.000 EUR (curs 5) dadea R9_1=1000 in loc de 5000.

Aceste probe PICA pe codul de dinainte de reparatie si TREC dupa. Partea de DB (factura EUR -> nota
in lei -> D300 rd.9 -> D394) e in `core/test_a1_valuta_pana_in_declaratie.py`.
"""
from collections import namedtuple
from decimal import Decimal

import pytest

from core import d300, sume_lei

P = namedtuple("P", "an luna")

_PROF = {"platitor_tva": True, "tip_decont": "L", "nume": "X", "cui": "1",
         "adresa": "a", "oras": "o", "judet": "CJ", "caen": "6202",
         "banca": "BT", "iban": "RO49AAAA1B31007593840000",
         "declarant_nume": "P", "declarant_prenume": "I", "declarant_functie": "a"}


# ── accesorul unic ───────────────────────────────────────────────────────────────────────────
def test_curs_ron_e_unu():
    assert sume_lei.curs_factura({"moneda": "RON"}) == Decimal(1)
    assert sume_lei.curs_factura({}) == Decimal(1)              # absenta monedei = RON
    assert sume_lei.curs_factura({"moneda": None}) == Decimal(1)


def test_curs_valuta_din_document():
    assert sume_lei.curs_factura({"moneda": "EUR", "curs_bnr": Decimal("4.97")}) == Decimal("4.97")


def test_valuta_fara_curs_nu_se_ghiceste_ci_ridica():
    with pytest.raises(sume_lei.LipsaCurs):
        sume_lei.curs_factura({"moneda": "EUR", "id": 7})


def test_baza_lei_scaleaza():
    assert sume_lei.baza_lei(2, 1000, Decimal(5)) == Decimal(10000)


def test_antet_lei_prefera_coloanele_apoi_deriva():
    assert sume_lei.antet_lei({"total_lei": 6050, "tva_lei": 1050}) == (Decimal(6050), Decimal(1050))
    # fara coloane, cu curs -> derivat
    assert sume_lei.antet_lei({"moneda": "EUR", "curs_bnr": 5, "total": 1210, "tva": 210}) == \
        (Decimal(6050), Decimal(1050))


# ── D300: factura EUR intra IN LEI ─────────────────────────────────────────────────────────────
def test_factura_eur_intra_in_lei_in_d300():
    f = {"directie": "emisa", "tert_tara": "RO", "moneda": "EUR", "curs_bnr": 5,
         "total": 1210, "tva": 210, "total_lei": 6050, "tva_lei": 1050,
         "linii": [(1, 1000, 21)]}
    res = d300.calcul_d300(_PROF, P(2026, 8), [f])
    assert res.R.get("R9_1") == 5000, "R9_1 = %r (asteptat 5000 lei = 1000 EUR x 5)" % res.R.get("R9_1")
    assert res.R.get("R9_2") == 1050, "R9_2 = %r (asteptat 1050 lei)" % res.R.get("R9_2")


def test_factura_ron_ramane_neschimbata():
    """Regresie: RON nu se scaleaza (curs 1). Fara asta reparatia ar rupe cazul dominant."""
    f = {"directie": "emisa", "tert_tara": "RO", "moneda": "RON",
         "total": 1210, "tva": 210, "linii": [(1, 1000, 21)]}
    res = d300.calcul_d300(_PROF, P(2026, 8), [f])
    assert res.R.get("R9_1") == 1000
    assert res.R.get("R9_2") == 210


def test_factura_valuta_fara_curs_exclusa_si_semnalata():
    """O factura in valuta fara curs NU intra tacit ca lei; se exclude si se semnaleaza.

    Aserția e pe STRUCTURĂ, nu pe textul mesajului (METODA §23): excluderea = rândul R9_1 rămâne 0
    (factura de 1.000 nu contribuie), iar semnalarea = lista de avertismente e nevidă. O singură
    factură în perioadă, deci singurul avertisment posibil e chiar cel de curs — nu e nevoie să
    potrivim proza lui."""
    fara = {"id": 99, "directie": "emisa", "tert_tara": "RO", "moneda": "EUR",
            "total": 1210, "tva": 210, "linii": [(1, 1000, 21)]}
    res_fara = d300.calcul_d300(_PROF, P(2026, 8), [fara])
    # cu curs, aceeași factură ar da R9_1=5000; fără curs, trebuie EXCLUSĂ -> 0.
    cu = dict(fara, curs_bnr=5)
    assert d300.calcul_d300(_PROF, P(2026, 8), [cu]).R.get("R9_1") == 5000
    assert res_fara.R.get("R9_1", 0) == 0, "factura fara curs n-ar fi trebuit sa intre: R9_1=%r" % res_fara.R.get("R9_1")
    assert len(res_fara.avertismente) >= 1, "excluderea trebuie SEMNALATA; avertismente=%r" % res_fara.avertismente
