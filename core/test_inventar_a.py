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
    assert m["tva_standard"]["data_out"].startswith("—")   # TVA nu expira


def test_overlay_judecati_umane_pastrat_la_regenerare():
    txt = g.genereaza()
    assert "salariu_minim" in txt and "FISCAL" in txt      # Risc din overlay apare in output
    assert g.OVERLAY.endswith("INVENTAR_A_OVERLAY.tsv")     # overlay = sursa separata, persistenta
    ov = g.overlay()
    assert ov.get("salariu_minim", {}).get("risc") == "FISCAL"
