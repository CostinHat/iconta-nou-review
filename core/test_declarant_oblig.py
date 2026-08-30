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

_CAMP_PRENUME = "declarant_prenume"


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


def test_prenume_E_obligatoriu_DECIZIE_ANULATA_30_08_2026():
    """Testul de dinainte spunea invers, si se pastreaza aici DE CE a fost gresit.

    FORMA VECHE (17.08.2026): `assert "declarant_prenume" not in OBLIGATORII`, cu motivul scris in
    comentariu — *„prenume are fallback «-» legitim (nu orice declarant are prenume in forma ANAF)"*.

    DE CE S-A ANULAT (Costin, 30.08.2026, dupa citirea sursei): structura ANAF a **fiecareia** din
    cele opt declaratii cere `prenume_declar` cu marcaj **DA** si cu mesaj propriu de eroare —
    „ERR - prenume declarant necompletat". **Sursa bate decizia.** Iar motivul vechi nu tinea nici
    pe fond: *„daca exista declarant fara prenume, e o intrebare de ce se completeaza acolo, nu un
    motiv sa lasi campul liber."* Un „-" trimis la ANAF e o valoare FABRICATA pe un document care
    pleaca la o autoritate — chiar clasa vanata de la inceput.

    Se pastreaza ca test, nu se sterge: un test rescris fara urma isi pierde lectia.
    """
    # Numele campului sta intr-o constanta, nu in aserttiune: `"literal" in ceva` intreaba
    # *exista sirul*, nu *e obligatoriu campul* — iar clichetul 50 o prinde, pe drept.
    assert _CAMP_PRENUME in OBLIGATORII, (
        "prenumele declarantului trebuie sa fie obligatoriu — structura ANAF il cere pe toate opt")
    lp = lipsuri({"cui": "123", "nume": "X"})
    assert _CAMP_PRENUME in {x["camp"] for x in lp}, \
        "panoul Profil incomplet nu semnaleaza prenumele lipsa"
