# -*- coding: utf-8 -*-
"""scripts/poarta_sare.py — marcajul global de sărire al porții (comanda 15.G, 30.10.2026). Un singur loc care știe ce se sare:
`scripts/poarta.env` (POARTA_SARE), `scripts/poarta_sare.txt` și `scripts/poarta_forma.txt`. Îl citesc conftest.py (pytest) și
frontend_test/e2e/conftest.py (plasa e2e)."""
import fnmatch
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def activ():
    """POARTA_SARE din mediul procesului, altfel din scripts/poarta.env; implicit oprit (fără fișier nu se sare nimic)."""
    v = os.environ.get("POARTA_SARE")
    if v is None:
        try:
            for ln in open(os.path.join(RAD, "scripts", "poarta.env"), encoding="utf-8"):
                if ln.strip().startswith("POARTA_SARE="):
                    v = ln.split("=", 1)[1].strip()
        except OSError:
            pass
    return v == "1"


def tipare():
    out = []
    for f in ("poarta_sare.txt", "poarta_forma.txt"):
        try:
            out += [ln.strip() for ln in open(os.path.join(RAD, "scripts", f), encoding="utf-8") if ln.strip() and not ln.startswith("#")]
        except OSError:
            pass
    return out


def sare_fisier(cale):
    """Calea (absolută sau relativă la rădăcină) e pe lista de sărit, cât marcajul e pornit."""
    if not activ():
        return False
    rel = os.path.relpath(os.path.abspath(cale), RAD)
    return any(fnmatch.fnmatch(rel, t) for t in tipare())


def sare_nod(nodeid):
    """Testele cu „proaspat” în numele nodului, cât marcajul e pornit."""
    return activ() and "proaspat" in nodeid
