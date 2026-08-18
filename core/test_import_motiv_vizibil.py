# -*- coding: utf-8 -*-
"""[Regula 6 + Regula 14] GARD: motivul de refuz din preview-ul de IMPORT e VIZIBIL, nu doar in `title`.

Provocarea straturilor de import (Regula 14.4) a scos un tipar: motivul pentru care un rand e marcat ⚠
(CNP invalid la salariati/asociati, avertismentele la mijloace fixe / istoric declaratii) era livrat DOAR
prin atributul `title` -> pe touch (telefon) tooltip-ul nu apare, iar contabilul vede ⚠ fara sa stie DE CE.
Reparat: motivul se randeaza ca text VIZIBIL (span.mig-motiv) langa ⚠, pe toate cele 4 instante (salariati,
asociati, mijloace fixe, istoric). Probat live pe tenant_006 (salariati, bad_sal.csv): "⚠ cifra de control"
/ "⚠ luna invalida" vizibile, title=None, Salveaza dezactivat.
Ratchet pe sursa (fara browser): title-ul purtator-de-motiv NU are voie sa revina; .mig-motiv trebuie sa existe.
"""
import os
import re
import pytest


def _js():
    p = "static/js/ecrane/migrare.js"
    if not os.path.exists(p):
        pytest.skip("migrare.js absent")
    return open(p, encoding="utf-8").read()


def test_motiv_nu_e_title_only():
    """Niciun ⚠ nu-si mai ascunde motivul (cnp_motiv / avertismente / avertisment) DOAR intr-un title."""
    s = _js()
    rele = re.findall(r'title="\$\{[^"]*(?:cnp_motiv|avertismente|avertisment)[^"]*\}"', s)
    assert not rele, "motiv livrat title-only (pierdut pe touch): %s" % rele


def test_motiv_vizibil_prezent():
    """Motivul se randeaza ca text vizibil (span.mig-motiv) - macar cele 4 instante reparate."""
    s = _js()
    n = s.count('class="mig-motiv"')
    assert n >= 4, "asteptam >=4 randari vizibile ale motivului (mig-motiv), gasit %d" % n


def test_mig_motiv_stilizat():
    """Clasa .mig-motiv exista in stil.css (altfel textul vizibil n-are forma DS)."""
    p = "static/stil.css"
    if not os.path.exists(p):
        pytest.skip("stil.css absent")
    assert ".mig-motiv" in open(p, encoding="utf-8").read(), ".mig-motiv lipseste din stil.css"
