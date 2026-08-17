# -*- coding: utf-8 -*-
"""core/test_declarant_warn.py — GARD: cand declarantul lipseste din profil, generatoarele AVERTIZEAZA
(nu fabrica TACIT "ADMINISTRATOR"). Aliniere la tiparul d301/d390 (audit tenant_001, thread 3, 17.08.2026).
XML-ul ramane neschimbat (fallback-ul emite tot ADMINISTRATOR - DUK respinge campul gol); doar avertismentul
e nou -> contabilul afla ca declarantul nu e completat, in loc de o declaratie semnata de un "ADMINISTRATOR"
fabricat tacit. Regula 4."""
import io

# (fisier de cod ce emite declarantul) -> avertizeaza cand lipseste. bilant sta in bilant_api.
_DECL = {"d100":"core/d100.py","d101":"core/d101.py","d205":"core/d205.py","d112":"core/d112.py",
         "d300":"core/d300.py","d301":"core/d301.py","d390":"core/d390.py","bilant":"core/bilant_api.py"}


def test_toate_declaratiile_avertizeaza_declarant_lipsa():
    lipsa = []
    for d, path in _DECL.items():
        src = io.open(path, encoding="utf-8").read()
        if not ("declarantul" in src and ("lipseste din profil" in src or "lipsește din profil" in src)):
            lipsa.append(d)
    assert not lipsa, ("declaratii care fabrica TACIT declarantul (fara avertisment cand lipseste): %s" % lipsa)
