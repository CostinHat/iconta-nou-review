# -*- coding: utf-8 -*-
"""GARD completitudine golden-XSD: fiecare XSD de declaratie din corpus (anaf_surse/*.xsd +
core/saft.xsd) trebuie sa aiba un generator (core/<mod>.py) SI cel putin un test care il
EXERCITA (importa modulul + genereaza/valideaza). Un generator cu XSD dar fara test = XML
niciodata probat contra structurii oficiale (cazul d402, 19.08: generator complet, zero teste).
Ratchet: un XSD nou nemapate sau fara test -> BLOCHEAZA (ca gardul hartii de ecrane)."""
import os
import re
import glob
import pytest

from core.graf_temei import importuri_core

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# XSD stem (declaratie) -> modul generator in core/. Nemapate = eroare (forteaza inregistrarea).
_HARTA = {
    "d104": "d104", "d110": "d110", "d112": "d112", "d307": "d307", "d311": "d311", "d402": "d402", "saft": "d406",
    "d101g": "d101g",   # [lotul 11, C70] d101g_2024.xsd adus în corpus; generatorul core/d101g.py, probat de test_lot11_d_d101g
}
#: [lotul 13, deficiența 660] XSD-urile formularelor înlocuite de Declarația unică (CF art.120 „Abrogat.” / art.107 alin.(2) / art.125 alin.(4),
#: OUG 128/2024): generatoarele lor au fost șterse, XSD-urile rămân în `anaf_surse/` ca sursă oficială arhivată. Lista e ÎNCHISĂ și numită.
_INLOCUITE_DECLARATIA_UNICA = frozenset(("d220", "d221", "d223"))
_GEN_TOKEN = re.compile(r"build_xml|genereaza|calcul_|XMLSchema|Validator\.jar|\.xsd", re.I)


def _xsd_stems():
    fis = glob.glob(os.path.join(_RAD, "anaf_surse", "*.xsd")) + \
        glob.glob(os.path.join(_RAD, "core", "saft.xsd"))
    out = {}
    for f in fis:
        nume = os.path.splitext(os.path.basename(f))[0]
        stem = re.sub(r"_\d+$", "", nume)  # d402_20160226 -> d402
        out.setdefault(stem, f)
    return out


def test_fiecare_xsd_are_generator_si_test_care_il_exercita():
    lipsa = []
    for stem, xsd in sorted(_xsd_stems().items()):
        if stem in _INLOCUITE_DECLARATIA_UNICA:
            if os.path.exists(os.path.join(_RAD, "core", stem + ".py")):
                lipsa.append("XSD '%s': formular înlocuit de Declarația unică (660), dar generatorul core/%s.py a reapărut" % (stem, stem))
            continue
        mod = _HARTA.get(stem)
        if mod is None:
            lipsa.append("XSD '%s' (%s) nemapate in _HARTA -> inregistreaza modulul generator"
                         % (stem, os.path.basename(xsd)))
            continue
        if not os.path.exists(os.path.join(_RAD, "core", mod + ".py")):
            lipsa.append("XSD '%s': lipseste generatorul core/%s.py" % (stem, mod))
            continue
        # cauta un test care importa modulul SI il exercita (generare/validare)
        gasit = False
        for tf in glob.glob(os.path.join(_RAD, "core", "test_*.py")):
            txt = open(tf, encoding="utf-8").read()
            alias, nume = importuri_core(txt)   # din arborele de sintaxă: și importurile în paranteze
            importa = (mod + ".py") in set(alias.values()) | {m for m, _ in nume.values()}
            if importa and _GEN_TOKEN.search(txt):
                gasit = True
                break
        if not gasit:
            lipsa.append("XSD '%s' (generator core/%s.py) n-are NICIUN test care sa-l genereze/"
                         "valideze -> XML neprobat contra structurii oficiale (cazul d402)" % (stem, mod))
    assert not lipsa, "Goluri golden-XSD:\n  " + "\n  ".join(lipsa)
