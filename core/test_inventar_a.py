# -*- coding: utf-8 -*-
"""Inventar A generat PARTIAL din common.COTE + overlay separat pentru judecatile umane.

Proposal point 3 (31.07.2026): structura (cluster/temei/data_out) se GENEREAZA din cod; judecatile
umane (Risc/bifa/PARTIAL) NU au corespondent in cod -> traiesc intr-un overlay persistent care NU
se pierde la regenerare."""
import genereaza_inventar_a as g


def test_structura_derivata_din_cote():
    m = {r["cluster"]: r for r in g.structura()}
    assert "salariu_minim" in m
    assert "HG 146/2026" in m["salariu_minim"]["temei"]
    assert m["salariu_minim"]["data_out"].startswith("2026-12-31")
    assert "ESTIMAT" in m["salariu_minim"]["data_out"]
    assert "tva_standard" in m and "Legea 141/2025" in m["tva_standard"]["temei"]
    assert m["tva_standard"]["data_out"].startswith("2026-12-31")   # ESTIMAT, re-verificare anuala (regula 01.08)
    assert "ESTIMAT" in m["tva_standard"]["data_out"]


def test_overlay_judecati_umane_pastrat_la_regenerare():
    txt = g.genereaza()
    assert "salariu_minim" in txt and "FISCAL" in txt      # Risc din overlay apare in output
    assert g.OVERLAY.endswith("INVENTAR_A_OVERLAY.tsv")     # overlay = sursa separata, persistenta
    ov = g.overlay()
    assert ov.get("salariu_minim", {}).get("risc") == "FISCAL"


def test_inventar_a_vede_algoritmii_cu_temei_la_nivel_de_functie():
    """Deducerea personala si procentele CM sunt ALGORITMI (nu cote in COTE) - au marker TEMEI:
    la nivel de functie (proposal point 2, nu se atomizeaza in cote false). Inventarul A trebuie
    sa le vada, altfel bifele clusterelor de azi stau pe temeiuri care nu sunt in registru."""
    alg = {r["functie"]: r for r in g.algoritmi_cu_temei()}
    assert "deducere_personala" in alg, "deducerea personala nu apare in inventar"
    assert "art.77" in alg["deducere_personala"]["temei"]
    assert "procent_cm" in alg
    assert "158/2005" in alg["procent_cm"]["temei"] and "141/2025" in alg["procent_cm"]["temei"]
    txt = g.genereaza()
    assert "deducere_personala" in txt and "procent_cm" in txt   # apar in artefactul generat
