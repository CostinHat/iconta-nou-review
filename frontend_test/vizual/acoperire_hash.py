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
    """Numele ecranelor din nav_ecrane.ECRANE, prin regex (fara import de browser).

    [R160, 05.09.2026] Blocul se inchide la un `]` la INCEPUT DE RAND, nu la prima paranteza
    dreapta din text: pana azi cautarea era negreedy si se oprea in comentariul
    `# [LOTUL 12, R142]`, scris deasupra intrarii «emitere» — deci gardul cerea 16 ecrane din
    18, iar ultimele doua adaugate puteau lipsi din artefact fara sa cada nimic.
    Comentariile se scot INAINTE de cautarea numelor, altfel un nume citat intr-un comentariu
    ar intra in lista pe care gardul o cere.

    ANTI-VACUU: daca blocul nu se gaseste sau iese gol, se RIDICA. Un `[]` intors tacut ar
    face gardul sa nu ceara nimic — exact felul de verde despre care nu se poate afla nimic.
    """
    s = open(os.path.join(_HERE, "nav_ecrane.py"), encoding="utf-8").read()
    bloc = re.search(r"^ECRANE\s*=\s*\[(.*?)^\]", s, re.DOTALL | re.MULTILINE)
    if not bloc:
        raise AssertionError("nav_ecrane.py: nu gasesc lista ECRANE (un literal care se "
                             "inchide cu `]` la inceput de rand)")
    fara_comentarii = "\n".join(l.split("#")[0] for l in bloc.group(1).split("\n"))
    nume = re.findall(r'\("([a-z_0-9]+)"', fara_comentarii)
    if not nume:
        raise AssertionError("nav_ecrane.ECRANE e goala — gardul n-ar cere niciun ecran")
    return nume
