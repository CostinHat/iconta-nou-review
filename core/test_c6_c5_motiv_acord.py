# -*- coding: utf-8 -*-
"""GARD C6 + C5 (audit vizual tenant_003, 16.08.2026).
C6: selectorul de declaratii afisa motiv HARDCODAT fals 'nu se aplica (partida simpla)' pentru orice
declaratie neaplicabila (ex. D301/D390 la un SRL, care tine partida DUBLA), iar motivul REAL (corect,
din neaplicabile_selector) era ascuns in title. Fix: optiunea afiseaza motivul real (neap).
C5: caseta 'Profil incomplet' hardcoda pluralul ('1 campuri obligatorii lipsesc'). Fix: acord singular/plural.
"""
import io


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_c6_dropdown_arata_motivul_real_nu_partida_simpla():
    """RED pe cod vechi: 'nu se aplica (partida simpla)' hardcodat in optiunea disabled."""
    src = _read("static/js/ecrane/declaratii.js")
    assert "nu se aplică (partidă simplă)" not in src, "motiv hardcodat fals '(partida simpla)' in dropdown (C6)"
    # optiunea neaplicabila afiseaza motivul REAL din backend (neap), nu doar in title
    assert 'title="${esc(neap)}">${esc(neap)}</option>' in src, "optiunea neaplicabila nu arata motivul real"


def test_c5_acord_singular_plural_profil_incomplet():
    """RED pe cod vechi: pluralul '${lipsa.length} campuri obligatorii lipsesc' fara ramificare."""
    src = _read("static/js/ecrane/date_firma.js")
    # [lotul 5, 15.10.2026] numeralul trece prin `cate` (cu „de” de la 20); verbul se acordă separat
    assert 'cate(lipsa.length, "c\\u00e2mp obligatoriu", "c\\u00e2mpuri obligatorii")' in src, \
        "fara acord singular/plural la 'Profil incomplet' (C5)"
    assert 'lipsa.length === 1 ? "lipse\\u0219te" : "lipsesc"' in src, "verbul nu se acorda (un camp obligatoriu lipseste)"
