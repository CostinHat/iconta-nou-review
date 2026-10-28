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


def ecrane_incape():
    """[lotul 14, 687] Numele TUTUROR ecranelor pe care le măsoară `incape_ecran.py` (nav_ecrane.ECRANE + ECRANE_CAMPANIE + ECRANE_CABINET), prin
    regex, fără browser. ECRANE_CAMPANIE se construiește din `_FA_CAMPANIE` (`fa-<nume>`), deci numele vin din acea listă."""
    s = open(os.path.join(_HERE, "nav_ecrane.py"), encoding="utf-8").read()
    out = []
    for lista in ("ECRANE", "ECRANE_CABINET"):
        bloc = re.search(r"^%s\s*=\s*\[(.*?)^\]" % lista, s, re.DOTALL | re.MULTILINE)
        if not bloc:
            raise AssertionError("nav_ecrane.py: nu gasesc lista %s" % lista)
        out += re.findall(r'^\s*\("([a-z_0-9]+)"', "\n".join(l.split("#")[0] for l in bloc.group(1).split("\n")), re.MULTILINE)   # doar începutul rândului: nu și `_card_fn("raportari")`
    camp = re.search(r"^_FA_CAMPANIE\s*=\s*\[(.*?)^\]", s, re.DOTALL | re.MULTILINE)
    if camp:
        out += [x[3:].replace("-", "_") for x in re.findall(r'"(fa-[a-z0-9-]+)"', "\n".join(l.split("#")[0] for l in camp.group(1).split("\n")))]
    if not out:
        raise AssertionError("nicio fereastra de masurat")
    return list(dict.fromkeys(out))
