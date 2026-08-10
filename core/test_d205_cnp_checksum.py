# -*- coding: utf-8 -*-
"""Gard D205 c1 (TEMA T1, CATALOG_INVALIDITATE.md): CNP beneficiar pre-validat pe CIFRA DE
CONTROL inainte de emitere, nu doar pe forma.

NECONFORMITATE (HEAD 8b74ccb): `_cnp_rezident` verifica INTENTIONAT doar forma (13 cifre, prima
1-8) pentru a deriva rezidenta; un CNP rezident cu cifra de control gresita era emis TACIT si
respins abia de DUK regula R29 ("cif1(<cnp>) este invalid"). Reparat: dupa derivarea rezidentei,
daca beneficiarul e rezident (CNP-shaped) se valideaza checksum-ul cu core.identitate.valideaza_cnp;
control gresit -> ValueError care numeste beneficiarul + R29. Refuzul de NEREZIDENT (prefix-9 / cod
strain, R32) ramane neatins - checksum-ul il COMPLETEAZA doar pentru rezidenti.

MUTATIE DOVEDITA:
  HEAD 8b74ccb: build_xml emite CNP-ul cu control gresit fara sa ridice -> pytest.raises PICA.
  Post-fix: ValueError cu "DUK regula R29"; CNP-ul valid ramane emis (baseline neatins).
"""
import re
import pytest

from core.d205 import calcul_d205, build_xml

# CNP rezident VALID (prima cifra 1, checksum corect - acceptat de DUK) vs. acelasi CNP cu ultima
# cifra schimbata = cifra de control GRESITA (respins de DUK R29), dar tot rezident-shaped.
CNP_VALID = "1750901400191"
CNP_BAD_CTRL = "1750901400190"


def _prof():
    return {"cui": "302222000", "nume": "TEST SRL", "adresa": "X"}  # CUI valid (checksum ok)


def _benef(cif):
    return [{"categ": "1.a", "nume": "GEORGESCU ANA", "cif": cif,
             "baza": 8000, "imp": 1280, "divid_d": 8000, "divid_p": 8000}]


def test_cnp_valid_ramane_emis():
    """Baseline: un beneficiar cu CNP valid (checksum corect) se emite normal."""
    res = calcul_d205(_prof(), 2026, _benef(CNP_VALID))
    xml = build_xml(res)
    assert 'cifR="%s"' % CNP_VALID in xml
    assert 'Rezid="1"' in re.search(r'<benef[^>]*/>', xml).group(0)


def test_cnp_checksum_gresit_refuzat():
    """MUTATIE c1: CNP rezident-shaped cu cifra de control gresita. HEAD il emite tacit
    (pytest.raises PICA); post-fix ValueError care numeste beneficiarul + DUK R29."""
    res = calcul_d205(_prof(), 2026, _benef(CNP_BAD_CTRL))
    assert len(res.beneficiari) == 1
    with pytest.raises(ValueError) as ei:
        build_xml(res)
    msg = str(ei.value)
    assert "CNP invalid" in msg
    assert CNP_BAD_CTRL in msg
    assert "cifra de control" in msg
    assert "DUK regula R29" in msg
