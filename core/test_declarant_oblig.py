# -*- coding: utf-8 -*-
"""core/test_declarant_oblig.py — GARD: declarantul (nume + functie) e OBLIGATORIU in profil - se cere
EXPLICIT (ca regim_fiscal), nu se fabrica tacit "ADMINISTRATOR".

DEFECT (audit tenant_001, 17.08.2026): declarant_nume/prenume/functie erau CAMPURI_FISCALE dar NU in
firma_profil_api.OBLIGATORII -> ecranul Date firma nu le cerea, iar generatoarele (d100/d101/d205/d112/d300/
bilant) emiteau "ADMINISTRATOR" fabricat cand lipseau (Regula 4). FIX: declarant_nume + declarant_functie in
OBLIGATORII (Date firma le cere in panoul "Profil incomplet" + salveaza_date valideaza) + ob:true in
date_firma.js (g9 pastreaza corespondenta).

TEMEI: Regula 4 (fara valori fabricate) + DS cap.6 (validari preventive). DUK respinge campul declarant gol,
deci se cere EXPLICIT la sursa (profilul firmei), ca regim_fiscal.
"""
from core.firma_profil_api import OBLIGATORII, lipsuri


def test_declarant_in_obligatorii():
    assert "declarant_nume" in OBLIGATORII, "declarant_nume trebuie sa fie obligatoriu (se cere explicit)"
    assert "declarant_functie" in OBLIGATORII, "declarant_functie trebuie sa fie obligatoriu"


def test_lipsuri_semnaleaza_declarantul_lipsa():
    lp = lipsuri({"cui": "123", "nume": "X"})  # profil fara declarant
    camp = {l["camp"] for l in lp}
    assert "declarant_nume" in camp and "declarant_functie" in camp, \
        "panoul Profil incomplet NU semnaleaza declarantul lipsa: %s" % sorted(camp)
    # fiecare blocheaza declaratiile cu declarant (macar D100+D112)
    d = {l["camp"]: l["declaratii"] for l in lp}
    assert "D100" in d["declarant_nume"] and "D112" in d["declarant_functie"]


def test_prenume_nu_e_obligatoriu():
    # prenume are fallback "-" legitim (nu orice declarant are prenume in forma ANAF) - NU se forteaza
    assert "declarant_prenume" not in OBLIGATORII
