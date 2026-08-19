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

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# XSD stem (declaratie) -> modul generator in core/. Nemapate = eroare (forteaza inregistrarea).
_HARTA = {
    "d104": "d104", "d110": "d110", "d112": "d112", "d220": "d220", "d221": "d221",
    "d223": "d223", "d307": "d307", "d311": "d311", "d402": "d402", "saft": "d406",
}
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
            importa = ("from core import %s" % mod) in txt or ("core.%s" % mod) in txt \
                or re.search(r"\bimport %s\b" % re.escape(mod), txt)
            if importa and _GEN_TOKEN.search(txt):
                gasit = True
                break
        if not gasit:
            lipsa.append("XSD '%s' (generator core/%s.py) n-are NICIUN test care sa-l genereze/"
                         "valideze -> XML neprobat contra structurii oficiale (cazul d402)" % (stem, mod))
    assert not lipsa, "Goluri golden-XSD:\n  " + "\n  ".join(lipsa)
