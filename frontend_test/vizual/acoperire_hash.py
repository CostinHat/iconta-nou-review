# -*- coding: utf-8 -*-
"""Hash-ul surselor UI + lista ecranelor asteptate. PUR (fara browser/DB) — importat de
interactiune_scan.py (tool) SI de core/test_acoperire_vizuala.py (gard), ca sa nu drifteze."""
import os
import re
import glob
import hashlib

_HERE = os.path.dirname(os.path.abspath(__file__))
RAD = os.path.abspath(os.path.join(_HERE, "..", ".."))
ARTEFACT = os.path.join(_HERE, "acoperire_vizuala.json")


def ui_hash():
    """Hash peste TOATE sursele UI (static/js/**.js + stil.css). Orice schimbare -> hash nou ->
    scanul devine stale -> gardul cere re-scan (over-inclusiv = niciun ecran nu scapa)."""
    fisiere = sorted(
        glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True)
        + [os.path.join(RAD, "static", "stil.css")]
    )
    h = hashlib.sha256()
    for f in fisiere:
        h.update(os.path.relpath(f, RAD).replace(os.sep, "/").encode())
        with open(f, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def ecrane_asteptate():
    """Numele ecranelor din nav_ecrane.ECRANE, prin regex (fara import de browser)."""
    s = open(os.path.join(_HERE, "nav_ecrane.py"), encoding="utf-8").read()
    bloc = re.search(r"ECRANE\s*=\s*\[(.*?)\]", s, re.DOTALL)
    return re.findall(r'\("([a-z_0-9]+)"', bloc.group(1)) if bloc else []
