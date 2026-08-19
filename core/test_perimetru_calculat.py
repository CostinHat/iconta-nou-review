# -*- coding: utf-8 -*-
"""#11 — §5 CALCULAT (meta-gardul). Din registrul de fatete (MODEL_AUDIT_TENANT.md, F1..F9)
computeaza ce e ACOPERIT mecanic vs. ce ramane pe diligenta: §5 = multimea fatetelor MANUAL,
CALCULATA nu afirmata. Bite: (a) fiecare fateta cere eticheta `**Acoperire:** GARDAT <fisier> |
MANUAL — <motiv>`; (b) orice GARDAT trebuie sa numeasca fisier(e) care EXISTA (enforcement nu
poate disparea tacit — ex. daca cineva sterge test_acoperire_vizuala, F6 pica); (c) §5 (MANUAL)
e pinat la baseline: daca o fateta aluneca din GARDAT in MANUAL (gard pierdut) §5 creste -> pica;
daca gardez una noua (§5 scade) -> pica, ca sa actualizez constient baseline-ul.
Ar fi prins ratatul original 'am sarit DS+mobil': F6/F9 fara gard ar aparea in §5 > baseline."""
import os
import re
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL = os.path.join(_RAD, "MODEL_AUDIT_TENANT.md")

# §5 baseline: fatetele care NU-s inca gardate mecanic (raman pe diligenta + inspectie).
# Actualizeaza CONSTIENT cand gardezi una (scade) sau cand un gard se pierde (creste).
_MANUAL_BASELINE = {"F3", "F4", "F5", "F7"}

# harta fisier-atins -> fateta implicata (pt §5 per-changeset)
_FISIER_FATETA = [
    (re.compile(r"core/(d\d+|[^/]*engine)[^/]*\.py$"), "F2"),
    (re.compile(r"(templates/.*\.html|static/js/.*\.js|stil\.css)$"), "F6"),
    (re.compile(r"core/nav_ecrane\.py$"), "F1"),
    (re.compile(r"(\.sql$|migrat)"), "F3"),
    (re.compile(r"(core/test_.*\.py$|verificator)"), "F8"),
]


def _fatete():
    """{Fx: {'mod': 'GARDAT'|'MANUAL', 'fisiere': [...]}} din MODEL_AUDIT_TENANT.md."""
    txt = open(_MODEL, encoding="utf-8").read()
    blocuri = re.split(r"\n### (F\d) — ", txt)
    out = {}
    for i in range(1, len(blocuri), 2):
        fx, corp = blocuri[i], blocuri[i + 1]
        m = re.search(r"\*\*Acoperire:\*\*\s*(GARDAT|MANUAL)\b(.*)", corp)
        if not m:
            out[fx] = None
            continue
        fisiere = re.findall(r"`((?:core|frontend_test)/[\w/]+\.py)`", m.group(2))
        out[fx] = {"mod": m.group(1), "fisiere": fisiere}
    return out


def sectiunea5_metoda():
    """§5 la nivel de metoda = fatetele cu Acoperire MANUAL (neacoperite mecanic)."""
    return {fx for fx, v in _fatete().items() if v and v["mod"] == "MANUAL"}


def sectiunea5(fisiere_atinse):
    """§5 pt un changeset: fatetele implicate de fisierele atinse care sunt MANUAL (neacoperite)."""
    fat = _fatete()
    implicate = set()
    for f in fisiere_atinse:
        for rx, fx in _FISIER_FATETA:
            if rx.search(f):
                implicate.add(fx)
    return {fx for fx in implicate if fat.get(fx) and fat[fx]["mod"] == "MANUAL"}


def test_fiecare_fateta_are_eticheta_acoperire():
    fat = _fatete()
    for fx in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"):
        assert fat.get(fx), "Fateta %s n-are eticheta **Acoperire:** in MODEL_AUDIT_TENANT.md" % fx


def test_gardat_numeste_fisiere_care_exista():
    lipsa = []
    for fx, v in _fatete().items():
        if v and v["mod"] == "GARDAT":
            if not v["fisiere"]:
                lipsa.append("%s: GARDAT dar nu numeste niciun fisier-garda" % fx)
            for f in v["fisiere"]:
                if not os.path.exists(os.path.join(_RAD, f)):
                    lipsa.append("%s: garda numita %s NU exista (enforcement pierdut)" % (fx, f))
    assert not lipsa, "Fatete GARDAT cu enforcement inexistent:\n  " + "\n  ".join(lipsa)


def test_sectiunea5_calculata_egala_baseline():
    """§5 (fatetele MANUAL) = baseline. Diferenta = o fateta a alunecat (gard pierdut/castigat)."""
    s5 = sectiunea5_metoda()
    alunecat_in_5 = s5 - _MANUAL_BASELINE   # a pierdut gardul -> a intrat in §5
    gardat_nou = _MANUAL_BASELINE - s5      # a castigat gard -> a iesit din §5
    assert not alunecat_in_5, ("Fatete care si-au PIERDUT gardul (enforcement disparut) -> intra in §5: %s. "
                               "Repune garda sau, daca e intentionat, muta in _MANUAL_BASELINE." % sorted(alunecat_in_5))
    assert not gardat_nou, ("Fatete NOU gardate (au iesit din §5): %s. Scoate-le din _MANUAL_BASELINE "
                            "(actualizare constienta a §5)." % sorted(gardat_nou))


def test_sectiunea5_per_changeset_functioneaza():
    """Proba: atingerea unui .sql implica F3 (MANUAL -> in §5); un core/dXXX.py implica F2 (GARDAT -> nu)."""
    assert "F3" in sectiunea5(["migrations/007_x.sql"])          # F3 manual -> apare
    assert sectiunea5(["core/d402.py"]) == set()                 # F2 gardat -> §5 gol
    assert "F6" not in sectiunea5(["static/js/app.js"])          # F6 gardat -> nu apare
