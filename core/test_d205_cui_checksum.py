# -*- coding: utf-8 -*-
"""Gard D205 c2 (TEMA T1, CATALOG_INVALIDITATE.md): CUI platitor pre-validat pe CIFRA DE CONTROL
inainte de emitere, nu doar pe non-gol.

NECONFORMITATE (HEAD 8b74ccb): erori_generare verifica DOAR ca CUI-ul e non-gol. Un CUI cu cifra
de control gresita (sau lungime gresita / non-numeric) era emis TACIT in header si respins abia de
DUK (eroare de atribut "cui: CUI invalid"; structura ANAF rand 9 "Verificare cui" -> "ERR - CIF
platitor de venit invalid"). Reparat: build_xml valideaza CUI-ul cu core.identitate.valideaza_cui;
control gresit -> ValueError care da motivul exact.

MUTATIE DOVEDITA:
  HEAD 8b74ccb: build_xml emite CUI-ul cu control gresit fara sa ridice -> pytest.raises PICA.
  Post-fix: ValueError cu motivul ("cifra de control"); CUI-ul valid ramane emis (baseline neatins).
"""
import pytest

from core.d205 import calcul_d205, build_xml

CUI_VALID = "302222000"     # checksum ok (acceptat de DUK)
CUI_BAD_CTRL = "14399841"   # 14399840 e valid; ...41 = cifra de control gresita (respins de DUK)


def _prof(cui):
    return {"cui": cui, "nume": "TEST SRL", "adresa": "X"}


def _benef():
    return [{"categ": "1.a", "nume": "GEORGESCU ANA", "cif": "1750901400191",
             "baza": 8000, "imp": 1280, "divid_d": 8000, "divid_p": 8000}]


def test_cui_valid_ramane_emis():
    """Baseline: CUI valid -> se emite normal, cu CUI-ul in header."""
    res = calcul_d205(_prof(CUI_VALID), 2026, _benef())
    xml = build_xml(res)
    assert 'cui="%s"' % CUI_VALID in xml


def test_cui_checksum_gresit_refuzat():
    """MUTATIE c2: CUI platitor cu cifra de control gresita. HEAD il emite tacit (pytest.raises
    PICA); post-fix ValueError cu motivul exact + referinta la validarea ANAF/DUK a CUI-ului."""
    res = calcul_d205(_prof(CUI_BAD_CTRL), 2026, _benef())
    with pytest.raises(ValueError) as ei:
        build_xml(res)
    msg = str(ei.value)
    assert "CUI plătitor" in msg
    assert CUI_BAD_CTRL in msg
    assert "cifra de control" in msg
    assert "cui: CUI invalid" in msg
