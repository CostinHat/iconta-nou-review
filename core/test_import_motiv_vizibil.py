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
    """[comanda Costin 8.2 pct.4] Motivul se randeaza ca text vizibil intr-un SINGUR loc — tabelul comun al previzualizarilor
    (`tabelPrevizualizare`, coloana „Starea”, div.mig-prev-motiv) — folosit de fiecare import (solduri, parteneri, salariati, asociati,
    mijloace fixe, istoric, RIP, articole, retete)."""
    s = _js()
    corp = s[s.index("function tabelPrevizualizare("):]
    corp = corp[:corp.index("\n}\n")]
    assert corp.count('class="mig-prev-motiv"') == 1, "tabelul comun nu mai arata motivul randului"
    n = s.count("tabelPrevizualizare(") - 1
    assert n >= 9, "asteptam ca fiecare import (9) sa foloseasca tabelul comun, gasit %d" % n


def test_mig_motiv_stilizat():
    """Clasa .mig-prev-motiv exista in stil.css (altfel textul vizibil n-are forma DS)."""
    p = "static/stil.css"
    if not os.path.exists(p):
        pytest.skip("stil.css absent")
    assert ".mig-prev-motiv" in open(p, encoding="utf-8").read(), ".mig-prev-motiv lipseste din stil.css"
