# -*- coding: utf-8 -*-
"""[Regula 14 + metoda-ca-poarta, cerut de Costin 19.08.2026] GARD: o schimbare de UI cere un scan
vizual+interactiune PROASPAT si CURAT. Cupleaza MECANIC diff-ul de UI de scanul F6+interactiune, ca metoda
sa NU se poata sari (asa cum s-a intamplat: am reparat mesajul dar am sarit DS+mobil+comportament).

- UI schimbat de la ultimul scan (ui_hash difera) -> PICA (ruleaza frontend_test/vizual/interactiune_scan.py);
- scanul a gasit VREO violare pe vreun ecran (axe desktop/mobil, tinte<24 AA, overflow/aliniere la completarea
  casetelor, erori JS la apasarea butoanelor, layout rupt, title-only pe touch, overflow mobil) -> PICA.

Artefact = frontend_test/vizual/acoperire_vizuala.json (produs de interactiune_scan.py cu browser, out-of-band,
ca versioneaza_assets --scrie). ui_hash + ecrane_asteptate din acoperire_hash (PUR, importat si de tool).
"""
import os
import sys
import json
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "frontend_test", "vizual"))
from acoperire_hash import ui_hash, ARTEFACT, ecrane_asteptate  # noqa: E402


def _load():
    if not os.path.exists(ARTEFACT):
        pytest.fail("acoperire_vizuala.json lipseste — ruleaza frontend_test/vizual/interactiune_scan.py")
    return json.load(open(ARTEFACT, encoding="utf-8"))


def test_scan_proaspat():
    """UI-ul nu s-a schimbat de la ultimul scan (altfel scanul e stale — se poate sari un defect nou)."""
    a = _load()
    assert a.get("ui_hash") == ui_hash(), (
        "UI-ul s-a schimbat de la ultimul scan vizual — ruleaza "
        "frontend_test/vizual/interactiune_scan.py inainte de commit (si comite artefactul)")


def test_toate_ecranele_scanate():
    a = _load()
    lipsa = [e for e in ecrane_asteptate() if e not in a.get("ecrane", {})]
    assert not lipsa, "ecrane din nav_ecrane.ECRANE nescanate: %s" % lipsa


def test_fara_violari():
    a = _load()
    probleme = []
    for nume, r in a.get("ecrane", {}).items():
        if r.get("error"):
            probleme.append((nume, "nav", r["error"]))
        if r.get("error_mobil"):
            probleme.append((nume, "nav_mobil", r["error_mobil"]))
        for k in ("axe_desktop", "axe_mobil"):
            if r.get(k):
                probleme.append((nume, k, r[k]))
        ap = r.get("apasare", {})
        if ap.get("console_errors"):
            probleme.append((nume, "erori_consola_la_apasare", ap["console_errors"]))
        if ap.get("layout_rupt_dupa_click"):
            probleme.append((nume, "layout_rupt_dupa_click", True))
        c = r.get("completare", {})
        if c.get("overflow_x"):
            probleme.append((nume, "overflow_x_la_completare", True))
        if c.get("peste_viewport"):
            probleme.append((nume, "elemente_peste_viewport_la_completare", c["peste_viewport"]))
        m = r.get("mobil", {})
        if m.get("tap_sub24"):
            probleme.append((nume, "tap_sub24_AA", m["tap_sub24"]))
        if m.get("overflow_x"):
            probleme.append((nume, "overflow_x_mobil", True))
        if m.get("title_unic"):
            probleme.append((nume, "title_only_pe_touch", m["title_unic"]))
    assert not probleme, "scan vizual/interactiune cu violari (repara + re-scaneaza): %s" % probleme
