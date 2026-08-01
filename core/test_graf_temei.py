# -*- coding: utf-8 -*-
"""Graful de dependente fiscale extras din cod (core/graf_temei.py, Modelul de temei 01.08 pct.3).

Proba ceruta de Costin: interogarea salariu_minim trebuie sa contina functiile care aplica minimul
(deducere_personala, facilitate, plafon 12 sm, suprataxare part-time, prag tineri). Daca lipseste
vreuna, extractia nu vede ceva - se spune ce si de ce."""
from core.graf_temei import construieste_graf, depinde_de


def test_depinde_de_salariu_minim_acopera_clusterul():
    """deducere_personala (scara degresiva + prag tineri) + calcul_salariu (facilitate + plafon 12 sm +
    suprataxare part-time) - AMBELE direct. Cele 4 sub-concepte NU sunt functii separate: traiesc IN
    aceste doua functii, deci graful le vede PRIN ele. Extractie completa la nivel de functie."""
    dep = depinde_de("salariu_minim")
    assert "deducere_personala" in dep, "deducerea (dispecer) nu apare"  # prin varianta _deducere_personala_2018
    assert dep.get("_deducere_personala_2018") == "direct", "varianta deducerii nu apare direct"
    # calcul_salariu e acum dispecer versionat (PAS 3): logica (cota salariu_minim) traieste in varianta
    # datata _calcul_salariu_2018 -> dispecerul depinde TRANZITIV (prin varianta), varianta DIRECT.
    assert "calcul_salariu" in dep, "calcul_salariu (dispecer) nu apare"
    assert dep.get("_calcul_salariu_2018") == "direct", "varianta calcul_salariu (facilitate/plafon12sm/suprataxare) nu apare direct"


def test_calcul_salariu_contine_sub_conceptele():
    """DOVADA ca cele 4 sub-concepte sunt in variantele datate _calcul_salariu_2018/_deducere_personala_2018
    (nu functii separate, deci graful le acopera prin functia-gazda): _calcul_salariu_2018 cere DIRECT
    salariu_minim + facilitate + plafonul facilitatii; _deducere_personala_2018 cere salariu_minim."""
    g = construieste_graf()
    cote_cs = g["_calcul_salariu_2018"]["cote"]
    assert "salariu_minim" in cote_cs               # suprataxare part-time, plafon 12 sm
    assert "facilitate_salariu_minim" in cote_cs    # facilitate
    assert "plafon_facilitate_salariu_minim" in cote_cs
    assert "salariu_minim" in g["_deducere_personala_2018"]["cote"]   # prag tineri (in varianta datata)


def test_inchidere_tranzitiva_prinde_consumatorii():
    """Cine apeleaza calcul_salariu/deducere_personala depinde TRANZITIV de salariu_minim (d112, fluturas,
    note lunare) - asta e valoarea grafului: la o schimbare a minimului, lista completa de locuri afectate."""
    dep = depinde_de("salariu_minim")
    tranzitive = [n for n, v in dep.items() if v.startswith("prin")]
    assert tranzitive, "inchiderea tranzitiva nu prinde niciun consumator"
    assert len(dep) > 5, "prea putine dependente - extractia rateaza ceva"


def test_graf_reflecta_codul_nu_o_lista_manuala():
    """O functie care NU cheama cota() nu apare ca dependenta directa - graful reflecta codul de azi
    (prin constructie), nu o lista scrisa de mana care devine stale."""
    dep = depinde_de("tva_standard")
    # facturi.calcul_tva / d394 folosesc tva prin cota() -> apar; o functie de rotunjire (_q) NU
    g = construieste_graf()
    assert "_q" not in {n for n, d in g.items() if "tva_standard" in d["cote"]}
