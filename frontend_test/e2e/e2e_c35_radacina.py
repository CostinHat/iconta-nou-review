# -*- coding: utf-8 -*-
"""C35 (decizia Costin 15.10.2026, verbatim în DECIZII „Lotul 3 — C35”): gărzile porții judecă arborele COMMITULUI, nu checkout-ul publicat.

Plasa rulează din arborele exportat din index (`scripts/e2e_poarta.py`, un director temporar, alt loc decât checkout-ul publicat) —
exact situația worktree-ului din regimul pilot. Aici se plantează un defect într-un ecran al ACESTUI arbore și se rulează verificatorul
de conformitate din el: dacă își calculează rădăcina din fișierul însuși, numește defectul; dacă ar citi checkout-ul publicat, nu l-ar
vedea. La fel scanul constantelor: rădăcina lui e `core/` al acestui arbore. Fără browser: deficiența e a porții, nu a unui ecran.
Rulează numai în arborele exportat (fără `.git`), ca să nu planteze nimic într-un checkout real."""
import os
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SONDA = os.path.join(RAD, "static", "js", "ecrane", "zz_sonda_c35.js")


@pytest.fixture
def arbore_exportat():
    if os.path.exists(os.path.join(RAD, ".git")):
        pytest.skip("numai în arborele exportat al plasei — nu se plantează nimic într-un checkout git")
    yield RAD


def test_def_c35_garzile_portii_judeca_arborele_commitului(arbore_exportat):
    with open(SONDA, "w", encoding="utf-8") as f:
        f.write('export function zzSondaC35() { alert("sonda C35"); }\n')
    try:
        r = subprocess.run([sys.executable, "verificator_conformitate.py"], cwd=RAD, capture_output=True, text=True, timeout=900)
    finally:
        os.remove(SONDA)
    linii = r.stdout.splitlines()
    total = [int(l.split()[1]) for l in linii if l.startswith("TOTAL: ")]
    numite = [l for l in linii if l.split()[:1] == ["zz_sonda_c35.js"]]
    assert (total, len(numite)) == ([1], 1), (total, numite, r.stdout[-2000:])
    sys.path.insert(0, RAD)
    from core import scan_constante
    assert os.path.dirname(scan_constante.__file__) == scan_constante.RAD == os.path.join(RAD, "core"), scan_constante.RAD
