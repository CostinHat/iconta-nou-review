# -*- coding: utf-8 -*-
"""[15.1-E4, pct.4, 736] Orice semnal al cărui text spune „deschide „X”” / „mergi la „X”” are butonul S care deschide X: textele din core/ care numesc un ecran
între ghilimele sunt cele din registrul de mai jos, iar ecranul din registru are butonul pus în firme.js (ACTIUNI_BLOCAJ_ECRAN)."""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: textul serverului care numește un ecran -> codul blocajului și ecranul al cărui buton îl poartă
SEMNALE_CU_ECRAN = {"Reevaluare valută": "REEVALUARE_VALUTA"}


def _texte_server():
    gasite = []
    for f in glob.glob(os.path.join(RAD, "core", "*.py")):
        if os.path.basename(f).startswith("test_"):
            continue
        for i, ln in enumerate(open(f, encoding="utf-8").read().splitlines(), 1):
            if ln.lstrip().startswith("#"):
                continue
            for m in re.finditer(r"(?:deschide|mergi la|intră în)\s+„([^”]{3,40})”", ln, re.I):
                gasite.append((os.path.relpath(f, RAD), i, m.group(1)))
    return gasite


def test_orice_ecran_numit_intr_un_semnal_are_butonul_lui():
    firme = open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    for fisier, linie, ecran in _texte_server():
        if fisier.endswith("uc_auth.py"):
            continue   # „folosește „Am uitat parola”” e textul unei pagini de autentificare, nu un semnal de fereastră
        assert ecran in SEMNALE_CU_ECRAN, f"{fisier}:{linie}: semnalul numește „{ecran}” fără butonul care îl deschide (adaugă-l în ACTIUNI_BLOCAJ_ECRAN și în registrul testului)"
        m = re.search(r"ACTIUNI_BLOCAJ_ECRAN = \{(.*?)\n", firme, re.S)
        assert m and SEMNALE_CU_ECRAN[ecran] in m.group(1) and f'eticheta: "{ecran}"' in m.group(1)
