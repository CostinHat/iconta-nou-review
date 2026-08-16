# -*- coding: utf-8 -*-
"""GARDĂ: infrastructura de testare vizuală (frontend_test/vizual) nu poate dispărea tăcut.
Cele trei unelte (axe / mobil / baseline), sursa axe vandorizată, helperul de navigare și
baseline-urile de referință TREBUIE să existe. Dacă vreuna e ștearsă, suita pică — exact ce
cere Regula 6 (unealta permanentă intră în verificator, nu doar în documentație).

Introdusă 17.08.2026 împreună cu infra vizuală (marca de referință 66f50cd).
Rulează fără DB și fără browser — doar prezența fișierelor.
"""
import os

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIZ = os.path.join(RADACINA, "frontend_test", "vizual")

ECRANE = ["import_mijloace_fixe", "vector_fiscal", "plan_conturi", "stat_plata", "declaratii"]


def test_uneltele_vizuale_exista():
    for f in ["axe_scan.py", "mobil_scan.py", "baseline_scan.py", "nav_ecrane.py"]:
        cale = os.path.join(VIZ, f)
        assert os.path.isfile(cale), "unealtă vizuală lipsă: frontend_test/vizual/%s" % f


def test_axe_vandorizat_prezent():
    axe = os.path.join(VIZ, "axe.min.js")
    assert os.path.isfile(axe), "axe.min.js lipsește — axe-core trebuie vandorizat offline"
    # marker de conținut: nu un fișier gol / placeholder
    with open(axe, encoding="utf-8") as f:
        cap = f.read(400)
    assert "axe" in cap and os.path.getsize(axe) > 100_000, "axe.min.js pare trunchiat/gol"


def test_baseline_de_referinta_exista():
    bdir = os.path.join(VIZ, "baseline")
    assert os.path.isdir(bdir), "lipsește frontend_test/vizual/baseline/"
    for ecran in ECRANE:
        png = os.path.join(bdir, ecran + ".png")
        assert os.path.isfile(png), "baseline lipsă pentru ecranul %s (rulează baseline_scan.py)" % ecran
        assert os.path.getsize(png) > 1000, "baseline %s pare gol/corupt" % ecran


def test_cele_cinci_ecrane_declarate():
    """nav_ecrane.ECRANE = exact cele cinci ecrane problematice numite de Costin, în ordine."""
    with open(os.path.join(VIZ, "nav_ecrane.py"), encoding="utf-8") as f:
        sursa = f.read()
    for ecran in ECRANE:
        assert '"%s"' % ecran in sursa, "ecranul %s nu mai e în nav_ecrane.ECRANE" % ecran
