# -*- coding: utf-8 -*-
"""[Regula 6 + Regula 13] GARD LANDMARKS app-wide (18.08.2026).

Shell-ul SPA (navigator.js) monta tot chrome-ul de sus (bara albastra, subbara "firma in lucru", bara3
motivationala) si toasturile ca frati ai <header>/<main>, iar ferestrele modale in #app in AFARA lui <main>
-> tot continutul lor cadea in afara oricarui landmark (axe "region": 2 noduri pe dashboard, 5 pe fereastra,
8-26 app-wide). Reparat STRUCTURAL, o singura data, in shell-ul comun -> app-wide:
  - un singur <header class="bara-antet"> (banner) inveleste bara+subbara+bara3;
  - fereastra modala are role="dialog" + aria-modal (frontiera de landmark -> continutul ei nu mai e orfan);
  - toastul de bun-venit are role="status" (live region).
Proba reala (0 violari region pe dashboard + cele 5 ECRANE): frontend_test/vizual/scan_region_all.py.
Acest gard e ratchet pe SURSA (fara browser, ruleaza in poarta): daca structura de landmark e desfacuta,
regula axe "region" reapare. Geaman cu core/test_a11y_contrast_tokens.py (citeste stil.css).
"""
import os
import pytest


def _nav():
    p = "static/js/navigator.js"
    if not os.path.exists(p):
        pytest.skip("navigator.js absent")
    return open(p, encoding="utf-8").read()


def test_banner_inveleste_chrome_de_sus():
    """bara+subbara+bara3 stau intr-un SINGUR <header class='bara-antet'> (banner), nu ca frati orfani."""
    s = _nav()
    assert 'antet = document.createElement("header")' in s, "lipseste <header> antet (banner)"
    assert 'antet.className = "bara-antet"' in s, "antet nu are clasa bara-antet"
    for cop in ("bara", "subbara", "bara3"):
        assert 'antet.appendChild(%s)' % cop in s, "%s nu e pus in banner-ul <header>" % cop
    # regresie: chrome-ul NU mai trebuie atasat direct la ecran (ar fi in afara landmark-ului)
    for cop in ("subbara", "bara3"):
        assert 'ecran.appendChild(%s)' % cop not in s, "%s inca se ataseaza la ecran (orfan de landmark)" % cop


def test_bara_nu_e_al_doilea_header():
    """bara e <div> (chrome-ul propriu-zis), nu un al doilea <header> (ar duce la banner duplicat/orfan)."""
    s = _nav()
    assert 'const bara = document.createElement("div")' in s, "bara ar trebui sa fie <div> in banner"
    assert 'const bara = document.createElement("header")' not in s, "bara nu mai are voie sa fie <header>"


def test_main_prezent():
    """Continutul principal ramane intr-un <main> (landmark)."""
    assert 'document.createElement("main")' in _nav(), "lipseste <main> (continut principal)"


def test_fereastra_modala_e_dialog():
    """Fereastra de lucru = dialog modal (frontiera de landmark -> continutul ei nu mai declanseaza region)."""
    s = _nav()
    assert 'fer.setAttribute("role", "dialog")' in s, "fereastra nu are role=dialog"
    assert 'fer.setAttribute("aria-modal", "true")' in s, "fereastra nu are aria-modal"
    assert 'fer.setAttribute("aria-label"' in s, "fereastra-dialog fara nume accesibil (aria-label)"


def test_toast_e_live_region():
    """Toastul de bun-venit are role=status (live region), nu continut orfan intre landmark-uri."""
    s = _nav()
    assert 't.setAttribute("role", "status")' in s, "toastul sumar-login nu e live region (role=status)"
