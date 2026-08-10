# -*- coding: utf-8 -*-
"""Gard D205 c3 (TEMA T1, CATALOG_INVALIDITATE.md): (tip_venit1+cifR) UNIC per declaratie.

NECONFORMITATE (HEAD 8b74ccb): doi asociati cu ACELASI CNP (toti dividende, tip_venit1=08)
produceau doua sectiuni <benef> cu aceeasi combinatie (08+cifR). Reconcilierea (core/
d205_reconciliere.py) indexeaza beneficiarii intr-un dict pe cheia `cif` ({b.cif: b}), deci a doua
aparitie COLAPSEAZA pe prima si dublura scapa nedetectata -> respinsa abia de DUK regula R41b (
"combinatia 08_<cnp> nu este unica la id_inreg=2"). Structura ANAF "Validari suplimentare" pct.2:
"unicitate (tip_venit1+cifR) pt. tip_venit1#25". Reparat: build_xml detecteaza cifR-uri repetate
si ridica ValueError care numeste CNP-ul, inainte de emitere.

MUTATIE DOVEDITA:
  HEAD 8b74ccb: build_xml emite doua sectiuni <benef> cu acelasi cifR fara sa ridice -> pytest.raises PICA.
  Post-fix: ValueError cu "DUK regula R41b"; CNP-uri distincte raman emise (baseline neatins).
"""
import pytest

from core.d205 import calcul_d205, build_xml

CNP_A = "1750901400191"
CNP_B = "2900101410011"   # CNP distinct valid (persoana diferita, checksum ok)


def _prof():
    return {"cui": "302222000", "nume": "TEST SRL", "adresa": "X"}


def _b(nume, cif):
    return {"categ": "1.a", "nume": nume, "cif": cif,
            "baza": 4000, "imp": 640, "divid_d": 4000, "divid_p": 4000}


def test_doi_beneficiari_cnp_distinct_emisi():
    """Baseline: doi asociati cu CNP-uri DISTINCTE -> ambele sectiuni emise (nrben=2)."""
    res = calcul_d205(_prof(), 2026, [_b("ANA", CNP_A), _b("ION", CNP_B)])
    xml = build_xml(res)
    assert xml.count("<benef ") == 2
    assert 'cifR="%s"' % CNP_A in xml and 'cifR="%s"' % CNP_B in xml


def test_cnp_duplicat_refuzat():
    """MUTATIE c3: acelasi CNP de doua ori (tip_venit1=08). HEAD emite dubla tacit (pytest.raises
    PICA); post-fix ValueError care numeste CNP-ul + DUK R41b."""
    res = calcul_d205(_prof(), 2026, [_b("ANA", CNP_A), _b("ANA (DUP)", CNP_A)])
    assert len(res.beneficiari) == 2
    with pytest.raises(ValueError) as ei:
        build_xml(res)
    msg = str(ei.value)
    assert CNP_A in msg
    assert "apare de 2 ori" in msg
    assert "DUK regula R41b" in msg
