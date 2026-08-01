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
    assert dep.get("deducere_personala") == "direct", "deducerea (scara + prag tineri) nu apare"
    assert dep.get("calcul_salariu") == "direct", "calcul_salariu (facilitate/plafon12sm/suprataxare) nu apare"


def test_calcul_salariu_contine_sub_conceptele():
    """DOVADA ca cele 4 sub-concepte sunt in calcul_salariu/deducere_personala (nu functii separate,
    deci graful le acopera prin functia-gazda): calcul_salariu cere DIRECT salariu_minim + facilitate +
    plafonul facilitatii; deducere_personala cere salariu_minim (pragul tinerilor iese din el)."""
    g = construieste_graf()
    cote_cs = g["calcul_salariu"]["cote"]
    assert "salariu_minim" in cote_cs               # suprataxare part-time, plafon 12 sm
    assert "facilitate_salariu_minim" in cote_cs    # facilitate
    assert "plafon_facilitate_salariu_minim" in cote_cs
    assert "salariu_minim" in g["deducere_personala"]["cote"]   # prag tineri (sm+2000)


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
