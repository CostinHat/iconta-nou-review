# -*- coding: utf-8 -*-
"""[Regula 6] GARD touch-target (AA 2.5.8, 18.08.2026) - ratchet pe stil.css (fara browser, ruleaza in poarta).

Sweep mobil (Pixel5, frontend_test/vizual/mobil_scan.py) pe cele 5 ecrane a scos tinte de atingere sub pragul
AA 2.5.8 = 24px CSS px, standardul ADOPTAT de proiect (precedent: subbara-edu ridicat 18->24). Reparate app-wide:
  - .fir-veriga (breadcrumb din antetul ORICAREI ferestre) era 19px inaltime / 21px latime -> min 24px;
  - .ajutor-btn (butonul contextual "?") era 20x20 -> 24x24;
  - controalele copil-DIRECT ale unei ferestre largi (.fer-larg .fereastra-corp = flex column) erau strivite
    de un frate inalt (lista) prin flex-shrink pana la inaltimea continutului (dovedit: #pc-cauta 40->20px)
    -> flex-shrink:0 pe input/select/textarea copil-direct.
Proba reala (0 tinte <24px pe cele 5 ecrane): rularea sub24 din frontend_test/vizual. Geaman cu test_a11y_contrast_tokens.
"""
import os
import re
import pytest


def _css():
    p = "static/stil.css"
    if not os.path.exists(p):
        pytest.skip("stil.css absent")
    return open(p, encoding="utf-8").read()


def test_fir_veriga_tinta_24():
    """Breadcrumb-ul (.fir-veriga) - tinta de atingere >=24px pe ambele dimensiuni."""
    s = _css()
    assert "min-height: 24px" in s and ".fir-veriga" in s, "fir-veriga fara min-height 24px"
    assert re.search(r"\.fir-veriga\s*\{[^}]*min-width:\s*24px", s), "fir-veriga fara min-width 24px"


def test_ajutor_btn_24():
    """Butonul contextual '?' (.ajutor-btn) e 24x24, nu 20x20."""
    s = _css()
    m = re.search(r"\.ajutor-btn\s*\{([^}]*)\}", s)
    assert m, ".ajutor-btn negasit"
    assert "width:24px" in m.group(1) and "height:24px" in m.group(1), ".ajutor-btn nu e 24x24: %s" % m.group(1)[:80]
    assert "width:20px" not in m.group(1), ".ajutor-btn inca 20px (regresie)"


def test_control_copil_direct_nu_e_strivit_in_fer_larg():
    """Controalele copil-direct ale unui .fer-larg .fereastra-corp (flex column) au flex-shrink:0 -> nu se
    strivesc vertical cand un frate (lista) e inalt."""
    s = _css()
    assert re.search(r"\.fereastra\.fer-larg\s+\.fereastra-corp\s*>\s*input[^{]*\{[^}]*flex-shrink:\s*0", s), \
        "lipseste flex-shrink:0 pe inputurile copil-direct din fereastra larga (bug #pc-cauta poate reveni)"
